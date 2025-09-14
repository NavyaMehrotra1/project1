#!/usr/bin/env python3
"""
Company News API Routes
Provides endpoints for fetching latest company news using multi_source_agent
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Any, Optional
import json
import asyncio
from datetime import datetime, timedelta
import sys
from pathlib import Path

# Add data_agent to path
sys.path.append('/Users/sutharsikakumar/project1-1/data_agent')

try:
    from multi_source_agent import MultiSourceDataAgent, NewsItem
    AGENT_AVAILABLE = True
except ImportError:
    AGENT_AVAILABLE = False

router = APIRouter()

# Initialize the agent with NewsAPI key
NEWSAPI_KEY = "1014972b4176494696a58168fcc176fe"  # From the multi_source_agent.py file
agent = None

if AGENT_AVAILABLE:
    agent = MultiSourceDataAgent(newsapi_key=NEWSAPI_KEY)

def load_company_dataset() -> List[str]:
    """Load company names from the graph dataset"""
    try:
        with open('/Users/sutharsikakumar/project1-1/data_agent/data_agent/output/graph_data_for_frontend.json', 'r') as f:
            data = json.load(f)
        
        companies = []
        for node in data.get('nodes', []):
            company_name = node.get('label', '').strip()
            if company_name:
                companies.append(company_name)
        
        return companies
    except Exception as e:
        print(f"Error loading company dataset: {e}")
        return []

def format_news_for_ui(news_items: List[NewsItem]) -> List[Dict[str, Any]]:
    """Format news items for UI consumption"""
    formatted_news = []
    
    for item in news_items:
        # Calculate time ago
        time_diff = datetime.now() - item.published_date.replace(tzinfo=None)
        if time_diff.days > 0:
            time_ago = f"{time_diff.days}d ago"
        elif time_diff.seconds > 3600:
            time_ago = f"{time_diff.seconds // 3600}h ago"
        else:
            time_ago = f"{time_diff.seconds // 60}m ago"
        
        # Determine news category/type
        category = "General"
        if item.deal_type:
            category_map = {
                'acquisition': 'M&A',
                'merger': 'M&A', 
                'investment': 'Funding',
                'partnership': 'Partnership',
                'ipo': 'IPO',
                'exit': 'Exit'
            }
            category = category_map.get(item.deal_type, 'Business')
        
        formatted_item = {
            'id': f"news_{hash(item.url)}",
            'title': item.title,
            'description': item.content,
            'source': item.source,
            'url': item.url,
            'published_date': item.published_date.isoformat(),
            'time_ago': time_ago,
            'companies': item.companies_mentioned,
            'category': category,
            'deal_type': item.deal_type,
            'deal_value': item.deal_value,
            'deal_value_formatted': format_deal_value(item.deal_value) if item.deal_value else None,
            'is_major': item.deal_value and item.deal_value > 100000000,  # $100M+
            'relevance_score': calculate_relevance_score(item)
        }
        formatted_news.append(formatted_item)
    
    # Sort by relevance and recency
    formatted_news.sort(key=lambda x: (x['relevance_score'], x['published_date']), reverse=True)
    
    return formatted_news

def format_deal_value(value: float) -> str:
    """Format deal value for display"""
    if value >= 1e9:
        return f"${value/1e9:.1f}B"
    elif value >= 1e6:
        return f"${value/1e6:.1f}M"
    elif value >= 1e3:
        return f"${value/1e3:.1f}K"
    else:
        return f"${value:.0f}"

def calculate_relevance_score(item: NewsItem) -> float:
    """Calculate relevance score for news item"""
    score = 0.5  # Base score
    
    # Higher score for recent news
    days_old = (datetime.now() - item.published_date.replace(tzinfo=None)).days
    if days_old <= 1:
        score += 0.3
    elif days_old <= 7:
        score += 0.2
    elif days_old <= 30:
        score += 0.1
    
    # Higher score for deal value
    if item.deal_value:
        if item.deal_value >= 1e9:  # $1B+
            score += 0.3
        elif item.deal_value >= 1e8:  # $100M+
            score += 0.2
        elif item.deal_value >= 1e7:  # $10M+
            score += 0.1
    
    # Higher score for important deal types
    if item.deal_type in ['acquisition', 'merger', 'ipo']:
        score += 0.2
    elif item.deal_type in ['investment', 'partnership']:
        score += 0.1
    
    # Higher score for trusted sources
    if item.source in ['Reuters', 'Bloomberg', 'Wall Street Journal', 'TechCrunch', 'Yahoo Finance']:
        score += 0.1
    
    return min(score, 1.0)

@router.get("/company-news")
async def get_company_news(
    companies: Optional[str] = Query(None, description="Comma-separated list of company names"),
    days_back: int = Query(7, description="Number of days to look back for news"),
    limit: int = Query(50, description="Maximum number of news items to return"),
    category: Optional[str] = Query(None, description="Filter by category: M&A, Funding, Partnership, IPO, etc.")
):
    """
    Get latest news for companies in the dataset
    
    Returns formatted news data ready for UI cards
    """
    if not AGENT_AVAILABLE:
        raise HTTPException(status_code=500, detail="Multi-source agent not available")
    
    try:
        # Load companies from dataset or use provided list
        if companies:
            company_list = [c.strip() for c in companies.split(',')]
        else:
            company_list = load_company_dataset()
            # Limit to top companies to avoid rate limits
            company_list = company_list[:20]
        
        if not company_list:
            raise HTTPException(status_code=400, detail="No companies found")
        
        # Collect news from all sources
        news_items = await agent.collect_all_sources(company_list, days_back=days_back)
        
        # Format for UI
        formatted_news = format_news_for_ui(news_items)
        
        # Filter by category if specified
        if category:
            formatted_news = [item for item in formatted_news if item['category'].lower() == category.lower()]
        
        # Apply limit
        formatted_news = formatted_news[:limit]
        
        return {
            'success': True,
            'total_companies_searched': len(company_list),
            'total_news_found': len(formatted_news),
            'days_back': days_back,
            'news': formatted_news
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching company news: {str(e)}")

@router.get("/company-news/summary")
async def get_news_summary():
    """
    Get a summary of recent company news activity
    
    Returns aggregated statistics for dashboard widgets
    """
    if not AGENT_AVAILABLE:
        raise HTTPException(status_code=500, detail="Multi-source agent not available")
    
    try:
        # Load companies and get recent news
        company_list = load_company_dataset()[:15]  # Limit for performance
        news_items = await agent.collect_all_sources(company_list, days_back=7)
        
        # Calculate summary statistics
        total_news = len(news_items)
        
        # Count by category
        category_counts = {}
        deal_values = []
        recent_major_deals = []
        
        for item in news_items:
            # Category counting
            if item.deal_type:
                category = {
                    'acquisition': 'M&A',
                    'merger': 'M&A',
                    'investment': 'Funding',
                    'partnership': 'Partnership',
                    'ipo': 'IPO'
                }.get(item.deal_type, 'Other')
                
                category_counts[category] = category_counts.get(category, 0) + 1
            
            # Deal values
            if item.deal_value:
                deal_values.append(item.deal_value)
                
                # Major deals (>$100M)
                if item.deal_value > 100000000:
                    recent_major_deals.append({
                        'title': item.title,
                        'companies': item.companies_mentioned,
                        'value': format_deal_value(item.deal_value),
                        'type': item.deal_type,
                        'date': item.published_date.isoformat()
                    })
        
        # Calculate total deal value
        total_deal_value = sum(deal_values) if deal_values else 0
        
        return {
            'success': True,
            'summary': {
                'total_news_items': total_news,
                'total_companies_with_news': len(set([comp for item in news_items for comp in item.companies_mentioned])),
                'total_deal_value': total_deal_value,
                'total_deal_value_formatted': format_deal_value(total_deal_value) if total_deal_value else '$0',
                'category_breakdown': category_counts,
                'major_deals_count': len(recent_major_deals),
                'recent_major_deals': recent_major_deals[:5],  # Top 5
                'last_updated': datetime.now().isoformat()
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating news summary: {str(e)}")

@router.get("/company-news/{company_name}")
async def get_single_company_news(
    company_name: str,
    days_back: int = Query(30, description="Number of days to look back"),
    limit: int = Query(10, description="Maximum number of news items")
):
    """
    Get news for a specific company
    
    Returns news data for a single company
    """
    if not AGENT_AVAILABLE:
        raise HTTPException(status_code=500, detail="Multi-source agent not available")
    
    try:
        # Search for specific company
        news_items = await agent.collect_all_sources([company_name], days_back=days_back)
        
        # Format for UI
        formatted_news = format_news_for_ui(news_items)
        formatted_news = formatted_news[:limit]
        
        return {
            'success': True,
            'company': company_name,
            'total_news_found': len(formatted_news),
            'days_back': days_back,
            'news': formatted_news
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching news for {company_name}: {str(e)}")

@router.get("/company-news/categories")
async def get_news_categories():
    """
    Get available news categories for filtering
    """
    return {
        'success': True,
        'categories': [
            {'id': 'ma', 'name': 'M&A', 'description': 'Mergers and Acquisitions'},
            {'id': 'funding', 'name': 'Funding', 'description': 'Investment and Funding Rounds'},
            {'id': 'partnership', 'name': 'Partnership', 'description': 'Strategic Partnerships'},
            {'id': 'ipo', 'name': 'IPO', 'description': 'Initial Public Offerings'},
            {'id': 'exit', 'name': 'Exit', 'description': 'Company Exits and Sales'},
            {'id': 'general', 'name': 'General', 'description': 'General Business News'}
        ]
    }
