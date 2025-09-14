"""
Unstructured Text Processing Service for HackMIT
Extracts structured M&A data from messy, unstructured text sources
"""

import json
import logging
import re
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
import asyncio

logger = logging.getLogger(__name__)

@dataclass
class ExtractedMAEvent:
    """Structured M&A event extracted from unstructured text"""
    source_company: Optional[str] = None
    target_company: Optional[str] = None
    deal_type: Optional[str] = None
    deal_value: Optional[float] = None
    deal_date: Optional[str] = None
    description: Optional[str] = None
    confidence_score: float = 0.0
    extraction_metadata: Dict[str, Any] = None

class UnstructuredTextProcessor:
    """
    Processes messy, unstructured text to extract structured M&A information
    Demonstrates advanced NLP and LLM integration for HackMIT
    """
    
    def __init__(self):
        self.deal_type_patterns = {
            'acquisition': [
                r'acquire[ds]?', r'acquisition', r'bought', r'purchase[ds]?', 
                r'takeover', r'buyout', r'absorb[s]?'
            ],
            'merger': [
                r'merg[ers]?', r'combining', r'consolidat[e|ion]', 
                r'join[s|ed]? forces', r'unite[d|s]?'
            ],
            'partnership': [
                r'partner[ship]?', r'collaborat[e|ion]', r'alliance', 
                r'team[s]? up', r'work[s]? together'
            ],
            'funding': [
                r'raised?', r'funding', r'investment', r'round', r'capital',
                r'Series [A-Z]', r'seed', r'venture'
            ],
            'ipo': [
                r'IPO', r'public offering', r'going public', r'list[ed|ing]'
            ]
        }
        
        self.value_patterns = [
            r'\$([0-9,.]+)\s*(billion|B|million|M|thousand|K)',
            r'([0-9,.]+)\s*(billion|B|million|M|thousand|K)\s*dollars?',
            r'valued at\s*\$?([0-9,.]+)\s*(billion|B|million|M)',
            r'worth\s*\$?([0-9,.]+)\s*(billion|B|million|M)'
        ]
        
        self.date_patterns = [
            r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            r'(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}',
            r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{1,2},?\s+\d{4}',
            r'(\d{4}-\d{2}-\d{2})'
        ]
        
        # Company name indicators
        self.company_indicators = [
            r'Inc\.?', r'Corp\.?', r'LLC', r'Ltd\.?', r'Co\.?', 
            r'Company', r'Technologies', r'Tech', r'Systems'
        ]
    
    async def process_unstructured_text(self, text: str, source_info: Dict[str, Any] = None) -> List[ExtractedMAEvent]:
        """
        Main method to extract M&A events from unstructured text
        
        Args:
            text: Raw unstructured text (press release, news article, social media post)
            source_info: Metadata about the source
            
        Returns:
            List of extracted M&A events with confidence scores
        """
        # Clean and preprocess text
        cleaned_text = self._clean_text(text)
        
        # Extract potential events using multiple methods
        pattern_events = self._extract_with_patterns(cleaned_text)
        llm_events = await self._extract_with_llm(cleaned_text)
        
        # Combine and deduplicate events
        all_events = pattern_events + llm_events
        deduplicated_events = self._deduplicate_events(all_events)
        
        # Score and filter events
        scored_events = []
        for event in deduplicated_events:
            confidence = self._calculate_extraction_confidence(event, cleaned_text)
            if confidence > 0.3:  # Minimum confidence threshold
                event.confidence_score = confidence
                event.extraction_metadata = {
                    'source_info': source_info or {},
                    'extraction_method': 'hybrid_pattern_llm',
                    'text_length': len(text),
                    'processed_at': datetime.now().isoformat()
                }
                scored_events.append(event)
        
        return scored_events
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text for processing"""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Fix common encoding issues
        text = text.replace('â€™', "'").replace('â€œ', '"').replace('â€', '"')
        
        # Remove HTML tags if present
        text = re.sub(r'<[^>]+>', '', text)
        
        # Normalize quotes and dashes
        text = text.replace('"', '"').replace('"', '"')
        text = text.replace('–', '-').replace('—', '-')
        
        return text.strip()
    
    def _extract_with_patterns(self, text: str) -> List[ExtractedMAEvent]:
        """Extract events using regex patterns"""
        events = []
        
        # Find sentences that might contain M&A information
        sentences = self._split_into_sentences(text)
        
        for sentence in sentences:
            # Check for deal type indicators
            deal_type = self._identify_deal_type(sentence)
            if not deal_type:
                continue
            
            # Extract companies
            companies = self._extract_companies(sentence)
            if len(companies) < 1:
                continue
            
            # Extract financial information
            deal_value = self._extract_deal_value(sentence)
            
            # Extract dates
            deal_date = self._extract_date(sentence)
            
            # Create event
            event = ExtractedMAEvent(
                source_company=companies[0] if len(companies) > 0 else None,
                target_company=companies[1] if len(companies) > 1 else None,
                deal_type=deal_type,
                deal_value=deal_value,
                deal_date=deal_date,
                description=sentence[:200] + "..." if len(sentence) > 200 else sentence
            )
            
            events.append(event)
        
        return events
    
    async def _extract_with_llm(self, text: str) -> List[ExtractedMAEvent]:
        """Extract events using LLM (Claude/GPT) for complex cases"""
        try:
            # This would integrate with your existing Claude service
            # For now, return empty list - implement based on your Claude integration
            return []
        except Exception as e:
            logger.error(f"LLM extraction failed: {e}")
            return []
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences for processing"""
        # Simple sentence splitting - could be enhanced with NLTK
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if len(s.strip()) > 20]
    
    def _identify_deal_type(self, text: str) -> Optional[str]:
        """Identify the type of M&A deal from text"""
        text_lower = text.lower()
        
        for deal_type, patterns in self.deal_type_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    return deal_type
        
        return None
    
    def _extract_companies(self, text: str) -> List[str]:
        """Extract company names from text"""
        companies = []
        
        # Look for capitalized words that might be company names
        # This is a simplified approach - could be enhanced with NER
        words = text.split()
        
        potential_companies = []
        current_company = []
        
        for i, word in enumerate(words):
            # Check if word looks like part of a company name
            if (word[0].isupper() and len(word) > 2) or any(indicator in word for indicator in self.company_indicators):
                current_company.append(word)
            else:
                if current_company:
                    company_name = ' '.join(current_company)
                    if self._is_likely_company_name(company_name):
                        potential_companies.append(company_name)
                    current_company = []
        
        # Add final company if exists
        if current_company:
            company_name = ' '.join(current_company)
            if self._is_likely_company_name(company_name):
                potential_companies.append(company_name)
        
        # Filter and return top candidates
        return potential_companies[:2]  # Return up to 2 companies
    
    def _is_likely_company_name(self, name: str) -> bool:
        """Determine if a string is likely a company name"""
        # Must be reasonable length
        if len(name) < 2 or len(name) > 50:
            return False
        
        # Should contain at least one letter
        if not re.search(r'[a-zA-Z]', name):
            return False
        
        # Bonus points for company indicators
        if any(indicator in name for indicator in self.company_indicators):
            return True
        
        # Should be mostly alphanumeric
        alphanumeric_ratio = len(re.findall(r'[a-zA-Z0-9]', name)) / len(name)
        return alphanumeric_ratio > 0.7
    
    def _extract_deal_value(self, text: str) -> Optional[float]:
        """Extract financial deal value from text"""
        for pattern in self.value_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    # Extract number and unit
                    if len(match.groups()) >= 2:
                        number_str = match.group(1).replace(',', '')
                        unit = match.group(2).lower()
                    else:
                        # Handle patterns with single group
                        full_match = match.group(0)
                        number_match = re.search(r'([0-9,.]+)', full_match)
                        unit_match = re.search(r'(billion|B|million|M|thousand|K)', full_match, re.IGNORECASE)
                        
                        if not number_match or not unit_match:
                            continue
                        
                        number_str = number_match.group(1).replace(',', '')
                        unit = unit_match.group(1).lower()
                    
                    number = float(number_str)
                    
                    # Convert to standard units (dollars)
                    multipliers = {
                        'billion': 1_000_000_000, 'b': 1_000_000_000,
                        'million': 1_000_000, 'm': 1_000_000,
                        'thousand': 1_000, 'k': 1_000
                    }
                    
                    multiplier = multipliers.get(unit, 1)
                    return number * multiplier
                    
                except (ValueError, IndexError):
                    continue
        
        return None
    
    def _extract_date(self, text: str) -> Optional[str]:
        """Extract dates from text"""
        for pattern in self.date_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                date_str = match.group(1)
                # Normalize date format
                try:
                    # Try to parse and reformat
                    parsed_date = self._parse_flexible_date(date_str)
                    if parsed_date:
                        return parsed_date.strftime('%Y-%m-%d')
                except:
                    # Return as-is if parsing fails
                    return date_str
        
        return None
    
    def _parse_flexible_date(self, date_str: str) -> Optional[datetime]:
        """Parse dates in various formats"""
        formats = [
            '%m/%d/%Y', '%m-%d-%Y', '%d/%m/%Y', '%d-%m-%Y',
            '%Y-%m-%d', '%Y/%m/%d',
            '%B %d, %Y', '%B %d %Y',
            '%b %d, %Y', '%b %d %Y'
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        
        return None
    
    def _deduplicate_events(self, events: List[ExtractedMAEvent]) -> List[ExtractedMAEvent]:
        """Remove duplicate events"""
        unique_events = []
        
        for event in events:
            is_duplicate = False
            
            for existing_event in unique_events:
                if self._events_are_similar(event, existing_event):
                    # Keep the one with higher confidence or more complete data
                    if self._is_better_event(event, existing_event):
                        unique_events.remove(existing_event)
                        unique_events.append(event)
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                unique_events.append(event)
        
        return unique_events
    
    def _events_are_similar(self, event1: ExtractedMAEvent, event2: ExtractedMAEvent) -> bool:
        """Check if two events are likely duplicates"""
        # Compare company names (fuzzy matching)
        companies1 = {event1.source_company, event1.target_company}
        companies2 = {event2.source_company, event2.target_company}
        companies1.discard(None)
        companies2.discard(None)
        
        if companies1 and companies2:
            # Check for any overlap in company names
            for c1 in companies1:
                for c2 in companies2:
                    if c1 and c2 and self._company_names_similar(c1, c2):
                        return True
        
        return False
    
    def _company_names_similar(self, name1: str, name2: str) -> bool:
        """Check if two company names are similar"""
        from difflib import SequenceMatcher
        
        # Normalize names
        norm1 = re.sub(r'\b(Inc|Corp|LLC|Ltd|Co|Company)\b\.?', '', name1, flags=re.IGNORECASE).strip()
        norm2 = re.sub(r'\b(Inc|Corp|LLC|Ltd|Co|Company)\b\.?', '', name2, flags=re.IGNORECASE).strip()
        
        similarity = SequenceMatcher(None, norm1.lower(), norm2.lower()).ratio()
        return similarity > 0.8
    
    def _is_better_event(self, event1: ExtractedMAEvent, event2: ExtractedMAEvent) -> bool:
        """Determine which event has better/more complete data"""
        score1 = self._calculate_completeness_score(event1)
        score2 = self._calculate_completeness_score(event2)
        return score1 > score2
    
    def _calculate_completeness_score(self, event: ExtractedMAEvent) -> float:
        """Calculate completeness score for an event"""
        score = 0.0
        
        if event.source_company:
            score += 0.2
        if event.target_company:
            score += 0.2
        if event.deal_type:
            score += 0.2
        if event.deal_value:
            score += 0.2
        if event.deal_date:
            score += 0.1
        if event.description:
            score += 0.1
        
        return score
    
    def _calculate_extraction_confidence(self, event: ExtractedMAEvent, original_text: str) -> float:
        """Calculate confidence score for extracted event"""
        confidence = 0.5  # Base confidence
        
        # Bonus for completeness
        completeness = self._calculate_completeness_score(event)
        confidence += completeness * 0.3
        
        # Bonus for deal value presence and reasonableness
        if event.deal_value:
            if 1_000_000 <= event.deal_value <= 1_000_000_000_000:  # $1M to $1T
                confidence += 0.1
            else:
                confidence -= 0.1  # Penalty for unrealistic values
        
        # Bonus for recent dates
        if event.deal_date:
            try:
                date_obj = datetime.strptime(event.deal_date, '%Y-%m-%d')
                days_old = (datetime.now() - date_obj).days
                if days_old < 365:  # Within last year
                    confidence += 0.1
            except:
                pass
        
        # Penalty for very short descriptions
        if event.description and len(event.description) < 50:
            confidence -= 0.1
        
        return max(0.0, min(1.0, confidence))

# Integration functions
def process_messy_press_release(text: str) -> List[Dict[str, Any]]:
    """
    Process a messy press release and extract structured M&A events
    Demo function for HackMIT
    """
    processor = UnstructuredTextProcessor()
    
    # Run async processing in sync context
    import asyncio
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        events = loop.run_until_complete(
            processor.process_unstructured_text(text, {'source_type': 'press_release'})
        )
        
        # Convert to dict format for JSON serialization
        return [
            {
                'source_company': event.source_company,
                'target_company': event.target_company,
                'deal_type': event.deal_type,
                'deal_value': event.deal_value,
                'deal_date': event.deal_date,
                'description': event.description,
                'confidence_score': event.confidence_score,
                'extraction_metadata': event.extraction_metadata
            }
            for event in events
        ]
    finally:
        loop.close()

def process_social_media_chaos(posts: List[str]) -> List[Dict[str, Any]]:
    """
    Process chaotic social media posts and extract real M&A signals
    Demo function for HackMIT showing noise filtering
    """
    processor = UnstructuredTextProcessor()
    all_events = []
    
    import asyncio
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        for i, post in enumerate(posts):
            events = loop.run_until_complete(
                processor.process_unstructured_text(post, {
                    'source_type': 'social_media',
                    'post_index': i
                })
            )
            
            # Apply additional filtering for social media noise
            filtered_events = [
                event for event in events 
                if event.confidence_score > 0.4  # Higher threshold for social media
            ]
            
            all_events.extend(filtered_events)
        
        # Convert to dict format
        return [
            {
                'source_company': event.source_company,
                'target_company': event.target_company,
                'deal_type': event.deal_type,
                'deal_value': event.deal_value,
                'deal_date': event.deal_date,
                'description': event.description,
                'confidence_score': event.confidence_score,
                'extraction_metadata': event.extraction_metadata,
                'noise_filtered': True
            }
            for event in all_events
        ]
    finally:
        loop.close()
