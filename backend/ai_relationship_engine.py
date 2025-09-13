"""
AI-Powered Relationship Inference Engine
Implements intelligent relationship detection and link prediction algorithms
"""

import asyncio
import numpy as np
import pandas as pd
from typing import List, Dict, Any, Tuple, Set
from datetime import datetime, timedelta
import networkx as nx
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re
import json
from collections import defaultdict, Counter
import math

class RelationshipInferenceEngine:
    def __init__(self):
        self.graph = nx.Graph()  # Undirected graph
        self.company_embeddings = {}
        self.relationship_history = defaultdict(list)
        self.confidence_threshold = 0.6
        
        # Industry similarity matrix
        self.industry_similarities = {
            'Artificial Intelligence': ['Machine Learning', 'Data Analytics', 'Automation'],
            'Finance': ['Cryptocurrency', 'Banking', 'Insurance'],
            'Technology': ['Software', 'Hardware', 'Cloud Computing'],
            'Healthcare': ['Biotechnology', 'Medical Devices', 'Pharmaceuticals'],
            'E-commerce': ['Retail', 'Marketplace', 'Logistics'],
            'Social Media': ['Communication', 'Entertainment', 'Gaming'],
            'Transportation': ['Autonomous Vehicles', 'Logistics', 'Mobility']
        }
    
    def calculate_jaccard_similarity(self, company1_id: str, company2_id: str) -> float:
        """Calculate Jaccard similarity between two companies based on shared connections"""
        if not self.graph.has_node(company1_id) or not self.graph.has_node(company2_id):
            return 0.0
        
        neighbors1 = set(self.graph.neighbors(company1_id))
        neighbors2 = set(self.graph.neighbors(company2_id))
        
        if len(neighbors1) == 0 and len(neighbors2) == 0:
            return 0.0
        
        intersection = len(neighbors1.intersection(neighbors2))
        union = len(neighbors1.union(neighbors2))
        
        return intersection / union if union > 0 else 0.0
    
    def calculate_adamic_adar_index(self, company1_id: str, company2_id: str) -> float:
        """Calculate Adamic-Adar index for link prediction"""
        if not self.graph.has_node(company1_id) or not self.graph.has_node(company2_id):
            return 0.0
        
        neighbors1 = set(self.graph.neighbors(company1_id))
        neighbors2 = set(self.graph.neighbors(company2_id))
        common_neighbors = neighbors1.intersection(neighbors2)
        
        if len(common_neighbors) == 0:
            return 0.0
        
        score = 0.0
        for neighbor in common_neighbors:
            degree = self.graph.degree(neighbor)
            if degree > 1:
                score += 1.0 / math.log(degree)
        
        return score
    
    def calculate_industry_similarity(self, industry1: str, industry2: str) -> float:
        """Calculate similarity between industries"""
        if industry1 == industry2:
            return 1.0
        
        # Check if industries are in similar categories
        for main_industry, related in self.industry_similarities.items():
            if industry1 == main_industry and industry2 in related:
                return 0.8
            if industry2 == main_industry and industry1 in related:
                return 0.8
            if industry1 in related and industry2 in related:
                return 0.6
        
        return 0.1  # Default low similarity
    
    def calculate_market_cap_affinity(self, cap1: float, cap2: float) -> float:
        """Calculate affinity based on market cap similarity"""
        if not cap1 or not cap2:
            return 0.5
        
        ratio = min(cap1, cap2) / max(cap1, cap2)
        return ratio ** 0.5  # Square root to smooth the curve
    
    def infer_relationship_strength(self, company1: Dict, company2: Dict) -> Tuple[float, str, List[str]]:
        """
        Infer relationship strength between two companies
        Returns: (confidence_score, relationship_type, reasoning)
        """
        reasons = []
        base_score = 0.0
        
        # Industry similarity
        industry_sim = self.calculate_industry_similarity(
            company1.get('industry', ''), 
            company2.get('industry', '')
        )
        base_score += industry_sim * 0.3
        if industry_sim > 0.6:
            reasons.append(f"Similar industries: {company1.get('industry')} ↔ {company2.get('industry')}")
        
        # Market cap affinity
        cap_affinity = self.calculate_market_cap_affinity(
            company1.get('market_cap', 0),
            company2.get('market_cap', 0)
        )
        base_score += cap_affinity * 0.2
        if cap_affinity > 0.7:
            reasons.append("Similar market valuations suggest potential partnership tier")
        
        # Network-based similarities
        jaccard = self.calculate_jaccard_similarity(company1['id'], company2['id'])
        adamic_adar = self.calculate_adamic_adar_index(company1['id'], company2['id'])
        
        base_score += jaccard * 0.25
        base_score += min(adamic_adar / 10, 0.25)  # Normalize Adamic-Adar
        
        if jaccard > 0.3:
            reasons.append(f"Shared business connections (Jaccard: {jaccard:.2f})")
        if adamic_adar > 2:
            reasons.append(f"Strong network proximity (Adamic-Adar: {adamic_adar:.2f})")
        
        # Extraordinary score boost
        if company1.get('extraordinary_score', 0) > 0.8 and company2.get('extraordinary_score', 0) > 0.8:
            base_score += 0.15
            reasons.append("Both companies are market leaders")
        
        # Determine relationship type
        relationship_type = "partnership"
        if industry_sim > 0.8:
            if cap_affinity < 0.3:
                relationship_type = "acquisition"
                reasons.append("Large cap difference suggests acquisition potential")
            else:
                relationship_type = "merger"
                reasons.append("Similar size and industry suggests merger potential")
        elif industry_sim > 0.5:
            relationship_type = "strategic_alliance"
        elif base_score > 0.7:
            relationship_type = "investment"
        
        return min(base_score, 1.0), relationship_type, reasons
    
    def predict_missing_relationships(self, companies: List[Dict], max_predictions: int = 20) -> List[Dict]:
        """Predict missing relationships between companies"""
        predictions = []
        
        # Build current graph
        self.graph.clear()
        for company in companies:
            self.graph.add_node(company['id'], **company)
        
        # Generate all possible pairs
        for i, company1 in enumerate(companies):
            for j, company2 in enumerate(companies[i+1:], i+1):
                # Skip if relationship already exists
                if self.graph.has_edge(company1['id'], company2['id']):
                    continue
                
                confidence, rel_type, reasons = self.infer_relationship_strength(company1, company2)
                
                if confidence >= self.confidence_threshold:
                    predictions.append({
                        'source_company_id': company1['id'],
                        'target_company_id': company2['id'],
                        'source_company_name': company1['name'],
                        'target_company_name': company2['name'],
                        'relationship_type': rel_type,
                        'confidence_score': confidence,
                        'reasoning': reasons,
                        'predicted_date': datetime.now() + timedelta(days=np.random.randint(30, 365)),
                        'is_predicted': True
                    })
        
        # Sort by confidence and return top predictions
        predictions.sort(key=lambda x: x['confidence_score'], reverse=True)
        return predictions[:max_predictions]
    
    def simulate_relationship_impact(self, source_id: str, target_id: str, 
                                   companies: List[Dict]) -> Dict[str, Any]:
        """Simulate the impact of adding a relationship between two companies"""
        
        # Find the companies
        source_company = next((c for c in companies if c['id'] == source_id), None)
        target_company = next((c for c in companies if c['id'] == target_id), None)
        
        if not source_company or not target_company:
            return {"error": "Companies not found"}
        
        # Calculate direct impact
        confidence, rel_type, reasons = self.infer_relationship_strength(source_company, target_company)
        
        # Find affected companies (competitors and partners)
        affected_companies = []
        
        for company in companies:
            if company['id'] in [source_id, target_id]:
                continue
            
            # Check if this company would be affected
            source_sim = self.calculate_industry_similarity(
                company.get('industry', ''), 
                source_company.get('industry', '')
            )
            target_sim = self.calculate_industry_similarity(
                company.get('industry', ''), 
                target_company.get('industry', '')
            )
            
            if source_sim > 0.6 or target_sim > 0.6:
                impact_type = "competitive_pressure" if source_sim > 0.8 or target_sim > 0.8 else "market_shift"
                impact_strength = max(source_sim, target_sim)
                
                affected_companies.append({
                    'company_id': company['id'],
                    'company_name': company['name'],
                    'impact_type': impact_type,
                    'impact_strength': impact_strength,
                    'reasoning': f"Operates in similar space to {'both companies' if source_sim > 0.6 and target_sim > 0.6 else 'one of the companies'}"
                })
        
        # Sort by impact strength
        affected_companies.sort(key=lambda x: x['impact_strength'], reverse=True)
        
        return {
            'relationship': {
                'source': source_company['name'],
                'target': target_company['name'],
                'type': rel_type,
                'confidence': confidence,
                'reasoning': reasons
            },
            'market_impact': {
                'affected_companies': affected_companies[:10],  # Top 10 most affected
                'market_concentration': self._calculate_market_concentration(companies, source_id, target_id),
                'innovation_impact': self._assess_innovation_impact(source_company, target_company)
            },
            'timeline': {
                'immediate': "Market positioning adjustments",
                'short_term': "Competitive response strategies",
                'long_term': "Industry consolidation effects"
            }
        }
    
    def _calculate_market_concentration(self, companies: List[Dict], source_id: str, target_id: str) -> Dict:
        """Calculate market concentration impact"""
        source_company = next((c for c in companies if c['id'] == source_id), None)
        target_company = next((c for c in companies if c['id'] == target_id), None)
        
        if not source_company or not target_company:
            return {}
        
        # Calculate combined market cap
        combined_cap = (source_company.get('market_cap', 0) + target_company.get('market_cap', 0))
        
        # Find industry peers
        industry = source_company.get('industry', '')
        industry_companies = [c for c in companies if c.get('industry') == industry]
        total_industry_cap = sum(c.get('market_cap', 0) for c in industry_companies)
        
        concentration_ratio = combined_cap / total_industry_cap if total_industry_cap > 0 else 0
        
        return {
            'combined_market_cap': combined_cap,
            'industry_concentration_ratio': concentration_ratio,
            'market_dominance_level': 'high' if concentration_ratio > 0.3 else 'medium' if concentration_ratio > 0.15 else 'low'
        }
    
    def _assess_innovation_impact(self, company1: Dict, company2: Dict) -> Dict:
        """Assess potential innovation impact of relationship"""
        innovation_score = 0
        factors = []
        
        # AI/Tech companies have higher innovation potential
        tech_industries = ['Artificial Intelligence', 'Technology', 'Software', 'Data Analytics']
        
        if company1.get('industry') in tech_industries:
            innovation_score += 0.3
            factors.append(f"{company1['name']} operates in high-innovation sector")
        
        if company2.get('industry') in tech_industries:
            innovation_score += 0.3
            factors.append(f"{company2['name']} operates in high-innovation sector")
        
        # Extraordinary companies boost innovation
        if company1.get('extraordinary_score', 0) > 0.8:
            innovation_score += 0.2
            factors.append(f"{company1['name']} is a market leader")
        
        if company2.get('extraordinary_score', 0) > 0.8:
            innovation_score += 0.2
            factors.append(f"{company2['name']} is a market leader")
        
        return {
            'innovation_potential': min(innovation_score, 1.0),
            'impact_level': 'high' if innovation_score > 0.7 else 'medium' if innovation_score > 0.4 else 'low',
            'factors': factors
        }
    
    def add_temporal_decay(self, relationships: List[Dict], decay_rate: float = 0.1) -> List[Dict]:
        """Apply temporal decay to relationship confidence scores"""
        current_time = datetime.now()
        
        for relationship in relationships:
            if 'predicted_date' in relationship:
                days_old = (current_time - relationship['predicted_date']).days
                if days_old > 0:
                    decay_factor = math.exp(-decay_rate * days_old / 365)  # Yearly decay
                    relationship['confidence_score'] *= decay_factor
                    relationship['temporal_decay_applied'] = True
        
        return relationships

# Global instance
relationship_engine = RelationshipInferenceEngine()
