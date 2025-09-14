#!/usr/bin/env python3
"""
Real-time Data Agent
Fetches company information from Reddit and other free APIs every minute
Updates ChromaDB vector database with new information
"""

import asyncio
import json
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import requests
from dataclasses import dataclass
import chromadb
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class CompanyUpdate:
    """Data structure for company updates"""
    company_name: str
    source: str
    content: str
    timestamp: datetime
    update_type: str  # 'deal', 'competition', 'news', 'funding'
    confidence: float
    url: Optional[str] = None

class RealTimeDataAgent:
    def __init__(self, chromadb_path: str = "./chroma_db"):
        self.chromadb_path = chromadb_path
        self.client = chromadb.PersistentClient(path=chromadb_path)
        self.updates_log = []
        self.company_names = self._load_company_names()
        
        # Initialize collections
        try:
            self.companies_collection = self.client.get_collection("yc_companies")
        except:
            self.companies_collection = self.client.create_collection("yc_companies")
            
        try:
            self.updates_collection = self.client.get_collection("company_updates")
        except:
            self.updates_collection = self.client.create_collection("company_updates")
    
    def _load_company_names(self) -> List[str]:
        """Load company names from graph data"""
        try:
            with open('../data_agent/data_agent/output/graph_data_for_frontend.json', 'r') as f:
                graph_data = json.load(f)
            return [node['label'] for node in graph_data['nodes']]
        except Exception as e:
            logger.error(f"Failed to load company names: {e}")
            return []
    
    def fetch_reddit_data(self, company_name: str) -> List[CompanyUpdate]:
        """Fetch company mentions from Reddit using free API"""
        updates = []
        try:
            # Use Reddit's JSON API (no auth required for public posts)
            search_terms = [
                f"{company_name} funding",
                f"{company_name} deal",
                f"{company_name} acquisition",
                f"{company_name} partnership"
            ]
            
            for term in search_terms:
                url = f"https://www.reddit.com/search.json?q={term}&sort=new&limit=10&t=week"
                headers = {'User-Agent': 'CompanyDataAgent/1.0 (Educational Research)'}
                
                response = requests.get(url, headers=headers, timeout=15)
                if response.status_code == 200:
                    data = response.json()
                    
                    for post in data.get('data', {}).get('children', []):
                        post_data = post['data']
                        
                        # Get post details
                        title = post_data.get('title', '')
                        selftext = post_data.get('selftext', '')
                        permalink = post_data.get('permalink', '')
                        created_utc = post_data.get('created_utc', 0)
                        score = post_data.get('score', 0)
                        
                        # Skip if no permalink or too old (older than 7 days)
                        if not permalink or (time.time() - created_utc) > 604800:
                            continue
                            
                        # Filter for relevant posts with strict criteria
                        title_lower = title.lower()
                        selftext_lower = selftext.lower()
                        company_lower = company_name.lower()
                        
                        # Must mention company name and relevant keywords
                        has_company = company_lower in title_lower or company_lower in selftext_lower
                        has_keywords = any(keyword in title_lower or keyword in selftext_lower 
                                         for keyword in ['funding', 'raised', 'investment', 'deal', 'acquisition', 'partnership', 'series'])
                        
                        # Must have minimum engagement (score > 5)
                        has_engagement = score > 5
                        
                        if has_company and has_keywords and has_engagement:
                            update_type = self._classify_update_type(title + " " + selftext)
                            confidence = self._calculate_confidence(title, selftext, company_name)
                            
                            # Higher confidence threshold for real data
                            if confidence > 0.6:
                                # Construct full Reddit URL
                                reddit_url = f"https://reddit.com{permalink}"
                                
                                # Verify URL is accessible
                                try:
                                    url_check = requests.head(reddit_url, timeout=5)
                                    if url_check.status_code == 200:
                                        update = CompanyUpdate(
                                            company_name=company_name,
                                            source="Reddit",
                                            content=f"{title} - {selftext[:200]}",
                                            timestamp=datetime.fromtimestamp(created_utc),
                                            update_type=update_type,
                                            confidence=confidence,
                                            url=reddit_url
                                        )
                                        updates.append(update)
                                        logger.info(f"✅ Found valid Reddit update for {company_name}: {title[:50]}...")
                                except:
                                    continue  # Skip if URL not accessible
                
                # Rate limiting to respect Reddit's API
                time.sleep(2)
                
        except Exception as e:
            logger.error(f"Error fetching Reddit data for {company_name}: {e}")
        
        return updates
    
    def fetch_hackernews_data(self, company_name: str) -> List[CompanyUpdate]:
        """Fetch company mentions from Hacker News API"""
        updates = []
        try:
            # Search Hacker News API with more specific query
            search_url = f"https://hn.algolia.com/api/v1/search?query={company_name} funding OR {company_name} acquisition OR {company_name} deal&tags=story&hitsPerPage=10"
            response = requests.get(search_url, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                
                for hit in data.get('hits', []):
                    title = hit.get('title', '')
                    url = hit.get('url', '')
                    created_at = hit.get('created_at', '')
                    points = hit.get('points', 0)
                    
                    # Skip if no URL or too old (older than 30 days)
                    if not url or not created_at:
                        continue
                        
                    try:
                        created_time = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                        if (datetime.now().replace(tzinfo=created_time.tzinfo) - created_time).days > 30:
                            continue
                    except:
                        continue
                    
                    # Filter for relevant posts with strict criteria
                    title_lower = title.lower()
                    company_lower = company_name.lower()
                    
                    # Must mention company name and relevant keywords
                    has_company = company_lower in title_lower
                    has_keywords = any(keyword in title_lower for keyword in ['funding', 'raised', 'investment', 'deal', 'acquisition', 'partnership', 'series', 'round'])
                    
                    # Must have minimum engagement (points > 10)
                    has_engagement = points > 10
                    
                    if has_company and has_keywords and has_engagement:
                        update_type = self._classify_update_type(title)
                        confidence = self._calculate_confidence(title, "", company_name)
                        
                        # Higher confidence threshold for real data
                        if confidence > 0.6:
                            # Verify URL is accessible
                            try:
                                url_check = requests.head(url, timeout=5)
                                if url_check.status_code == 200:
                                    update = CompanyUpdate(
                                        company_name=company_name,
                                        source="Hacker News",
                                        content=title,
                                        timestamp=created_time.replace(tzinfo=None),
                                        update_type=update_type,
                                        confidence=confidence,
                                        url=url
                                    )
                                    updates.append(update)
                                    logger.info(f"✅ Found valid Hacker News update for {company_name}: {title[:50]}...")
                            except:
                                continue  # Skip if URL not accessible
            
        except Exception as e:
            logger.error(f"Error fetching Hacker News data for {company_name}: {e}")
        
        return updates
    
    def _classify_update_type(self, text: str) -> str:
        """Classify the type of update based on content"""
        text = text.lower()
        
        if any(word in text for word in ['funding', 'raised', 'investment', 'round']):
            return 'funding'
        elif any(word in text for word in ['acquisition', 'acquired', 'bought', 'merger']):
            return 'deal'
        elif any(word in text for word in ['partnership', 'partner', 'collaboration']):
            return 'partnership'
        elif any(word in text for word in ['competition', 'competitor', 'rival']):
            return 'competition'
        else:
            return 'news'
    
    def _calculate_confidence(self, title: str, content: str, company_name: str) -> float:
        """Calculate confidence score for the update relevance"""
        text = (title + " " + content).lower()
        company_lower = company_name.lower()
        
        confidence = 0.0
        
        # Exact company name match
        if company_lower in text:
            confidence += 0.5
        
        # Relevant keywords
        keywords = ['funding', 'deal', 'acquisition', 'partnership', 'competition', 'startup']
        for keyword in keywords:
            if keyword in text:
                confidence += 0.1
        
        # Business context
        business_terms = ['million', 'billion', 'series', 'round', 'investment', 'vc']
        for term in business_terms:
            if term in text:
                confidence += 0.05
        
        return min(confidence, 1.0)
    
    def add_update_to_vector_db(self, update: CompanyUpdate):
        """Add new update to ChromaDB vector database"""
        try:
            # Create document text
            doc_text = f"""
            Company: {update.company_name}
            Update Type: {update.update_type}
            Source: {update.source}
            Content: {update.content}
            Timestamp: {update.timestamp.isoformat()}
            Confidence: {update.confidence:.2f}
            """
            
            # Generate unique ID
            update_id = f"{update.company_name}_{update.source}_{int(update.timestamp.timestamp())}"
            
            # Add to updates collection
            self.updates_collection.upsert(
                documents=[doc_text.strip()],
                metadatas=[{
                    'company_name': update.company_name,
                    'source': update.source,
                    'update_type': update.update_type,
                    'timestamp': update.timestamp.isoformat(),
                    'confidence': update.confidence,
                    'url': update.url or ''
                }],
                ids=[update_id]
            )
            
            # Log the update
            self.updates_log.append({
                'timestamp': update.timestamp.isoformat(),
                'company': update.company_name,
                'type': update.update_type,
                'source': update.source,
                'confidence': update.confidence,
                'content': update.content[:100] + "..." if len(update.content) > 100 else update.content
            })
            
            logger.info(f"✅ Added update for {update.company_name}: {update.update_type} from {update.source}")
            
        except Exception as e:
            logger.error(f"Error adding update to vector DB: {e}")
    
    def get_recent_updates(self, limit: int = 10) -> List[Dict]:
        """Get recent updates from the log"""
        return self.updates_log[-limit:]
    
    def search_updates(self, query: str, limit: int = 5) -> List[Dict]:
        """Search for updates in the vector database"""
        try:
            results = self.updates_collection.query(
                query_texts=[query],
                n_results=limit
            )
            
            search_results = []
            for doc, metadata in zip(results['documents'][0], results['metadatas'][0]):
                search_results.append({
                    'company': metadata['company_name'],
                    'type': metadata['update_type'],
                    'source': metadata['source'],
                    'timestamp': metadata['timestamp'],
                    'confidence': metadata['confidence'],
                    'content': doc,
                    'url': metadata.get('url', '')
                })
            
            return search_results
            
        except Exception as e:
            logger.error(f"Error searching updates: {e}")
            return []
    
    async def run_continuous_monitoring(self):
        """Run continuous monitoring every minute"""
        logger.info("🚀 Starting real-time company data monitoring...")
        
        while True:
            try:
                start_time = time.time()
                updates_found = 0
                
                # Sample a few companies each cycle to avoid rate limits
                import random
                sample_companies = random.sample(self.company_names, min(3, len(self.company_names)))
                
                logger.info(f"🔍 Checking {len(sample_companies)} companies for updates...")
                
                for company in sample_companies:
                    logger.info(f"   Searching for {company}...")
                    
                    # Fetch from multiple sources
                    reddit_updates = self.fetch_reddit_data(company)
                    hn_updates = self.fetch_hackernews_data(company)
                    
                    all_updates = reddit_updates + hn_updates
                    
                    if all_updates:
                        for update in all_updates:
                            self.add_update_to_vector_db(update)
                            updates_found += 1
                        logger.info(f"   ✅ Found {len(all_updates)} valid updates for {company}")
                    else:
                        logger.info(f"   ❌ No valid updates found for {company}")
                    
                    # Rate limiting between companies
                    await asyncio.sleep(3)
                
                elapsed_time = time.time() - start_time
                
                if updates_found > 0:
                    logger.info(f"📊 Cycle complete: {updates_found} valid updates added to vector DB in {elapsed_time:.1f}s")
                else:
                    logger.info(f"📊 Cycle complete: No valid updates found this cycle ({elapsed_time:.1f}s)")
                
                # Wait for next minute (minimum 60 seconds between cycles)
                wait_time = max(60 - elapsed_time, 10)
                logger.info(f"⏰ Waiting {wait_time:.1f}s until next cycle...")
                await asyncio.sleep(wait_time)
                
            except KeyboardInterrupt:
                logger.info("🛑 Monitoring stopped by user")
                break
            except Exception as e:
                logger.error(f"Error in monitoring cycle: {e}")
                await asyncio.sleep(60)

def main():
    """Main function to run the agent"""
    agent = RealTimeDataAgent()
    
    try:
        asyncio.run(agent.run_continuous_monitoring())
    except KeyboardInterrupt:
        print("\n👋 Real-time monitoring stopped")

if __name__ == "__main__":
    main()
