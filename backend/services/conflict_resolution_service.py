"""
Multi-Source Conflict Resolution Service for HackMIT
Handles conflicting M&A data from multiple sources with intelligent resolution
"""

import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class SourceReliability(Enum):
    """Source reliability rankings for conflict resolution"""
    SEC_FILING = 1.0
    REUTERS = 0.95
    BLOOMBERG = 0.95
    WSJ = 0.90
    FORBES = 0.85
    TECHCRUNCH = 0.80
    TWITTER_VERIFIED = 0.60
    REDDIT = 0.30
    TWITTER_UNVERIFIED = 0.20
    UNKNOWN = 0.50

@dataclass
class ConflictingData:
    """Represents conflicting information from multiple sources"""
    field_name: str
    values: List[Tuple[Any, str, float]]  # (value, source, confidence)
    resolution_method: str
    resolved_value: Any
    confidence_score: float

class ConflictResolutionService:
    """
    Intelligent conflict resolution for messy M&A data
    Demonstrates real-world data handling capabilities for HackMIT
    """
    
    def __init__(self):
        self.source_reliability = self._initialize_source_weights()
        self.resolution_strategies = {
            'deal_value': self._resolve_financial_conflicts,
            'deal_date': self._resolve_temporal_conflicts,
            'company_names': self._resolve_entity_conflicts,
            'deal_type': self._resolve_categorical_conflicts,
            'description': self._resolve_narrative_conflicts
        }
    
    def _initialize_source_weights(self) -> Dict[str, float]:
        """Initialize source reliability weights"""
        return {
            'sec.gov': SourceReliability.SEC_FILING.value,
            'reuters.com': SourceReliability.REUTERS.value,
            'bloomberg.com': SourceReliability.BLOOMBERG.value,
            'wsj.com': SourceReliability.WSJ.value,
            'forbes.com': SourceReliability.FORBES.value,
            'techcrunch.com': SourceReliability.TECHCRUNCH.value,
            'twitter.com': SourceReliability.TWITTER_VERIFIED.value,
            'reddit.com': SourceReliability.REDDIT.value,
            'exa_api': SourceReliability.UNKNOWN.value
        }
    
    def resolve_conflicting_events(self, events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Main method to resolve conflicts between multiple M&A event reports
        
        Args:
            events: List of M&A events from different sources with potential conflicts
            
        Returns:
            Resolved event with confidence scores and conflict resolution metadata
        """
        if not events:
            return {}
        
        if len(events) == 1:
            return self._add_single_source_metadata(events[0])
        
        # Group events by similarity (same companies, similar timeframe)
        event_groups = self._group_similar_events(events)
        
        resolved_events = []
        for group in event_groups:
            resolved_event = self._resolve_event_group(group)
            resolved_events.append(resolved_event)
        
        # If multiple resolved events, pick the highest confidence one
        return max(resolved_events, key=lambda x: x.get('confidence_score', 0))
    
    def _group_similar_events(self, events: List[Dict[str, Any]]) -> List[List[Dict[str, Any]]]:
        """Group events that likely refer to the same M&A activity"""
        groups = []
        
        for event in events:
            placed = False
            for group in groups:
                if self._events_are_similar(event, group[0]):
                    group.append(event)
                    placed = True
                    break
            
            if not placed:
                groups.append([event])
        
        return groups
    
    def _events_are_similar(self, event1: Dict[str, Any], event2: Dict[str, Any]) -> bool:
        """Determine if two events likely refer to the same M&A activity"""
        # Check company name similarity
        companies1 = set([
            event1.get('source_company', '').lower(),
            event1.get('target_company', '').lower()
        ])
        companies2 = set([
            event2.get('source_company', '').lower(),
            event2.get('target_company', '').lower()
        ])
        
        company_overlap = len(companies1.intersection(companies2)) > 0
        
        # Check date proximity (within 30 days)
        date1 = self._parse_date(event1.get('deal_date'))
        date2 = self._parse_date(event2.get('deal_date'))
        
        date_proximity = False
        if date1 and date2:
            date_proximity = abs((date1 - date2).days) <= 30
        
        return company_overlap and (date_proximity or not date1 or not date2)
    
    def _resolve_event_group(self, events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Resolve conflicts within a group of similar events"""
        if len(events) == 1:
            return self._add_single_source_metadata(events[0])
        
        resolved_event = {}
        conflicts_detected = []
        
        # Resolve each field that might have conflicts
        for field in ['source_company', 'target_company', 'deal_value', 'deal_date', 'deal_type', 'description']:
            conflict_resolution = self._resolve_field_conflicts(events, field)
            
            if conflict_resolution:
                resolved_event[field] = conflict_resolution.resolved_value
                if len(conflict_resolution.values) > 1:
                    conflicts_detected.append(conflict_resolution)
        
        # Calculate overall confidence based on source reliability and conflict resolution
        confidence_score = self._calculate_overall_confidence(events, conflicts_detected)
        
        # Add metadata about the resolution process
        resolved_event.update({
            'confidence_score': confidence_score,
            'source_count': len(events),
            'conflicts_resolved': len(conflicts_detected),
            'resolution_metadata': {
                'sources': [self._extract_source_info(event) for event in events],
                'conflicts': [self._serialize_conflict(conflict) for conflict in conflicts_detected],
                'resolution_timestamp': datetime.now().isoformat(),
                'resolution_method': 'multi_source_intelligent_resolution'
            }
        })
        
        return resolved_event
    
    def _resolve_field_conflicts(self, events: List[Dict[str, Any]], field: str) -> Optional[ConflictingData]:
        """Resolve conflicts for a specific field across multiple events"""
        values_with_sources = []
        
        for event in events:
            if field in event and event[field] is not None:
                source = self._extract_source_name(event)
                source_weight = self._get_source_weight(source)
                values_with_sources.append((event[field], source, source_weight))
        
        if not values_with_sources:
            return None
        
        # If all values are the same, no conflict
        unique_values = set(val[0] for val in values_with_sources)
        if len(unique_values) <= 1:
            return ConflictingData(
                field_name=field,
                values=values_with_sources,
                resolution_method='no_conflict',
                resolved_value=values_with_sources[0][0],
                confidence_score=max(val[2] for val in values_with_sources)
            )
        
        # Apply field-specific resolution strategy
        if field in self.resolution_strategies:
            return self.resolution_strategies[field](values_with_sources, field)
        else:
            return self._resolve_by_source_weight(values_with_sources, field)
    
    def _resolve_financial_conflicts(self, values_with_sources: List[Tuple], field: str) -> ConflictingData:
        """Resolve conflicts in financial values (deal_value)"""
        # Convert to numbers and handle different formats
        numeric_values = []
        
        for value, source, weight in values_with_sources:
            try:
                # Handle various formats: "$2B", "2.5 billion", "2500000000"
                numeric_val = self._parse_financial_value(value)
                if numeric_val is not None:
                    numeric_values.append((numeric_val, source, weight))
            except:
                continue
        
        if not numeric_values:
            return self._resolve_by_source_weight(values_with_sources, field)
        
        # If values are within 10% of each other, take weighted average
        values_only = [val[0] for val in numeric_values]
        if max(values_only) / min(values_only) <= 1.1:  # Within 10%
            weighted_sum = sum(val * weight for val, _, weight in numeric_values)
            total_weight = sum(weight for _, _, weight in numeric_values)
            resolved_value = weighted_sum / total_weight
            
            return ConflictingData(
                field_name=field,
                values=values_with_sources,
                resolution_method='weighted_average',
                resolved_value=resolved_value,
                confidence_score=0.8  # High confidence for close values
            )
        
        # If values differ significantly, trust the most reliable source
        return self._resolve_by_source_weight(numeric_values, field)
    
    def _resolve_temporal_conflicts(self, values_with_sources: List[Tuple], field: str) -> ConflictingData:
        """Resolve conflicts in dates"""
        date_values = []
        
        for value, source, weight in values_with_sources:
            parsed_date = self._parse_date(value)
            if parsed_date:
                date_values.append((parsed_date, source, weight))
        
        if not date_values:
            return self._resolve_by_source_weight(values_with_sources, field)
        
        # If dates are within 7 days, take the most reliable source
        dates_only = [val[0] for val in date_values]
        date_range = max(dates_only) - min(dates_only)
        
        if date_range.days <= 7:
            # Close dates - trust most reliable source
            best_source = max(date_values, key=lambda x: x[2])
            return ConflictingData(
                field_name=field,
                values=values_with_sources,
                resolution_method='most_reliable_source_close_dates',
                resolved_value=best_source[0].strftime('%Y-%m-%d'),
                confidence_score=best_source[2]
            )
        
        # Dates differ significantly - flag for manual review but use most reliable
        return self._resolve_by_source_weight(date_values, field)
    
    def _resolve_entity_conflicts(self, values_with_sources: List[Tuple], field: str) -> ConflictingData:
        """Resolve conflicts in company names"""
        # Use fuzzy matching to identify similar names
        from difflib import SequenceMatcher
        
        # Group similar names
        name_groups = {}
        for value, source, weight in values_with_sources:
            best_match = None
            best_similarity = 0
            
            for existing_name in name_groups.keys():
                similarity = SequenceMatcher(None, value.lower(), existing_name.lower()).ratio()
                if similarity > best_similarity:
                    best_similarity = similarity
                    best_match = existing_name
            
            if best_similarity > 0.8:  # 80% similarity threshold
                name_groups[best_match].append((value, source, weight))
            else:
                name_groups[value] = [(value, source, weight)]
        
        # Pick the group with highest total weight
        best_group = max(name_groups.values(), key=lambda group: sum(w for _, _, w in group))
        
        # Within the best group, pick the most reliable source's version
        best_name = max(best_group, key=lambda x: x[2])
        
        return ConflictingData(
            field_name=field,
            values=values_with_sources,
            resolution_method='fuzzy_matching_with_source_weight',
            resolved_value=best_name[0],
            confidence_score=best_name[2] * 0.9  # Slight penalty for name conflicts
        )
    
    def _resolve_categorical_conflicts(self, values_with_sources: List[Tuple], field: str) -> ConflictingData:
        """Resolve conflicts in categorical fields like deal_type"""
        # Count occurrences weighted by source reliability
        weighted_counts = {}
        
        for value, source, weight in values_with_sources:
            if value not in weighted_counts:
                weighted_counts[value] = 0
            weighted_counts[value] += weight
        
        # Pick the category with highest weighted count
        best_category = max(weighted_counts.items(), key=lambda x: x[1])
        
        return ConflictingData(
            field_name=field,
            values=values_with_sources,
            resolution_method='weighted_voting',
            resolved_value=best_category[0],
            confidence_score=min(0.9, best_category[1] / sum(weighted_counts.values()))
        )
    
    def _resolve_narrative_conflicts(self, values_with_sources: List[Tuple], field: str) -> ConflictingData:
        """Resolve conflicts in narrative descriptions"""
        # For descriptions, combine information from multiple sources
        # Use the most reliable source as base, supplement with others
        
        sorted_by_reliability = sorted(values_with_sources, key=lambda x: x[2], reverse=True)
        primary_description = sorted_by_reliability[0][0]
        
        # TODO: Use LLM to intelligently merge descriptions
        # For now, use the most reliable source
        
        return ConflictingData(
            field_name=field,
            values=values_with_sources,
            resolution_method='most_reliable_source',
            resolved_value=primary_description,
            confidence_score=sorted_by_reliability[0][2]
        )
    
    def _resolve_by_source_weight(self, values_with_sources: List[Tuple], field: str) -> ConflictingData:
        """Default resolution: use the value from the most reliable source"""
        best_source = max(values_with_sources, key=lambda x: x[2])
        
        return ConflictingData(
            field_name=field,
            values=values_with_sources,
            resolution_method='most_reliable_source',
            resolved_value=best_source[0],
            confidence_score=best_source[2]
        )
    
    def _parse_financial_value(self, value: str) -> Optional[float]:
        """Parse various financial value formats"""
        if isinstance(value, (int, float)):
            return float(value)
        
        if not isinstance(value, str):
            return None
        
        # Remove common prefixes and suffixes
        value = value.replace('$', '').replace(',', '').strip().lower()
        
        # Handle billions/millions
        multiplier = 1
        if 'billion' in value or 'b' in value:
            multiplier = 1_000_000_000
            value = value.replace('billion', '').replace('b', '').strip()
        elif 'million' in value or 'm' in value:
            multiplier = 1_000_000
            value = value.replace('million', '').replace('m', '').strip()
        
        try:
            return float(value) * multiplier
        except ValueError:
            return None
    
    def _parse_date(self, date_str: Any) -> Optional[datetime]:
        """Parse various date formats"""
        if isinstance(date_str, datetime):
            return date_str
        
        if not isinstance(date_str, str):
            return None
        
        # Try common date formats
        formats = [
            '%Y-%m-%d',
            '%m/%d/%Y',
            '%d/%m/%Y',
            '%Y-%m-%d %H:%M:%S',
            '%B %d, %Y',
            '%b %d, %Y'
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        
        return None
    
    def _extract_source_name(self, event: Dict[str, Any]) -> str:
        """Extract source name from event for reliability weighting"""
        # Try various source fields
        for field in ['source', 'url', 'source_url', 'origin']:
            if field in event and event[field]:
                source = str(event[field]).lower()
                # Extract domain name
                if 'http' in source:
                    from urllib.parse import urlparse
                    return urlparse(source).netloc
                return source
        
        return 'unknown'
    
    def _get_source_weight(self, source: str) -> float:
        """Get reliability weight for a source"""
        source = source.lower()
        
        for known_source, weight in self.source_reliability.items():
            if known_source in source:
                return weight
        
        return SourceReliability.UNKNOWN.value
    
    def _calculate_overall_confidence(self, events: List[Dict[str, Any]], conflicts: List[ConflictingData]) -> float:
        """Calculate overall confidence score for resolved event"""
        # Base confidence on source reliability
        source_weights = [self._get_source_weight(self._extract_source_name(event)) for event in events]
        avg_source_reliability = sum(source_weights) / len(source_weights)
        
        # Penalty for conflicts
        conflict_penalty = len(conflicts) * 0.05  # 5% penalty per conflict
        
        # Bonus for multiple confirming sources
        source_bonus = min(0.2, (len(events) - 1) * 0.05)  # Up to 20% bonus
        
        confidence = avg_source_reliability + source_bonus - conflict_penalty
        return max(0.1, min(1.0, confidence))  # Clamp between 0.1 and 1.0
    
    def _add_single_source_metadata(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Add metadata for single-source events"""
        source = self._extract_source_name(event)
        source_weight = self._get_source_weight(source)
        
        event['confidence_score'] = source_weight
        event['source_count'] = 1
        event['conflicts_resolved'] = 0
        event['resolution_metadata'] = {
            'sources': [self._extract_source_info(event)],
            'conflicts': [],
            'resolution_timestamp': datetime.now().isoformat(),
            'resolution_method': 'single_source'
        }
        
        return event
    
    def _extract_source_info(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Extract source information for metadata"""
        source_name = self._extract_source_name(event)
        return {
            'name': source_name,
            'reliability_weight': self._get_source_weight(source_name),
            'url': event.get('source_url', event.get('url', '')),
            'timestamp': event.get('discovered_at', event.get('timestamp', datetime.now().isoformat()))
        }
    
    def _serialize_conflict(self, conflict: ConflictingData) -> Dict[str, Any]:
        """Serialize conflict data for JSON storage"""
        return {
            'field': conflict.field_name,
            'conflicting_values': [
                {'value': str(val), 'source': source, 'weight': weight}
                for val, source, weight in conflict.values
            ],
            'resolution_method': conflict.resolution_method,
            'resolved_value': str(conflict.resolved_value),
            'confidence': conflict.confidence_score
        }

# Utility functions for integration with existing system
def enhance_ma_events_with_conflict_resolution(events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Main integration function to enhance existing MA events with conflict resolution
    """
    resolver = ConflictResolutionService()
    
    # Group events by potential duplicates
    event_groups = {}
    
    for event in events:
        # Create a key based on companies and approximate date
        key = f"{event.get('source_company', '')}-{event.get('target_company', '')}"
        if key not in event_groups:
            event_groups[key] = []
        event_groups[key].append(event)
    
    resolved_events = []
    
    for group in event_groups.values():
        resolved_event = resolver.resolve_conflicting_events(group)
        if resolved_event:
            resolved_events.append(resolved_event)
    
    return resolved_events
