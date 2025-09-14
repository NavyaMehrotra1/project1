"""
Dynamic Confidence Scoring Service for HackMIT
Replaces static confidence=1 with intelligent scoring based on data quality factors
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import re

logger = logging.getLogger(__name__)

@dataclass
class ConfidenceFactors:
    """Individual factors contributing to confidence score"""
    source_reliability: float = 0.0
    data_completeness: float = 0.0
    cross_validation: float = 0.0
    temporal_freshness: float = 0.0
    semantic_consistency: float = 0.0
    structural_quality: float = 0.0

class DynamicConfidenceService:
    """
    Calculates dynamic confidence scores based on multiple data quality factors
    Demonstrates sophisticated handling of uncertainty for HackMIT
    """
    
    def __init__(self):
        self.source_weights = {
            'sec.gov': 1.0,
            'reuters.com': 0.95,
            'bloomberg.com': 0.95,
            'wsj.com': 0.90,
            'forbes.com': 0.85,
            'techcrunch.com': 0.80,
            'crunchbase.com': 0.75,
            'twitter.com': 0.60,
            'reddit.com': 0.30,
            'exa_api': 0.70,
            'unknown': 0.50
        }
        
        # Required fields for different event types
        self.required_fields = {
            'merger_acquisition': ['source_company', 'target_company', 'deal_type', 'deal_date'],
            'partnership': ['source_company', 'target_company', 'deal_type'],
            'funding_round': ['target_company', 'deal_value', 'deal_date'],
            'default': ['source_company', 'target_company', 'deal_type']
        }
    
    def calculate_confidence(self, event: Dict[str, Any], 
                           related_events: Optional[List[Dict[str, Any]]] = None) -> float:
        """
        Calculate dynamic confidence score for an M&A event
        
        Args:
            event: The M&A event to score
            related_events: Other events that might validate this one
            
        Returns:
            Confidence score between 0.0 and 1.0
        """
        factors = self._analyze_confidence_factors(event, related_events or [])
        
        # Weighted combination of factors
        weights = {
            'source_reliability': 0.25,
            'data_completeness': 0.20,
            'cross_validation': 0.20,
            'temporal_freshness': 0.15,
            'semantic_consistency': 0.15,
            'structural_quality': 0.05
        }
        
        confidence = sum(
            getattr(factors, factor) * weight 
            for factor, weight in weights.items()
        )
        
        # Apply penalties and bonuses
        confidence = self._apply_confidence_adjustments(event, confidence, factors)
        
        # Clamp to valid range
        return max(0.1, min(1.0, confidence))
    
    def _analyze_confidence_factors(self, event: Dict[str, Any], 
                                  related_events: List[Dict[str, Any]]) -> ConfidenceFactors:
        """Analyze individual confidence factors"""
        factors = ConfidenceFactors()
        
        factors.source_reliability = self._assess_source_reliability(event)
        factors.data_completeness = self._assess_data_completeness(event)
        factors.cross_validation = self._assess_cross_validation(event, related_events)
        factors.temporal_freshness = self._assess_temporal_freshness(event)
        factors.semantic_consistency = self._assess_semantic_consistency(event)
        factors.structural_quality = self._assess_structural_quality(event)
        
        return factors
    
    def _assess_source_reliability(self, event: Dict[str, Any]) -> float:
        """Assess reliability of the data source"""
        source = self._extract_source_domain(event)
        base_reliability = self.source_weights.get(source, self.source_weights['unknown'])
        
        # Bonus for verified sources
        if self._is_verified_source(event):
            base_reliability = min(1.0, base_reliability + 0.1)
        
        # Penalty for suspicious patterns
        if self._has_suspicious_patterns(event):
            base_reliability *= 0.8
        
        return base_reliability
    
    def _assess_data_completeness(self, event: Dict[str, Any]) -> float:
        """Assess how complete the event data is"""
        deal_type = event.get('deal_type', 'default')
        required_fields = self.required_fields.get(deal_type, self.required_fields['default'])
        
        # Count present required fields
        present_fields = sum(1 for field in required_fields if event.get(field))
        completeness_ratio = present_fields / len(required_fields)
        
        # Bonus for additional valuable fields
        bonus_fields = ['deal_value', 'description', 'companies_mentioned', 'source_url']
        bonus_count = sum(1 for field in bonus_fields if event.get(field))
        bonus = min(0.2, bonus_count * 0.05)
        
        return min(1.0, completeness_ratio + bonus)
    
    def _assess_cross_validation(self, event: Dict[str, Any], 
                               related_events: List[Dict[str, Any]]) -> float:
        """Assess validation from other sources"""
        if not related_events:
            return 0.5  # Neutral score for single source
        
        # Count confirming sources
        confirming_sources = self._count_confirming_sources(event, related_events)
        
        if confirming_sources == 0:
            return 0.3  # Low confidence for unconfirmed events
        elif confirming_sources == 1:
            return 0.7  # Good confidence for one confirmation
        elif confirming_sources >= 2:
            return 0.95  # High confidence for multiple confirmations
        
        return 0.5
    
    def _assess_temporal_freshness(self, event: Dict[str, Any]) -> float:
        """Assess how recent/fresh the information is"""
        discovered_at = event.get('discovered_at')
        if not discovered_at:
            return 0.6  # Neutral score for unknown discovery time
        
        try:
            if isinstance(discovered_at, str):
                discovery_time = datetime.fromisoformat(discovered_at.replace('Z', '+00:00'))
            else:
                discovery_time = discovered_at
            
            hours_old = (datetime.now() - discovery_time.replace(tzinfo=None)).total_seconds() / 3600
            
            if hours_old < 1:
                return 1.0  # Very fresh
            elif hours_old < 24:
                return 0.9  # Fresh
            elif hours_old < 168:  # 1 week
                return 0.7  # Recent
            elif hours_old < 720:  # 1 month
                return 0.5  # Older
            else:
                return 0.3  # Stale
                
        except Exception:
            return 0.6  # Default for parsing errors
    
    def _assess_semantic_consistency(self, event: Dict[str, Any]) -> float:
        """Assess internal consistency of the event data"""
        consistency_score = 1.0
        
        # Check deal type consistency with description
        deal_type = event.get('deal_type', '')
        description = event.get('description', '').lower()
        
        if deal_type and description:
            type_keywords = {
                'merger': ['merger', 'merge', 'combining'],
                'acquisition': ['acquisition', 'acquire', 'bought', 'purchase'],
                'partnership': ['partnership', 'partner', 'collaborate'],
                'funding': ['funding', 'investment', 'raised', 'round']
            }
            
            expected_keywords = type_keywords.get(deal_type.lower(), [])
            if expected_keywords and not any(keyword in description for keyword in expected_keywords):
                consistency_score *= 0.8
        
        # Check company name consistency
        source_company = event.get('source_company', '')
        target_company = event.get('target_company', '')
        companies_mentioned = event.get('companies_mentioned', [])
        
        if source_company and target_company and companies_mentioned:
            mentioned_names = [name.lower() for name in companies_mentioned]
            if (source_company.lower() not in mentioned_names or 
                target_company.lower() not in mentioned_names):
                consistency_score *= 0.9
        
        # Check deal value reasonableness
        deal_value = event.get('deal_value')
        if deal_value:
            try:
                value = float(deal_value)
                if value < 0 or value > 1_000_000_000_000:  # $1T limit
                    consistency_score *= 0.7
            except (ValueError, TypeError):
                consistency_score *= 0.8
        
        return consistency_score
    
    def _assess_structural_quality(self, event: Dict[str, Any]) -> float:
        """Assess the structural quality of the data"""
        quality_score = 1.0
        
        # Check for proper data types
        expected_types = {
            'deal_value': (int, float, type(None)),
            'deal_date': (str, type(None)),
            'companies_mentioned': (list, type(None))
        }
        
        for field, expected_type in expected_types.items():
            if field in event and not isinstance(event[field], expected_type):
                quality_score *= 0.9
        
        # Check for suspicious characters or formatting
        text_fields = ['source_company', 'target_company', 'description']
        for field in text_fields:
            value = event.get(field, '')
            if isinstance(value, str):
                # Penalty for excessive special characters
                special_char_ratio = len(re.findall(r'[^a-zA-Z0-9\s\-\.]', value)) / max(1, len(value))
                if special_char_ratio > 0.3:
                    quality_score *= 0.8
                
                # Penalty for all caps (likely spam/low quality)
                if len(value) > 10 and value.isupper():
                    quality_score *= 0.7
        
        return quality_score
    
    def _apply_confidence_adjustments(self, event: Dict[str, Any], 
                                    base_confidence: float, 
                                    factors: ConfidenceFactors) -> float:
        """Apply final adjustments to confidence score"""
        adjusted_confidence = base_confidence
        
        # Bonus for high-value deals (likely to be well-documented)
        deal_value = event.get('deal_value')
        if deal_value:
            try:
                value = float(deal_value)
                if value > 1_000_000_000:  # $1B+
                    adjusted_confidence = min(1.0, adjusted_confidence + 0.05)
                elif value > 100_000_000:  # $100M+
                    adjusted_confidence = min(1.0, adjusted_confidence + 0.02)
            except (ValueError, TypeError):
                pass
        
        # Penalty for very low individual factors
        critical_factors = [factors.source_reliability, factors.data_completeness]
        if any(factor < 0.3 for factor in critical_factors):
            adjusted_confidence *= 0.8
        
        # Bonus for consistently high factors
        all_factors = [
            factors.source_reliability, factors.data_completeness,
            factors.cross_validation, factors.temporal_freshness,
            factors.semantic_consistency, factors.structural_quality
        ]
        if all(factor > 0.8 for factor in all_factors):
            adjusted_confidence = min(1.0, adjusted_confidence + 0.1)
        
        return adjusted_confidence
    
    def _extract_source_domain(self, event: Dict[str, Any]) -> str:
        """Extract domain from source information"""
        source_fields = ['source', 'source_url', 'url']
        
        for field in source_fields:
            source = event.get(field, '')
            if source:
                # Extract domain from URL
                if 'http' in source:
                    try:
                        from urllib.parse import urlparse
                        domain = urlparse(source).netloc.lower()
                        return domain
                    except:
                        pass
                
                # Direct domain match
                source_lower = source.lower()
                for domain in self.source_weights:
                    if domain in source_lower:
                        return domain
        
        return 'unknown'
    
    def _is_verified_source(self, event: Dict[str, Any]) -> bool:
        """Check if source has verification indicators"""
        source_info = str(event.get('source', '')).lower()
        url = str(event.get('source_url', '')).lower()
        
        verification_indicators = ['verified', 'official', 'press-release', 'sec.gov', 'investor-relations']
        
        return any(indicator in source_info or indicator in url for indicator in verification_indicators)
    
    def _has_suspicious_patterns(self, event: Dict[str, Any]) -> bool:
        """Detect suspicious patterns that might indicate low quality data"""
        # Check for spam-like patterns
        description = event.get('description', '')
        if isinstance(description, str):
            # Too many exclamation marks or caps
            if description.count('!') > 3 or len(re.findall(r'[A-Z]{5,}', description)) > 2:
                return True
            
            # Suspicious keywords
            spam_keywords = ['click here', 'limited time', 'act now', 'guaranteed']
            if any(keyword in description.lower() for keyword in spam_keywords):
                return True
        
        # Check for unrealistic deal values
        deal_value = event.get('deal_value')
        if deal_value:
            try:
                value = float(deal_value)
                # Suspiciously round numbers might be estimates
                if value > 1000000 and value % 1000000000 == 0:  # Exact billions
                    return True
            except (ValueError, TypeError):
                pass
        
        return False
    
    def _count_confirming_sources(self, event: Dict[str, Any], 
                                related_events: List[Dict[str, Any]]) -> int:
        """Count how many other sources confirm this event"""
        confirming_count = 0
        
        event_companies = set()
        if event.get('source_company'):
            event_companies.add(event.get('source_company', '').lower())
        if event.get('target_company'):
            event_companies.add(event.get('target_company', '').lower())
        event_companies.discard('')
        
        for related_event in related_events:
            related_companies = set()
            if related_event.get('source_company'):
                related_companies.add(related_event.get('source_company', '').lower())
            if related_event.get('target_company'):
                related_companies.add(related_event.get('target_company', '').lower())
            related_companies.discard('')
            
            # Check if events involve same companies
            if len(event_companies.intersection(related_companies)) >= 1:
                # Check if from different source
                event_source = self._extract_source_domain(event)
                related_source = self._extract_source_domain(related_event)
                
                if event_source != related_source:
                    confirming_count += 1
        
        return confirming_count
    
    def get_confidence_explanation(self, event: Dict[str, Any], 
                                 confidence_score: float,
                                 related_events: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """
        Generate human-readable explanation of confidence score
        Useful for debugging and transparency in HackMIT demo
        """
        factors = self._analyze_confidence_factors(event, related_events or [])
        
        explanation = {
            'overall_confidence': confidence_score,
            'factors': {
                'source_reliability': {
                    'score': factors.source_reliability,
                    'explanation': self._explain_source_reliability(event)
                },
                'data_completeness': {
                    'score': factors.data_completeness,
                    'explanation': self._explain_data_completeness(event)
                },
                'cross_validation': {
                    'score': factors.cross_validation,
                    'explanation': self._explain_cross_validation(event, related_events or [])
                },
                'temporal_freshness': {
                    'score': factors.temporal_freshness,
                    'explanation': self._explain_temporal_freshness(event)
                },
                'semantic_consistency': {
                    'score': factors.semantic_consistency,
                    'explanation': self._explain_semantic_consistency(event)
                },
                'structural_quality': {
                    'score': factors.structural_quality,
                    'explanation': self._explain_structural_quality(event)
                }
            },
            'recommendations': self._generate_recommendations(factors, event)
        }
        
        return explanation
    
    def _explain_source_reliability(self, event: Dict[str, Any]) -> str:
        """Generate explanation for source reliability score"""
        source = self._extract_source_domain(event)
        reliability = self.source_weights.get(source, self.source_weights['unknown'])
        
        if reliability >= 0.9:
            return f"High reliability source ({source}) - institutional/verified publisher"
        elif reliability >= 0.7:
            return f"Good reliability source ({source}) - established news outlet"
        elif reliability >= 0.5:
            return f"Moderate reliability source ({source}) - social media or aggregator"
        else:
            return f"Low reliability source ({source}) - unverified or unknown"
    
    def _explain_data_completeness(self, event: Dict[str, Any]) -> str:
        """Generate explanation for data completeness score"""
        deal_type = event.get('deal_type', 'default')
        required_fields = self.required_fields.get(deal_type, self.required_fields['default'])
        present_fields = sum(1 for field in required_fields if event.get(field))
        
        return f"Has {present_fields}/{len(required_fields)} required fields for {deal_type} events"
    
    def _explain_cross_validation(self, event: Dict[str, Any], related_events: List[Dict[str, Any]]) -> str:
        """Generate explanation for cross validation score"""
        confirming_count = self._count_confirming_sources(event, related_events)
        
        if confirming_count == 0:
            return "No confirming sources found - single source event"
        elif confirming_count == 1:
            return "One additional source confirms this event"
        else:
            return f"{confirming_count} additional sources confirm this event"
    
    def _explain_temporal_freshness(self, event: Dict[str, Any]) -> str:
        """Generate explanation for temporal freshness score"""
        discovered_at = event.get('discovered_at')
        if not discovered_at:
            return "Discovery time unknown"
        
        try:
            if isinstance(discovered_at, str):
                discovery_time = datetime.fromisoformat(discovered_at.replace('Z', '+00:00'))
            else:
                discovery_time = discovered_at
            
            hours_old = (datetime.now() - discovery_time.replace(tzinfo=None)).total_seconds() / 3600
            
            if hours_old < 1:
                return "Very fresh - discovered less than 1 hour ago"
            elif hours_old < 24:
                return f"Fresh - discovered {int(hours_old)} hours ago"
            elif hours_old < 168:
                return f"Recent - discovered {int(hours_old/24)} days ago"
            else:
                return f"Older - discovered {int(hours_old/168)} weeks ago"
        except:
            return "Could not parse discovery time"
    
    def _explain_semantic_consistency(self, event: Dict[str, Any]) -> str:
        """Generate explanation for semantic consistency score"""
        issues = []
        
        deal_type = event.get('deal_type', '')
        description = event.get('description', '').lower()
        
        if deal_type and description:
            type_keywords = {
                'merger': ['merger', 'merge', 'combining'],
                'acquisition': ['acquisition', 'acquire', 'bought', 'purchase'],
                'partnership': ['partnership', 'partner', 'collaborate'],
                'funding': ['funding', 'investment', 'raised', 'round']
            }
            
            expected_keywords = type_keywords.get(deal_type.lower(), [])
            if expected_keywords and not any(keyword in description for keyword in expected_keywords):
                issues.append("deal type doesn't match description")
        
        if not issues:
            return "Event data is internally consistent"
        else:
            return f"Consistency issues: {', '.join(issues)}"
    
    def _explain_structural_quality(self, event: Dict[str, Any]) -> str:
        """Generate explanation for structural quality score"""
        issues = []
        
        # Check deal value
        deal_value = event.get('deal_value')
        if deal_value:
            try:
                value = float(deal_value)
                if value < 0:
                    issues.append("negative deal value")
                elif value > 1_000_000_000_000:
                    issues.append("unrealistically high deal value")
            except (ValueError, TypeError):
                issues.append("invalid deal value format")
        
        if not issues:
            return "Data structure and formatting is good"
        else:
            return f"Structural issues: {', '.join(issues)}"
    
    def _generate_recommendations(self, factors: ConfidenceFactors, event: Dict[str, Any]) -> List[str]:
        """Generate recommendations for improving confidence"""
        recommendations = []
        
        if factors.source_reliability < 0.6:
            recommendations.append("Seek confirmation from more reliable sources")
        
        if factors.data_completeness < 0.7:
            recommendations.append("Gather additional required fields (deal value, date, etc.)")
        
        if factors.cross_validation < 0.5:
            recommendations.append("Look for confirming reports from other sources")
        
        if factors.temporal_freshness < 0.5:
            recommendations.append("Verify if this is recent news or historical data")
        
        if factors.semantic_consistency < 0.8:
            recommendations.append("Review event details for internal consistency")
        
        return recommendations

# Integration function for existing system
def update_events_with_dynamic_confidence(events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Update existing events with dynamic confidence scores
    Replaces static confidence=1 with intelligent scoring
    """
    confidence_service = DynamicConfidenceService()
    
    for i, event in enumerate(events):
        # Get related events for cross-validation
        related_events = [e for j, e in enumerate(events) if i != j]
        
        # Calculate dynamic confidence
        confidence_score = confidence_service.calculate_confidence(event, related_events)
        
        # Update event with new confidence score
        event['confidence_score'] = confidence_score
        
        # Add confidence explanation for debugging
        event['confidence_explanation'] = confidence_service.get_confidence_explanation(
            event, confidence_score, related_events
        )
    
    return events
