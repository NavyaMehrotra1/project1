import os
import asyncio
import json
import re
from typing import List, Dict, Optional, Tuple
import aiohttp
from datetime import datetime, timedelta
import logging
from models.ma_events import MAEvent, EventType, EventStatus, CompanyInfo, EcosystemImpact

logger = logging.getLogger(__name__)

class MAIntelligenceService:
    def __init__(self):
        self.api_key = os.getenv('EXA_API_KEY')
        self.base_url = "https://api.exa.ai"
        self.session = None
        
        # M&A specific search queries
        self.ma_queries = [
            "merger acquisition startup tech company announced",
            "strategic partnership joint venture startup",
            "business consolidation acquisition deal",
            "startup acquired merger deal value",
            "strategic alliance partnership agreement",
            "venture capital acquisition exit",
            "tech company merger consolidation",
            "startup partnership strategic deal"
        ]
        
        # Keywords for event type classification
        self.event_keywords = {
            EventType.MERGER_ACQUISITION: [
                "merger", "acquisition", "acquired", "acquires", "buyout", 
                "takeover", "purchase", "bought", "exit", "deal"
            ],
            EventType.BUSINESS_PARTNERSHIP: [
                "partnership", "partner", "collaboration", "collaborate",
                "agreement", "deal", "contract", "alliance"
            ],
            EventType.CONSOLIDATION: [
                "consolidation", "consolidate", "merge", "combining",
                "integration", "unified", "streamline"
            ],
            EventType.JOINT_VENTURE: [
                "joint venture", "jv", "joint", "venture", "consortium",
                "cooperative", "shared venture"
            ],
            EventType.STRATEGIC_ALLIANCE: [
                "strategic alliance", "strategic partnership", "strategic agreement",
                "strategic cooperation", "strategic collaboration"
            ]
        }
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def search_ma_events(self, time_range_hours: int = 24) -> List[MAEvent]:
        """Search for M&A events in the specified time range"""
        if not self.api_key:
            logger.error("EXA_API_KEY not found in environment variables")
            return []
            
        start_date = datetime.now() - timedelta(hours=time_range_hours)
        all_events = []
        
        # Search with multiple queries to get comprehensive coverage
        for query in self.ma_queries:
            try:
                events = await self._search_with_query(query, start_date)
                all_events.extend(events)
                await asyncio.sleep(0.5)  # Rate limiting
            except Exception as e:
                logger.error(f"Error searching with query '{query}': {e}")
                continue
        
        # Deduplicate and rank events
        unique_events = self._deduplicate_events(all_events)
        return sorted(unique_events, key=lambda x: x.confidence_score, reverse=True)
    
    async def _search_with_query(self, query: str, start_date: datetime) -> List[MAEvent]:
        """Search for events with a specific query"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "query": query,
            "type": "neural",
            "useAutoprompt": True,
            "numResults": 20,
            "contents": {
                "text": True,
                "highlights": True,
                "summary": True
            },
            "startPublishedDate": start_date.isoformat(),
            "category": "company"
        }
        
        try:
            async with self.session.post(
                f"{self.base_url}/search",
                headers=headers,
                json=payload
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return await self._process_search_results(data, query)
                else:
                    error_text = await response.text()
                    logger.error(f"Exa API error: {response.status} - {error_text}")
                    return []
                    
        except Exception as e:
            logger.error(f"Error calling Exa API: {str(e)}")
            return []
    
    async def _process_search_results(self, exa_data: Dict, query: str) -> List[MAEvent]:
        """Process Exa search results into MAEvent objects"""
        results = exa_data.get("results", [])
        events = []
        
        for result in results:
            try:
                event = await self._extract_ma_event(result, query)
                if event:
                    events.append(event)
            except Exception as e:
                logger.error(f"Error processing result: {e}")
                continue
        
        return events
    
    async def _extract_ma_event(self, result: Dict, query: str) -> Optional[MAEvent]:
        """Extract M&A event information from a search result"""
        title = result.get("title", "")
        summary = result.get("summary", "")
        text = result.get("text", "")
        url = result.get("url", "")
        published_date = result.get("publishedDate", "")
        
        # Combine all text for analysis
        full_text = f"{title} {summary} {text}".lower()
        
        # Classify event type
        event_type = self._classify_event_type(full_text)
        if not event_type:
            return None
        
        # Extract companies
        companies = self._extract_companies(full_text, title)
        if len(companies) < 1:
            return None
        
        # Extract deal value
        deal_value = self._extract_deal_value(full_text)
        
        # Calculate confidence score
        confidence = self._calculate_confidence(result, event_type, companies, deal_value)
        
        # Create event
        event_id = f"ma_{hash(url)}_{int(datetime.now().timestamp())}"
        
        try:
            event = MAEvent(
                id=event_id,
                event_type=event_type,
                status=EventStatus.ANNOUNCED,
                primary_company=CompanyInfo(name=companies[0]),
                secondary_company=CompanyInfo(name=companies[1]) if len(companies) > 1 else None,
                other_companies=[CompanyInfo(name=c) for c in companies[2:]] if len(companies) > 2 else [],
                title=title,
                description=summary[:500] if summary else title,
                deal_value=deal_value,
                announced_date=self._parse_date(published_date),
                sources=[{
                    "url": url,
                    "title": title,
                    "published_date": published_date,
                    "query_used": query
                }],
                confidence_score=confidence,
                discovered_at=datetime.now(),
                last_updated=datetime.now()
            )
            return event
        except Exception as e:
            logger.error(f"Error creating MAEvent: {e}")
            return None
    
    def _classify_event_type(self, text: str) -> Optional[EventType]:
        """Classify the type of M&A event based on text content"""
        scores = {}
        
        for event_type, keywords in self.event_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text)
            if score > 0:
                scores[event_type] = score
        
        if not scores:
            return None
        
        # Return the event type with the highest score
        return max(scores.items(), key=lambda x: x[1])[0]
    
    def _extract_companies(self, text: str, title: str) -> List[str]:
        """Extract company names from text"""
        companies = []
        
        # Common patterns for company mentions
        patterns = [
            r'([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)*)\s+(?:acquires|acquired|merges|partners)',
            r'(?:acquires|acquired|merges|partners)\s+([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)*)',
            r'([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)*)\s+and\s+([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)*)',
            r'([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)*)\s+Inc\.?',
            r'([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)*)\s+Corp\.?',
            r'([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)*)\s+Ltd\.?'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, title + " " + text)
            if isinstance(matches[0], tuple) if matches else False:
                for match_group in matches:
                    companies.extend([m.strip() for m in match_group if m.strip()])
            else:
                companies.extend([m.strip() for m in matches])
        
        # Clean and deduplicate
        cleaned_companies = []
        for company in companies:
            if len(company) > 2 and company not in cleaned_companies:
                # Remove common suffixes
                company = re.sub(r'\s+(Inc|Corp|Ltd|LLC)\.?$', '', company)
                if company:
                    cleaned_companies.append(company)
        
        return cleaned_companies[:5]  # Limit to 5 companies
    
    def _extract_deal_value(self, text: str) -> Optional[float]:
        """Extract deal value from text"""
        # Patterns for deal values
        patterns = [
            r'\$(\d+(?:\.\d+)?)\s*billion',
            r'\$(\d+(?:\.\d+)?)\s*million',
            r'\$(\d+(?:,\d{3})*(?:\.\d+)?)',
            r'(\d+(?:\.\d+)?)\s*billion\s*dollars?',
            r'(\d+(?:\.\d+)?)\s*million\s*dollars?'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                try:
                    value = float(matches[0].replace(',', ''))
                    if 'billion' in pattern:
                        value *= 1_000_000_000
                    elif 'million' in pattern:
                        value *= 1_000_000
                    return value
                except ValueError:
                    continue
        
        return None
    
    def _calculate_confidence(self, result: Dict, event_type: EventType, 
                            companies: List[str], deal_value: Optional[float]) -> float:
        """Calculate confidence score for the event"""
        # All events from Exa API are considered high confidence
        # since they come from real news sources about actual events
        return 1.0
    
    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse date string to datetime object"""
        if not date_str:
            return None
        
        try:
            # Handle ISO format with Z
            if date_str.endswith('Z'):
                date_str = date_str[:-1] + '+00:00'
            return datetime.fromisoformat(date_str).replace(tzinfo=None)
        except:
            return None
    
    def _deduplicate_events(self, events: List[MAEvent]) -> List[MAEvent]:
        """Remove duplicate events based on similarity"""
        if not events:
            return []
        
        unique_events = []
        seen_combinations = set()
        
        for event in events:
            # Create a signature for the event
            companies = [event.primary_company.name]
            if event.secondary_company:
                companies.append(event.secondary_company.name)
            companies.extend([c.name for c in event.other_companies])
            
            signature = (
                event.event_type.value,
                tuple(sorted(companies)),
                event.deal_value
            )
            
            if signature not in seen_combinations:
                seen_combinations.add(signature)
                unique_events.append(event)
        
        return unique_events

    async def analyze_ecosystem_impact(self, event: MAEvent, 
                                     existing_companies: List[Dict]) -> EcosystemImpact:
        """Analyze how an M&A event impacts the startup ecosystem"""
        affected_companies = []
        impact_score = 0.0
        impact_description = ""
        
        # Get all companies involved in the event
        event_companies = [event.primary_company.name]
        if event.secondary_company:
            event_companies.append(event.secondary_company.name)
        event_companies.extend([c.name for c in event.other_companies])
        
        # Find related companies in the ecosystem
        for company_data in existing_companies:
            company_name = company_data.get('name', '')
            company_industry = company_data.get('industry', '')
            
            # Check if company is directly involved
            if company_name in event_companies:
                affected_companies.append(company_name)
                impact_score += 0.3
                continue
            
            # Check for industry overlap
            for event_company in event_companies:
                if self._companies_related(company_name, event_company, company_industry):
                    affected_companies.append(company_name)
                    impact_score += 0.1
        
        # Calculate final impact score
        impact_score = min(impact_score, 1.0)
        
        # Generate impact description
        if event.event_type == EventType.MERGER_ACQUISITION:
            impact_description = f"Acquisition of {event.secondary_company.name if event.secondary_company else 'target company'} by {event.primary_company.name} may affect competitive landscape"
        elif event.event_type == EventType.STRATEGIC_ALLIANCE:
            impact_description = f"Strategic alliance between {event.primary_company.name} and partners may create new market opportunities"
        else:
            impact_description = f"{event.event_type.value.replace('_', ' ').title()} involving {event.primary_company.name} may influence industry dynamics"
        
        return EcosystemImpact(
            event_id=event.id,
            affected_companies=affected_companies,
            impact_type="competitive",
            impact_score=impact_score,
            description=impact_description
        )
    
    def _companies_related(self, company1: str, company2: str, industry: str) -> bool:
        """Check if two companies are related (same industry, competitors, etc.)"""
        # Simple heuristic - can be enhanced with more sophisticated matching
        if not industry:
            return False
        
        # Check if companies are in similar industries
        similar_industries = {
            'fintech': ['finance', 'banking', 'payments'],
            'ai': ['artificial intelligence', 'machine learning', 'data'],
            'saas': ['software', 'enterprise', 'productivity'],
            'ecommerce': ['retail', 'marketplace', 'shopping']
        }
        
        industry_lower = industry.lower()
        for category, keywords in similar_industries.items():
            if any(keyword in industry_lower for keyword in keywords):
                return True
        
        return False
