import asyncio
import aiohttp
import yfinance as yf
from newsapi import NewsApiClient
import pandas as pd
from datetime import datetime, timedelta
import requests
from typing import List, Dict, Any, Optional
import json
import os
import csv
from models.schemas import Company, Deal, NewsData, DealType, CompanyProfile
import pandas as pd
import random
import uuid

class DataIngestionService:
    def __init__(self):
        self.newsapi_key = os.getenv("NEWSAPI_KEY")
        self.newsapi = NewsApiClient(api_key=self.newsapi_key) if self.newsapi_key else None
        
        # In-memory storage for demo (replace with database in production)
        self.companies_db = {}
        self.deals_db = {}
        
        # Initialize with some sample data
        self._initialize_sample_data()
    
    def _initialize_sample_data(self):
        """Initialize with sample companies and deals for demo"""
        sample_companies = [
            {
                "id": "openai",
                "name": "OpenAI",
                "industry": "Artificial Intelligence",
                "market_cap": 80000000000,
                "founded_year": 2015,
                "headquarters": "San Francisco, CA",
                "description": "AI research and deployment company",
                "is_public": False,
                "extraordinary_score": 0.95
            },
            {
                "id": "microsoft",
                "name": "Microsoft Corporation",
                "industry": "Technology",
                "market_cap": 2800000000000,
                "founded_year": 1975,
                "headquarters": "Redmond, WA",
                "ticker_symbol": "MSFT",
                "is_public": True,
                "extraordinary_score": 0.85
            },
            {
                "id": "google",
                "name": "Alphabet Inc.",
                "industry": "Technology",
                "market_cap": 1700000000000,
                "founded_year": 1998,
                "headquarters": "Mountain View, CA",
                "ticker_symbol": "GOOGL",
                "is_public": True,
                "extraordinary_score": 0.88
            },
            {
                "id": "meta",
                "name": "Meta Platforms",
                "industry": "Social Media",
                "market_cap": 800000000000,
                "founded_year": 2004,
                "headquarters": "Menlo Park, CA",
                "ticker_symbol": "META",
                "is_public": True,
                "extraordinary_score": 0.82
            },
            {
                "id": "anthropic",
                "name": "Anthropic",
                "industry": "Artificial Intelligence",
                "market_cap": 15000000000,
                "founded_year": 2021,
                "headquarters": "San Francisco, CA",
                "description": "AI safety company",
                "is_public": False,
                "extraordinary_score": 0.92
            }
        ]
        
        for company_data in sample_companies:
            company = Company(**company_data)
            self.companies_db[company.id] = company
        
        # Sample deals
        sample_deals = [
            {
                "id": "deal_1",
                "source_company_id": "microsoft",
                "target_company_id": "openai",
                "deal_type": DealType.INVESTMENT,
                "deal_value": 10000000000,
                "deal_date": datetime(2023, 1, 23),
                "description": "Microsoft invests $10B in OpenAI partnership",
                "status": "completed",
                "confidence_score": 1.0,
                "is_predicted": False
            },
            {
                "id": "deal_2",
                "source_company_id": "google",
                "target_company_id": "anthropic",
                "deal_type": DealType.INVESTMENT,
                "deal_value": 300000000,
                "deal_date": datetime(2022, 5, 15),
                "description": "Google invests $300M in Anthropic",
                "status": "completed",
                "confidence_score": 1.0,
                "is_predicted": False
            }
        ]
        
        for deal_data in sample_deals:
            deal = Deal(**deal_data)
            self.deals_db[deal.id] = deal

    async def fetch_news(self, query: str, days_back: int = 30) -> List[NewsData]:
        """Fetch M&A news from various sources"""
        news_data = []
        
        # NewsAPI integration
        if self.newsapi:
            try:
                from_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
                
                articles = self.newsapi.get_everything(
                    q=query,
                    from_param=from_date,
                    language='en',
                    sort_by='relevancy',
                    page_size=50
                )
                
                for article in articles.get('articles', []):
                    news_item = NewsData(
                        title=article['title'],
                        content=article['description'] or "",
                        source=article['source']['name'],
                        published_date=datetime.fromisoformat(article['publishedAt'].replace('Z', '+00:00')),
                        url=article['url'],
                        companies_mentioned=self._extract_companies_from_text(article['title'] + " " + (article['description'] or ""))
                    )
                    news_data.append(news_item)
            except Exception as e:
                print(f"NewsAPI error: {e}")
        
        # Add some mock news data for demo
        mock_news = [
            NewsData(
                title="Epic Games and Sony Announce Strategic Partnership",
                content="Epic Games and Sony have announced a new strategic partnership to develop next-generation gaming experiences.",
                source="TechCrunch",
                published_date=datetime.now() - timedelta(days=5),
                url="https://techcrunch.com/mock-article",
                companies_mentioned=["Epic Games", "Sony"]
            ),
            NewsData(
                title="Salesforce Acquires AI Startup for $2.1B",
                content="Salesforce has completed the acquisition of an AI startup specializing in customer analytics.",
                source="Reuters",
                published_date=datetime.now() - timedelta(days=10),
                url="https://reuters.com/mock-article",
                companies_mentioned=["Salesforce"]
            )
        ]
        
        news_data.extend(mock_news)
        return news_data

    def _extract_companies_from_text(self, text: str) -> List[str]:
        """Extract company names from text using simple pattern matching"""
        # This is a simplified version - in production, use NER models
        known_companies = list(self.companies_db.keys())
        mentioned = []
        
        for company_id in known_companies:
            company_name = self.companies_db[company_id].name
            if company_name.lower() in text.lower():
                mentioned.append(company_name)
        
        return mentioned

    async def process_news_to_deals(self, news_data: List[NewsData]) -> List[Deal]:
        """Process news articles to extract potential deals"""
        deals = []
        
        for news in news_data:
            # Simple keyword-based deal extraction
            text = (news.title + " " + news.content).lower()
            
            deal_type = None
            if any(word in text for word in ["acquire", "acquisition", "buys", "purchased"]):
                deal_type = DealType.ACQUISITION
            elif any(word in text for word in ["merge", "merger"]):
                deal_type = DealType.MERGER
            elif any(word in text for word in ["partner", "partnership", "collaborate"]):
                deal_type = DealType.PARTNERSHIP
            elif any(word in text for word in ["invest", "investment", "funding", "round"]):
                deal_type = DealType.INVESTMENT
            
            if deal_type and len(news.companies_mentioned) >= 2:
                deal_id = f"extracted_{len(deals)}"
                deal = Deal(
                    id=deal_id,
                    source_company_id=news.companies_mentioned[0].lower().replace(" ", "_"),
                    target_company_id=news.companies_mentioned[1].lower().replace(" ", "_"),
                    deal_type=deal_type,
                    deal_date=news.published_date,
                    description=news.title,
                    status="rumored",
                    confidence_score=0.7,
                    is_predicted=False
                )
                deals.append(deal)
                self.deals_db[deal.id] = deal
        
        return deals

    async def get_companies(self) -> List[Company]:
        """Get all companies"""
        return list(self.companies_db.values())

    async def get_deals(self) -> List[Deal]:
        """Get all deals"""
        return list(self.deals_db.values())

    async def get_company_profile(self, company_name: str) -> Dict[str, Any]:
        """Get detailed company profile"""
        company_id = company_name.lower().replace(" ", "_")
        
        if company_id not in self.companies_db:
            # Try to find by name
            for cid, company in self.companies_db.items():
                if company.name.lower() == company_name.lower():
                    company_id = cid
                    break
        
        if company_id not in self.companies_db:
            raise ValueError(f"Company {company_name} not found")
        
        company = self.companies_db[company_id]
        
        # Get related deals
        related_deals = [
            deal for deal in self.deals_db.values()
            if deal.source_company_id == company_id or deal.target_company_id == company_id
        ]
        
        # Mock financial data
        financial_metrics = {
            "revenue_growth": 0.15,
            "profit_margin": 0.25,
            "debt_to_equity": 0.3,
            "current_ratio": 2.1
        }
        
        return {
            "company": company,
            "connections": related_deals,
            "financial_metrics": financial_metrics,
            "news_sentiment": 0.75,
            "extraordinary_factors": ["AI Leadership", "Market Innovation", "Strong Partnerships"] if company.extraordinary_score and company.extraordinary_score > 0.8 else []
        }

    async def fetch_company_financials(self, ticker: str) -> Dict[str, Any]:
        """Fetch company financial data using yfinance"""
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            return {
                "market_cap": info.get("marketCap"),
                "revenue": info.get("totalRevenue"),
                "profit_margin": info.get("profitMargins"),
                "pe_ratio": info.get("trailingPE"),
                "debt_to_equity": info.get("debtToEquity"),
                "current_ratio": info.get("currentRatio")
            }
        except Exception as e:
            print(f"Error fetching financials for {ticker}: {e}")
            return {}

    def add_company(self, company: Company):
        """Add a new company to the database"""
        self.companies_db[company.id] = company

    def add_deal(self, deal: Deal):
        """Add a new deal to the database"""
        self.deals_db[deal.id] = deal
