import os
import asyncio
import json
import re
from typing import List, Dict, Optional, Tuple
import aiohttp
from datetime import datetime, timedelta
import logging
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

@dataclass
class ExtraordinaryMetrics:
    """Metrics used to calculate extraordinary score"""
    valuation: float = 0.0
    funding_raised: float = 0.0
    employee_count: int = 0
    revenue: float = 0.0
    growth_rate: float = 0.0
    market_share: float = 0.0
    awards_count: int = 0
    media_mentions: int = 0
    patent_count: int = 0
    unicorn_status: bool = False
    ipo_status: bool = False
    acquisition_count: int = 0
    notable_investors: int = 0
    years_in_business: int = 0
    innovation_score: float = 0.0

@dataclass
class ExtraordinaryProfile:
    """Complete extraordinary profile for a company/person"""
    name: str
    type: str  # 'company' or 'person'
    extraordinary_score: float
    metrics: ExtraordinaryMetrics
    notable_achievements: List[str]
    awards_recognitions: List[Dict]
    media_coverage: List[Dict]
    key_stats: Dict[str, any]
    innovation_highlights: List[str]
    competitive_advantages: List[str]
    leadership_team: List[Dict]
    funding_history: List[Dict]
    created_at: datetime

class ExtraordinaryResearchService:
    def __init__(self):
        self.exa_api_key = os.getenv('EXA_API_KEY')
        self.session = None
        
        # Data sources for comprehensive research
        self.data_sources = {
            'exa': 'https://api.exa.ai',
            'crunchbase_proxy': 'https://api.crunchbase.com/v4',  # Would need API key
            'pitchbook_proxy': 'https://api.pitchbook.com',       # Would need API key
            'bloomberg_proxy': 'https://api.bloomberg.com',       # Would need API key
        }
        
        # Extraordinary score weights
        self.score_weights = {
            'valuation': 0.20,      # 20% - Company valuation
            'funding': 0.15,        # 15% - Total funding raised
            'growth': 0.15,         # 15% - Growth metrics
            'innovation': 0.15,     # 15% - Innovation/patents
            'market_position': 0.10, # 10% - Market share/dominance
            'recognition': 0.10,    # 10% - Awards/media coverage
            'leadership': 0.05,     # 5% - Leadership quality
            'impact': 0.10,         # 10% - Social/industry impact
        }
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def research_extraordinary_profile(self, entity_name: str, entity_type: str = 'company') -> ExtraordinaryProfile:
        """Research and create comprehensive extraordinary profile"""
        
        logger.info(f"Researching extraordinary profile for {entity_name}")
        
        # Gather data from multiple sources
        research_data = await self._gather_comprehensive_data(entity_name, entity_type)
        
        # Extract metrics
        metrics = await self._extract_metrics(research_data, entity_name)
        
        # Calculate extraordinary score
        extraordinary_score = await self._calculate_extraordinary_score(metrics, research_data)
        
        # Extract profile components
        achievements = await self._extract_achievements(research_data)
        awards = await self._extract_awards_recognitions(research_data)
        media_coverage = await self._extract_media_coverage(research_data)
        key_stats = await self._extract_key_stats(research_data, metrics)
        innovations = await self._extract_innovations(research_data)
        advantages = await self._extract_competitive_advantages(research_data)
        leadership = await self._extract_leadership_team(research_data)
        funding = await self._extract_funding_history(research_data)
        
        return ExtraordinaryProfile(
            name=entity_name,
            type=entity_type,
            extraordinary_score=extraordinary_score,
            metrics=metrics,
            notable_achievements=achievements,
            awards_recognitions=awards,
            media_coverage=media_coverage,
            key_stats=key_stats,
            innovation_highlights=innovations,
            competitive_advantages=advantages,
            leadership_team=leadership,
            funding_history=funding,
            created_at=datetime.now()
        )
    
    async def _gather_comprehensive_data(self, entity_name: str, entity_type: str) -> Dict:
        """Gather data from multiple sources"""
        
        research_queries = [
            f"{entity_name} company valuation funding revenue",
            f"{entity_name} awards recognition achievements",
            f"{entity_name} innovation patents technology breakthrough",
            f"{entity_name} CEO founder leadership team",
            f"{entity_name} market share competition industry leader",
            f"{entity_name} unicorn IPO acquisition exit",
            f"{entity_name} growth metrics performance statistics",
            f"{entity_name} media coverage news articles press"
        ]
        
        all_data = []
        
        # Use Exa API for comprehensive research
        if self.exa_api_key:
            for query in research_queries:
                try:
                    data = await self._search_exa(query)
                    all_data.extend(data.get('results', []))
                    await asyncio.sleep(0.5)  # Rate limiting
                except Exception as e:
                    logger.error(f"Error searching with query '{query}': {e}")
        
        return {
            'search_results': all_data,
            'entity_name': entity_name,
            'entity_type': entity_type,
            'research_timestamp': datetime.now().isoformat()
        }
    
    async def _search_exa(self, query: str) -> Dict:
        """Search using Exa API"""
        headers = {
            "Authorization": f"Bearer {self.exa_api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "query": query,
            "type": "neural",
            "useAutoprompt": True,
            "numResults": 10,
            "contents": {
                "text": True,
                "highlights": True,
                "summary": True
            },
            "startPublishedDate": (datetime.now() - timedelta(days=365*2)).isoformat(),
            "category": "company"
        }
        
        async with self.session.post(
            f"{self.data_sources['exa']}/search",
            headers=headers,
            json=payload
        ) as response:
            if response.status == 200:
                return await response.json()
            else:
                logger.error(f"Exa API error: {response.status}")
                return {}
    
    async def _extract_metrics(self, research_data: Dict, entity_name: str) -> ExtraordinaryMetrics:
        """Extract quantitative metrics from research data"""
        
        metrics = ExtraordinaryMetrics()
        
        all_text = ""
        for result in research_data.get('search_results', []):
            all_text += f"{result.get('title', '')} {result.get('summary', '')} {result.get('text', '')} "
        
        all_text = all_text.lower()
        
        # Extract valuation
        valuation_patterns = [
            r'valued at \$(\d+(?:\.\d+)?)\s*billion',
            r'valuation of \$(\d+(?:\.\d+)?)\s*billion',
            r'\$(\d+(?:\.\d+)?)\s*billion valuation',
            r'worth \$(\d+(?:\.\d+)?)\s*billion'
        ]
        
        for pattern in valuation_patterns:
            matches = re.findall(pattern, all_text)
            if matches:
                metrics.valuation = float(matches[0]) * 1_000_000_000
                break
        
        # Extract funding
        funding_patterns = [
            r'raised \$(\d+(?:\.\d+)?)\s*billion',
            r'funding of \$(\d+(?:\.\d+)?)\s*billion',
            r'\$(\d+(?:\.\d+)?)\s*billion in funding',
            r'series [a-z] \$(\d+(?:\.\d+)?)\s*million'
        ]
        
        for pattern in funding_patterns:
            matches = re.findall(pattern, all_text)
            if matches:
                if 'billion' in pattern:
                    metrics.funding_raised = float(matches[0]) * 1_000_000_000
                else:
                    metrics.funding_raised = float(matches[0]) * 1_000_000
                break
        
        # Extract employee count
        employee_patterns = [
            r'(\d+,?\d*)\s*employees',
            r'team of (\d+,?\d*)',
            r'workforce of (\d+,?\d*)'
        ]
        
        for pattern in employee_patterns:
            matches = re.findall(pattern, all_text)
            if matches:
                metrics.employee_count = int(matches[0].replace(',', ''))
                break
        
        # Extract revenue
        revenue_patterns = [
            r'revenue of \$(\d+(?:\.\d+)?)\s*billion',
            r'\$(\d+(?:\.\d+)?)\s*billion in revenue',
            r'annual revenue \$(\d+(?:\.\d+)?)\s*million'
        ]
        
        for pattern in revenue_patterns:
            matches = re.findall(pattern, all_text)
            if matches:
                if 'billion' in pattern:
                    metrics.revenue = float(matches[0]) * 1_000_000_000
                else:
                    metrics.revenue = float(matches[0]) * 1_000_000
                break
        
        # Check for unicorn/IPO status
        metrics.unicorn_status = 'unicorn' in all_text or metrics.valuation >= 1_000_000_000
        metrics.ipo_status = any(term in all_text for term in ['ipo', 'public offering', 'nasdaq', 'nyse'])
        
        # Count awards and media mentions
        metrics.awards_count = len(re.findall(r'award|recognition|prize|honor', all_text))
        metrics.media_mentions = len(research_data.get('search_results', []))
        
        # Extract years in business
        founded_patterns = [
            r'founded in (\d{4})',
            r'established (\d{4})',
            r'started in (\d{4})'
        ]
        
        for pattern in founded_patterns:
            matches = re.findall(pattern, all_text)
            if matches:
                founded_year = int(matches[0])
                metrics.years_in_business = datetime.now().year - founded_year
                break
        
        return metrics
    
    async def _calculate_extraordinary_score(self, metrics: ExtraordinaryMetrics, research_data: Dict) -> float:
        """Calculate extraordinary score based on multiple factors"""
        
        score = 0.0
        
        # Valuation score (0-20 points)
        if metrics.valuation >= 100_000_000_000:  # $100B+
            score += 20
        elif metrics.valuation >= 10_000_000_000:  # $10B+
            score += 15
        elif metrics.valuation >= 1_000_000_000:   # $1B+ (Unicorn)
            score += 10
        elif metrics.valuation >= 100_000_000:     # $100M+
            score += 5
        
        # Funding score (0-15 points)
        if metrics.funding_raised >= 1_000_000_000:  # $1B+
            score += 15
        elif metrics.funding_raised >= 500_000_000:  # $500M+
            score += 12
        elif metrics.funding_raised >= 100_000_000:  # $100M+
            score += 8
        elif metrics.funding_raised >= 50_000_000:   # $50M+
            score += 5
        
        # Growth/Scale score (0-15 points)
        if metrics.employee_count >= 10000:
            score += 15
        elif metrics.employee_count >= 5000:
            score += 12
        elif metrics.employee_count >= 1000:
            score += 8
        elif metrics.employee_count >= 500:
            score += 5
        
        # Innovation score (0-15 points)
        innovation_keywords = ['breakthrough', 'revolutionary', 'first', 'pioneer', 'disruptive', 'innovation']
        all_text = ' '.join([r.get('summary', '') for r in research_data.get('search_results', [])])
        innovation_mentions = sum(1 for keyword in innovation_keywords if keyword in all_text.lower())
        score += min(innovation_mentions * 2, 15)
        
        # Market position score (0-10 points)
        market_keywords = ['leader', 'dominant', 'market share', 'industry leader', 'top company']
        market_mentions = sum(1 for keyword in market_keywords if keyword in all_text.lower())
        score += min(market_mentions * 2, 10)
        
        # Recognition score (0-10 points)
        score += min(metrics.awards_count, 10)
        
        # Leadership score (0-5 points)
        leadership_keywords = ['ceo', 'founder', 'visionary', 'entrepreneur']
        leadership_mentions = sum(1 for keyword in leadership_keywords if keyword in all_text.lower())
        score += min(leadership_mentions, 5)
        
        # Impact score (0-10 points)
        impact_keywords = ['impact', 'change', 'transform', 'revolutionize', 'disrupt']
        impact_mentions = sum(1 for keyword in impact_keywords if keyword in all_text.lower())
        score += min(impact_mentions, 10)
        
        # Bonus points
        if metrics.unicorn_status:
            score += 5
        if metrics.ipo_status:
            score += 5
        
        return min(score, 100.0)  # Cap at 100
    
    async def _extract_achievements(self, research_data: Dict) -> List[str]:
        """Extract notable achievements"""
        achievements = []
        
        achievement_patterns = [
            r'first to (.{1,100})',
            r'pioneered (.{1,100})',
            r'breakthrough in (.{1,100})',
            r'revolutionized (.{1,100})',
            r'achieved (.{1,100})',
            r'milestone (.{1,100})'
        ]
        
        for result in research_data.get('search_results', []):
            text = f"{result.get('title', '')} {result.get('summary', '')}"
            
            for pattern in achievement_patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                achievements.extend(matches[:2])  # Limit per result
        
        return list(set(achievements))[:10]  # Top 10 unique achievements
    
    async def _extract_awards_recognitions(self, research_data: Dict) -> List[Dict]:
        """Extract awards and recognitions"""
        awards = []
        
        for result in research_data.get('search_results', []):
            text = f"{result.get('title', '')} {result.get('summary', '')}"
            
            if any(keyword in text.lower() for keyword in ['award', 'recognition', 'honor', 'prize']):
                awards.append({
                    'title': result.get('title', ''),
                    'source': result.get('url', ''),
                    'date': result.get('publishedDate', ''),
                    'description': result.get('summary', '')[:200] + '...'
                })
        
        return awards[:5]  # Top 5 awards
    
    async def _extract_media_coverage(self, research_data: Dict) -> List[Dict]:
        """Extract notable media coverage"""
        media = []
        
        credible_sources = ['techcrunch', 'forbes', 'bloomberg', 'wsj', 'reuters', 'ft.com']
        
        for result in research_data.get('search_results', []):
            url = result.get('url', '').lower()
            
            if any(source in url for source in credible_sources):
                media.append({
                    'title': result.get('title', ''),
                    'source': result.get('url', ''),
                    'date': result.get('publishedDate', ''),
                    'summary': result.get('summary', '')[:200] + '...'
                })
        
        return sorted(media, key=lambda x: x.get('date', ''), reverse=True)[:10]
    
    async def _extract_key_stats(self, research_data: Dict, metrics: ExtraordinaryMetrics) -> Dict:
        """Extract key statistics"""
        return {
            'valuation': f"${metrics.valuation/1_000_000_000:.1f}B" if metrics.valuation >= 1_000_000_000 else f"${metrics.valuation/1_000_000:.1f}M",
            'funding_raised': f"${metrics.funding_raised/1_000_000_000:.1f}B" if metrics.funding_raised >= 1_000_000_000 else f"${metrics.funding_raised/1_000_000:.1f}M",
            'employees': f"{metrics.employee_count:,}",
            'years_active': metrics.years_in_business,
            'unicorn_status': metrics.unicorn_status,
            'public_status': metrics.ipo_status,
            'media_mentions': metrics.media_mentions,
            'awards_count': metrics.awards_count
        }
    
    async def _extract_innovations(self, research_data: Dict) -> List[str]:
        """Extract innovation highlights"""
        innovations = []
        
        innovation_patterns = [
            r'invented (.{1,100})',
            r'developed (.{1,100})',
            r'created (.{1,100})',
            r'innovation in (.{1,100})',
            r'patent for (.{1,100})'
        ]
        
        for result in research_data.get('search_results', []):
            text = f"{result.get('title', '')} {result.get('summary', '')}"
            
            for pattern in innovation_patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                innovations.extend(matches[:2])
        
        return list(set(innovations))[:8]
    
    async def _extract_competitive_advantages(self, research_data: Dict) -> List[str]:
        """Extract competitive advantages"""
        advantages = []
        
        advantage_patterns = [
            r'advantage (.{1,100})',
            r'unique (.{1,100})',
            r'differentiated (.{1,100})',
            r'proprietary (.{1,100})',
            r'exclusive (.{1,100})'
        ]
        
        for result in research_data.get('search_results', []):
            text = f"{result.get('title', '')} {result.get('summary', '')}"
            
            for pattern in advantage_patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                advantages.extend(matches[:2])
        
        return list(set(advantages))[:6]
    
    async def _extract_leadership_team(self, research_data: Dict) -> List[Dict]:
        """Extract leadership team information"""
        leaders = []
        
        for result in research_data.get('search_results', []):
            text = f"{result.get('title', '')} {result.get('summary', '')}"
            
            # Look for CEO, founder mentions
            if any(keyword in text.lower() for keyword in ['ceo', 'founder', 'chief executive']):
                # Extract names (simplified pattern)
                name_patterns = [
                    r'CEO ([A-Z][a-z]+ [A-Z][a-z]+)',
                    r'founder ([A-Z][a-z]+ [A-Z][a-z]+)',
                    r'([A-Z][a-z]+ [A-Z][a-z]+), CEO'
                ]
                
                for pattern in name_patterns:
                    matches = re.findall(pattern, text)
                    for match in matches:
                        leaders.append({
                            'name': match,
                            'role': 'CEO/Founder',
                            'source': result.get('url', '')
                        })
        
        return leaders[:3]  # Top 3 leaders
    
    async def _extract_funding_history(self, research_data: Dict) -> List[Dict]:
        """Extract funding history"""
        funding_rounds = []
        
        for result in research_data.get('search_results', []):
            text = f"{result.get('title', '')} {result.get('summary', '')}"
            
            if any(keyword in text.lower() for keyword in ['series', 'funding', 'raised', 'investment']):
                funding_rounds.append({
                    'description': result.get('title', ''),
                    'source': result.get('url', ''),
                    'date': result.get('publishedDate', ''),
                    'details': result.get('summary', '')[:150] + '...'
                })
        
        return funding_rounds[:5]  # Top 5 funding events

# Additional data sources you could integrate:
ADDITIONAL_DATA_SOURCES = {
    'crunchbase': 'Comprehensive startup/company database with funding, team, metrics',
    'pitchbook': 'Private market intelligence and valuations',
    'bloomberg_terminal': 'Financial data and market intelligence',
    'linkedin_api': 'Company size, employee data, leadership info',
    'glassdoor_api': 'Employee reviews and company culture insights',
    'patent_databases': 'USPTO, Google Patents for innovation metrics',
    'sec_filings': 'Public company financial data',
    'news_apis': 'NewsAPI, Bing News for media coverage analysis',
    'social_media_apis': 'Twitter, Reddit for sentiment and buzz analysis',
    'github_api': 'Open source contributions and developer activity',
    'app_store_apis': 'App rankings and download metrics',
    'web_traffic_apis': 'SimilarWeb, Alexa for website traffic data'
}
