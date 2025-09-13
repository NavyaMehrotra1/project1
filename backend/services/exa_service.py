import os
import asyncio
from typing import List, Dict, Optional
import aiohttp
import json
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class ExaService:
    def __init__(self):
        self.api_key = os.getenv('EXA_API_KEY')
        self.base_url = "https://api.exa.ai"
        self.session = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def search_company(
        self, 
        company_name: str, 
        num_results: int = 10,
        include_domains: List[str] = None
    ) -> Dict:
        """Search for company information using Exa API"""
        if not self.api_key:
            logger.error("EXA_API_KEY not found in environment variables")
            return {"error": "API key not configured"}
            
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Enhanced search query for better company results
        query = f"{company_name} company startup funding news recent"
        
        payload = {
            "query": query,
            "type": "neural",
            "useAutoprompt": True,
            "numResults": num_results,
            "contents": {
                "text": True,
                "highlights": True,
                "summary": True
            },
            "category": "company",
            "startPublishedDate": (datetime.now() - timedelta(days=365)).isoformat(),
        }
        
        if include_domains:
            payload["includeDomains"] = include_domains
            
        try:
            async with self.session.post(
                f"{self.base_url}/search",
                headers=headers,
                json=payload
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return await self._process_company_data(company_name, data)
                else:
                    error_text = await response.text()
                    logger.error(f"Exa API error: {response.status} - {error_text}")
                    return {"error": f"API request failed: {response.status}"}
                    
        except Exception as e:
            logger.error(f"Error calling Exa API: {str(e)}")
            return {"error": str(e)}
    
    async def _process_company_data(self, company_name: str, exa_data: Dict) -> Dict:
        """Process and structure the Exa API response"""
        results = exa_data.get("results", [])
        
        if not results:
            return {
                "company_name": company_name,
                "exa_data": {
                    "summary": "No recent information found",
                    "news_articles": [],
                    "key_highlights": [],
                    "funding_info": {},
                    "recent_activity": []
                }
            }
        
        # Extract key information
        news_articles = []
        key_highlights = []
        funding_mentions = []
        
        for result in results[:10]:  # Limit to top 10 results
            article = {
                "title": result.get("title", ""),
                "url": result.get("url", ""),
                "published_date": result.get("publishedDate", ""),
                "summary": result.get("summary", ""),
                "highlights": result.get("highlights", [])
            }
            news_articles.append(article)
            
            # Extract highlights for key insights
            if result.get("highlights"):
                key_highlights.extend(result["highlights"][:3])  # Top 3 highlights per article
            
            # Look for funding-related content
            text = result.get("text", "").lower()
            summary = result.get("summary", "").lower()
            
            funding_keywords = ["funding", "raised", "investment", "series", "round", "valuation", "investor"]
            if any(keyword in text or keyword in summary for keyword in funding_keywords):
                funding_mentions.append({
                    "source": result.get("title", ""),
                    "url": result.get("url", ""),
                    "excerpt": result.get("summary", "")[:200] + "..."
                })
        
        # Generate overall summary
        overall_summary = self._generate_company_summary(company_name, results)
        
        return {
            "company_name": company_name,
            "exa_data": {
                "summary": overall_summary,
                "news_articles": news_articles,
                "key_highlights": key_highlights[:10],  # Top 10 highlights
                "funding_info": {
                    "mentions": funding_mentions[:5],  # Top 5 funding mentions
                    "has_recent_funding": len(funding_mentions) > 0
                },
                "recent_activity": [
                    {
                        "type": "news",
                        "count": len(news_articles),
                        "latest_date": results[0].get("publishedDate", "") if results else ""
                    }
                ],
                "last_updated": datetime.now().isoformat(),
                "data_quality": "high" if len(results) >= 5 else "medium" if len(results) >= 2 else "low"
            }
        }
    
    def _generate_company_summary(self, company_name: str, results: List[Dict]) -> str:
        """Generate a concise summary of the company based on Exa results"""
        if not results:
            return f"Limited information available for {company_name}"
        
        # Use the first result's summary as base, or create from highlights
        primary_summary = results[0].get("summary", "")
        if primary_summary and len(primary_summary) > 50:
            return primary_summary[:300] + "..." if len(primary_summary) > 300 else primary_summary
        
        # Fallback: combine highlights
        all_highlights = []
        for result in results[:3]:  # Use top 3 results
            if result.get("highlights"):
                all_highlights.extend(result["highlights"][:2])
        
        if all_highlights:
            combined = " ".join(all_highlights[:3])  # Top 3 highlights
            return combined[:300] + "..." if len(combined) > 300 else combined
        
        return f"Recent activity and news coverage found for {company_name}"

    async def enrich_company_batch(self, companies: List[str]) -> Dict[str, Dict]:
        """Enrich multiple companies with Exa data"""
        results = {}
        
        # Process in batches to avoid rate limiting
        batch_size = 5
        for i in range(0, len(companies), batch_size):
            batch = companies[i:i + batch_size]
            batch_tasks = [self.search_company(company) for company in batch]
            
            batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
            
            for company, result in zip(batch, batch_results):
                if isinstance(result, Exception):
                    logger.error(f"Error processing {company}: {result}")
                    results[company] = {"error": str(result)}
                else:
                    results[company] = result
            
            # Rate limiting delay
            await asyncio.sleep(1)
        
        return results

# Utility functions for integration
async def get_enhanced_company_data(company_name: str) -> Dict:
    """Get enhanced company data using Exa API"""
    async with ExaService() as exa:
        return await exa.search_company(company_name)

async def enrich_yc_companies(yc_companies: List[str]) -> Dict:
    """Enrich YC company list with Exa data"""
    async with ExaService() as exa:
        return await exa.enrich_company_batch(yc_companies)
