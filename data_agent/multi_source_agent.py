"""
Multi-Source AI Data Collection Agent
This agent intelligently searches multiple sources for M&A and business news about companies.
"""

import requests
import json
import time
import re
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import asyncio
import aiohttp
from dataclasses import dataclass
from urllib.parse import quote_plus

@dataclass
class NewsItem:
    """Structure for news items found by the agent"""
    title: str
    content: str
    source: str
    url: str
    published_date: datetime
    companies_mentioned: List[str]
    deal_type: Optional[str] = None
    deal_value: Optional[float] = None

class MultiSourceDataAgent:
    def __init__(self, newsapi_key: Optional[str] = None):
        """
        Initialize the multi-source data agent.
        
        Args:
            newsapi_key: Optional NewsAPI key for enhanced news search
        """
        self.newsapi_key = newsapi_key
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # Enhanced deal type keywords for comprehensive relationship detection
        self.deal_keywords = {
            'acquisition': ['acquire', 'acquisition', 'bought', 'purchase', 'takeover', 'buyout', 'acquires', 'purchasing', 'acquired by'],
            'merger': ['merge', 'merger', 'combining', 'join forces', 'unite', 'merging with', 'merged with'],
            'investment': ['invest', 'investment', 'funding', 'round', 'capital', 'series', 'seed', 'led by', 'participated in', 'backs', 'invests in'],
            'partnership': ['partner', 'partnership', 'collaborate', 'alliance', 'joint venture', 'teams up', 'partners with', 'collaboration'],
            'ipo': ['ipo', 'public offering', 'goes public', 'listing', 'debut', 'public debut', 'stock market'],
            'exit': ['exit', 'sold', 'divest', 'spin off', 'spun off', 'exits'],
            'competition': ['competes with', 'rival', 'competitor', 'competing against', 'vs', 'versus'],
            'integration': ['integrates', 'integration', 'api partnership', 'platform integration', 'connects with'],
            'supplier': ['supplier', 'vendor', 'provides services', 'service provider', 'supplies'],
            'customer': ['customer', 'client', 'uses', 'adopts', 'implements']
        }
        
        print("🤖 Multi-Source AI Data Agent initialized")
        print("📡 Available sources: NewsAPI, Yahoo Finance, Google News, SEC Filings, Social Media")
    
    def extract_deal_info(self, text: str, companies: List[str]) -> Dict[str, Any]:
        """
        Enhanced AI-like pattern matching to extract comprehensive relationship information.
        
        Args:
            text: Text to analyze
            companies: List of company names to look for
            
        Returns:
            Dictionary with extracted deal information and relationships
        """
        text_lower = text.lower()
        
        # Find all mentioned companies in the text
        mentioned_companies = []
        for company in companies:
            if company.lower() in text_lower:
                mentioned_companies.append(company)
        
        # Find deal type with priority scoring
        deal_type = None
        deal_confidence = 0
        for deal, keywords in self.deal_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    # Score based on keyword specificity
                    confidence = len(keyword) / 20.0  # Longer keywords = higher confidence
                    if confidence > deal_confidence:
                        deal_type = deal
                        deal_confidence = confidence
                    break
        
        # Extract deal value using enhanced regex patterns
        deal_value = None
        value_patterns = [
            r'\$(\d+(?:\.\d+)?)\s*billion',
            r'\$(\d+(?:\.\d+)?)\s*b\b',
            r'\$(\d+(?:\.\d+)?)\s*million',
            r'\$(\d+(?:\.\d+)?)\s*m\b',
            r'(\d+(?:\.\d+)?)\s*billion\s*dollars?',
            r'(\d+(?:\.\d+)?)\s*million\s*dollars?',
            r'valued\s+at\s+\$(\d+(?:\.\d+)?)\s*billion',
            r'worth\s+\$(\d+(?:\.\d+)?)\s*billion',
            r'(\d+(?:\.\d+)?)\s*bn',
            r'(\d+(?:\.\d+)?)\s*mil'
        ]
        
        for pattern in value_patterns:
            match = re.search(pattern, text_lower)
            if match:
                value = float(match.group(1))
                if 'billion' in pattern or ' b' in pattern:
                    deal_value = value * 1e9
                elif 'million' in pattern or ' m' in pattern:
                    deal_value = value * 1e6
                break
        
        # Find mentioned companies
        mentioned_companies = []
        for company in companies:
            if company.lower() in text_lower:
                mentioned_companies.append(company)
        
        # Determine source and target companies based on deal type and context
        source_company = None
        target_company = None
        
        if len(mentioned_companies) >= 2:
            # For acquisitions, try to determine acquirer vs acquired
            if deal_type == 'acquisition':
                # Look for patterns like "Company A acquires Company B"
                for i, company in enumerate(mentioned_companies):
                    if any(f"{company.lower()} {keyword}" in text_lower for keyword in ['acquires', 'bought', 'purchased']):
                        source_company = company
                        target_company = mentioned_companies[1-i] if i < 2 else mentioned_companies[0]
                        break
            elif deal_type == 'investment':
                # For investments, investor is source, company is target
                for keyword in ['led by', 'invested by', 'backed by']:
                    if keyword in text_lower:
                        # Find which company is mentioned after the keyword
                        for company in mentioned_companies:
                            if f"{keyword} {company.lower()}" in text_lower:
                                source_company = company
                                target_company = next((c for c in mentioned_companies if c != company), None)
                                break
            
            # Default assignment if no specific pattern found
            if not source_company:
                source_company = mentioned_companies[0]
                target_company = mentioned_companies[1]
        elif len(mentioned_companies) == 1:
            source_company = mentioned_companies[0]
        
        return {
            'companies_mentioned': mentioned_companies,
            'deal_type': deal_type,
            'deal_value': deal_value,
            'source_company': source_company,
            'target_company': target_company,
            'confidence_score': deal_confidence,
            'relationship_strength': len(mentioned_companies) * deal_confidence
        }
    
    async def search_newsapi(self, company_names: List[str], days_back: int = 30) -> List[NewsItem]:
        """
        Search NewsAPI for M&A news about the companies.
        """
        if not self.newsapi_key:
            print("⚠️  NewsAPI key not provided, skipping NewsAPI search")
            return []
        
        print(f"🔍 Searching NewsAPI for M&A news about {len(company_names)} companies...")
        
        news_items = []
        
        # Create comprehensive search queries for different types of relationships
        # Split companies into smaller batches for better API results
        batch_size = 5
        company_batches = [company_names[i:i+batch_size] for i in range(0, len(company_names), batch_size)]
        
        search_queries = []
        for batch in company_batches:
            batch_query = ' OR '.join([f'"{company}"' for company in batch])
            search_queries.extend([
                f"({batch_query}) AND (acquisition OR merger OR acquires OR acquired)",
                f"({batch_query}) AND (investment OR funding OR series OR round OR raised)",
                f"({batch_query}) AND (partnership OR collaboration OR partners with)",
                f"({batch_query}) AND (IPO OR public offering OR goes public)",
                f"({batch_query}) AND (exit OR sold OR divest)",
                f"({batch_query}) AND (competes OR competitor OR rival)",
                f"({batch_query}) AND (integration OR API OR platform)"
            ])
        
        for query in search_queries:
            try:
                url = "https://newsapi.org/v2/everything"
                params = {
                    'q': query,
                    'apiKey': self.newsapi_key,
                    'language': 'en',
                    'sortBy': 'publishedAt',
                    'from': (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d'),
                    'pageSize': 50
                }
                
                response = self.session.get(url, params=params)
                if response.status_code == 200:
                    data = response.json()
                    
                    for article in data.get('articles', []):
                        # Extract deal info
                        text = f"{article.get('title', '')} {article.get('description', '')}"
                        deal_info = self.extract_deal_info(text, company_names)
                        
                        if deal_info['companies_mentioned']:  # Only include if companies are mentioned
                            news_item = NewsItem(
                                title=article.get('title', ''),
                                content=article.get('description', ''),
                                source=article.get('source', {}).get('name', 'NewsAPI'),
                                url=article.get('url', ''),
                                published_date=datetime.fromisoformat(article.get('publishedAt', '').replace('Z', '+00:00')),
                                companies_mentioned=deal_info['companies_mentioned'],
                                deal_type=deal_info['deal_type'],
                                deal_value=deal_info['deal_value']
                            )
                            news_items.append(news_item)
                
                time.sleep(0.1)  # Rate limiting
                
            except Exception as e:
                print(f"❌ Error searching NewsAPI for '{query}': {e}")
        
        print(f"✅ Found {len(news_items)} relevant news items from NewsAPI")
        return news_items
    
    def search_yahoo_finance(self, company_names: List[str]) -> List[NewsItem]:
        """
        Search Yahoo Finance for company news and financial events.
        """
        print(f"📈 Searching Yahoo Finance for news about {len(company_names)} companies...")
        
        news_items = []
        
        for company in company_names[:20]:  # Limit to avoid rate limiting
            try:
                # Yahoo Finance news search
                query = quote_plus(f"{company} merger acquisition funding")
                url = f"https://query1.finance.yahoo.com/v1/finance/search"
                params = {
                    'q': query,
                    'lang': 'en-US',
                    'region': 'US',
                    'quotesCount': 10,
                    'newsCount': 10
                }
                
                response = self.session.get(url, params=params, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    
                    for news in data.get('news', []):
                        # Extract deal info
                        text = f"{news.get('title', '')} {news.get('summary', '')}"
                        deal_info = self.extract_deal_info(text, company_names)
                        
                        if deal_info['companies_mentioned']:
                            news_item = NewsItem(
                                title=news.get('title', ''),
                                content=news.get('summary', ''),
                                source='Yahoo Finance',
                                url=news.get('link', ''),
                                published_date=datetime.fromtimestamp(news.get('providerPublishTime', 0)),
                                companies_mentioned=deal_info['companies_mentioned'],
                                deal_type=deal_info['deal_type'],
                                deal_value=deal_info['deal_value']
                            )
                            news_items.append(news_item)
                
                time.sleep(0.2)  # Rate limiting
                
            except Exception as e:
                print(f"❌ Error searching Yahoo Finance for '{company}': {e}")
        
        print(f"✅ Found {len(news_items)} relevant news items from Yahoo Finance")
        return news_items
    
    def search_google_news(self, company_names: List[str]) -> List[NewsItem]:
        """
        Search Google News using RSS feeds for M&A news.
        """
        print(f"🔍 Searching Google News for M&A information...")
        
        news_items = []
        
        # Google News RSS search terms
        search_terms = [
            "startup merger acquisition",
            "tech company funding",
            "IPO public offering",
            "venture capital investment"
        ]
        
        for term in search_terms:
            try:
                # Google News RSS feed
                query = quote_plus(term)
                url = f"https://news.google.com/rss/search?q={query}&hl=en-US&gl=US&ceid=US:en"
                
                response = self.session.get(url, timeout=10)
                if response.status_code == 200:
                    # Parse RSS (simplified - in production, use feedparser)
                    content = response.text
                    
                    # Extract titles and links using regex (simplified)
                    title_pattern = r'<title><!\[CDATA\[(.*?)\]\]></title>'
                    link_pattern = r'<link>(.*?)</link>'
                    
                    titles = re.findall(title_pattern, content)
                    links = re.findall(link_pattern, content)
                    
                    for title, link in zip(titles[:10], links[:10]):  # Limit results
                        deal_info = self.extract_deal_info(title, company_names)
                        
                        if deal_info['companies_mentioned']:
                            news_item = NewsItem(
                                title=title,
                                content=title,  # Limited content from RSS
                                source='Google News',
                                url=link,
                                published_date=datetime.now(),  # Approximate
                                companies_mentioned=deal_info['companies_mentioned'],
                                deal_type=deal_info['deal_type'],
                                deal_value=deal_info['deal_value']
                            )
                            news_items.append(news_item)
                
                time.sleep(0.3)  # Rate limiting
                
            except Exception as e:
                print(f"❌ Error searching Google News for '{term}': {e}")
        
        print(f"✅ Found {len(news_items)} relevant news items from Google News")
        return news_items
    
    def search_sec_filings(self, company_names: List[str]) -> List[NewsItem]:
        """
        Search SEC EDGAR database for M&A filings and announcements.
        """
        print(f"📋 Searching SEC filings for M&A activities...")
        
        news_items = []
        
        # SEC EDGAR API (simplified search)
        for company in company_names[:10]:  # Limit to avoid overwhelming the API
            try:
                # Search for recent filings
                query = quote_plus(company)
                url = f"https://www.sec.gov/cgi-bin/browse-edgar"
                params = {
                    'action': 'getcompany',
                    'CIK': '',
                    'company': query,
                    'type': '8-K',  # Current reports (often contain M&A news)
                    'dateb': '',
                    'owner': 'exclude',
                    'count': 10,
                    'output': 'atom'
                }
                
                # Note: SEC has strict rate limiting and requires proper headers
                headers = {
                    'User-Agent': 'YourCompany your-email@company.com',
                    'Accept-Encoding': 'gzip, deflate',
                    'Host': 'www.sec.gov'
                }
                
                response = self.session.get(url, params=params, headers=headers, timeout=10)
                if response.status_code == 200:
                    # Parse SEC response (simplified)
                    content = response.text
                    
                    # Look for M&A related filings
                    if any(keyword in content.lower() for keyword in ['merger', 'acquisition', 'agreement']):
                        news_item = NewsItem(
                            title=f"SEC Filing - {company} M&A Activity",
                            content="M&A related SEC filing detected",
                            source='SEC EDGAR',
                            url=f"https://www.sec.gov/edgar/search/#/q={quote_plus(company)}",
                            published_date=datetime.now(),
                            companies_mentioned=[company],
                            deal_type='acquisition',  # Inferred
                            deal_value=None
                        )
                        news_items.append(news_item)
                
                time.sleep(1)  # SEC requires slower rate limiting
                
            except Exception as e:
                print(f"❌ Error searching SEC for '{company}': {e}")
        
        print(f"✅ Found {len(news_items)} relevant SEC filings")
        return news_items
    
    async def collect_all_sources(self, company_names: List[str], days_back: int = 30) -> List[NewsItem]:
        """
        Main method to collect data from all sources.
        
        Args:
            company_names: List of company names to search for
            days_back: How many days back to search
            
        Returns:
            Combined list of news items from all sources
        """
        print(f"🚀 Starting multi-source data collection for {len(company_names)} companies...")
        print(f"📅 Searching {days_back} days back")
        
        all_news = []
        
        # Search NewsAPI (async)
        newsapi_results = await self.search_newsapi(company_names, days_back)
        all_news.extend(newsapi_results)
        
        # Search Yahoo Finance
        yahoo_results = self.search_yahoo_finance(company_names)
        all_news.extend(yahoo_results)
        
        # Search Google News
        google_results = self.search_google_news(company_names)
        all_news.extend(google_results)
        
        # Search SEC filings
        sec_results = self.search_sec_filings(company_names)
        all_news.extend(sec_results)
        
        # Remove duplicates based on title similarity
        unique_news = self._deduplicate_news(all_news)
        
        print(f"✅ Data collection complete!")
        print(f"📊 Total sources searched: 4")
        print(f"📰 Total news items found: {len(all_news)}")
        print(f"🎯 Unique news items after deduplication: {len(unique_news)}")
        
        return unique_news
    
    def _deduplicate_news(self, news_items: List[NewsItem]) -> List[NewsItem]:
        """
        Remove duplicate news items based on title similarity.
        """
        unique_items = []
        seen_titles = set()
        
        for item in news_items:
            # Simple deduplication based on first 50 characters of title
            title_key = item.title[:50].lower().strip()
            if title_key not in seen_titles:
                seen_titles.add(title_key)
                unique_items.append(item)
        
        return unique_items
    
    def format_for_graph(self, news_items: List[NewsItem]) -> List[Dict[str, Any]]:
        """
        Format the collected news data for graph visualization.
        
        Returns:
            List of dictionaries ready for graph creation
        """
        print("📊 Formatting data for graph visualization...")
        
        formatted_deals = []
        
        for item in news_items:
            if len(item.companies_mentioned) >= 2 and item.deal_type:
                # Create deal record
                deal = {
                    'id': f"deal_{len(formatted_deals)}",
                    'source_company': item.companies_mentioned[0],
                    'target_company': item.companies_mentioned[1],
                    'deal_type': item.deal_type,
                    'deal_value': item.deal_value,
                    'deal_date': item.published_date.isoformat(),
                    'description': item.title,
                    'source_url': item.url,
                    'news_source': item.source,
                    'confidence_score': self._calculate_confidence(item)
                }
                formatted_deals.append(deal)
        
        print(f"✅ Formatted {len(formatted_deals)} deals for graph visualization")
        return formatted_deals
    
    def _calculate_confidence(self, news_item: NewsItem) -> float:
        """
        Calculate confidence score for a news item based on various factors.
        """
        confidence = 0.5  # Base confidence
        
        # Higher confidence for official sources
        if news_item.source in ['SEC EDGAR', 'Yahoo Finance']:
            confidence += 0.3
        
        # Higher confidence if deal value is mentioned
        if news_item.deal_value:
            confidence += 0.2
        
        # Higher confidence for specific deal types
        if news_item.deal_type in ['acquisition', 'merger', 'ipo']:
            confidence += 0.1
        
        return min(confidence, 1.0)

# Example usage function
async def main():
    """
    Example of how to use the Multi-Source Data Agent
    """
    # Initialize agent (add your NewsAPI key if available)
    agent = MultiSourceDataAgent(newsapi_key= "1014972b4176494696a58168fcc176fe")  # Add your key here
    
    # Example company names (subset for testing)
    test_companies = [
        "Stripe", "OpenAI", "Anthropic", "Airbnb", "Coinbase",
        "DoorDash", "Instacart", "Brex", "Scale AI", "Zapier"
    ]
    
    # Collect data from all sources
    news_items = await agent.collect_all_sources(test_companies, days_back=30)
    
    # Format for graph
    graph_data = agent.format_for_graph(news_items)
    
    # Save results
    with open('data_agent/collected_deals.json', 'w') as f:
        json.dump(graph_data, f, indent=2, default=str)
    
    print(f"\n🎉 Data collection complete! Found {len(graph_data)} deals ready for visualization.")

if __name__ == "__main__":
    asyncio.run(main())
