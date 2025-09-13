"""
Relationship Generator for YC Companies
Creates synthetic but realistic relationships between companies based on industry patterns,
business logic, and known connection types for robust graph visualization.
"""

import json
import random
from typing import List, Dict, Any, Tuple
from datetime import datetime, timedelta
import uuid

class YCRelationshipGenerator:
    def __init__(self):
        """Initialize the relationship generator with business logic patterns."""
        
        # Industry relationship patterns
        self.industry_relationships = {
            'Fintech': {
                'partners_with': ['E-commerce', 'SaaS', 'Marketplace'],
                'competes_with': ['Fintech'],
                'supplies_to': ['E-commerce', 'SaaS', 'Marketplace', 'Healthcare'],
                'integrates_with': ['DevTools', 'Analytics', 'Database']
            },
            'DevTools': {
                'partners_with': ['Cloud', 'Database', 'Analytics'],
                'competes_with': ['DevTools'],
                'supplies_to': ['SaaS', 'E-commerce', 'Fintech', 'AI'],
                'integrates_with': ['Database', 'Analytics', 'Infrastructure']
            },
            'AI': {
                'partners_with': ['DevTools', 'Analytics', 'Database'],
                'competes_with': ['AI'],
                'supplies_to': ['SaaS', 'E-commerce', 'Healthcare', 'Fintech'],
                'integrates_with': ['DevTools', 'Database', 'Analytics']
            },
            'E-commerce': {
                'partners_with': ['Fintech', 'Logistics', 'Marketing'],
                'competes_with': ['E-commerce', 'Marketplace'],
                'uses': ['Fintech', 'DevTools', 'Analytics'],
                'integrates_with': ['Fintech', 'Analytics', 'Marketing']
            },
            'SaaS': {
                'partners_with': ['DevTools', 'Analytics', 'Fintech'],
                'competes_with': ['SaaS'],
                'uses': ['DevTools', 'Database', 'Analytics'],
                'integrates_with': ['DevTools', 'Database', 'Analytics', 'Fintech']
            },
            'Healthcare': {
                'partners_with': ['AI', 'Analytics', 'Fintech'],
                'competes_with': ['Healthcare'],
                'uses': ['AI', 'DevTools', 'Analytics'],
                'integrates_with': ['AI', 'Analytics', 'Database']
            }
        }
        
        # Company size-based relationship patterns
        self.size_relationships = {
            'large_acquires_small': 0.3,  # 30% chance large company acquires smaller
            'large_invests_in_small': 0.4,  # 40% chance large company invests in smaller
            'similar_size_partnership': 0.6,  # 60% chance similar sized companies partner
            'similar_size_competition': 0.4   # 40% chance similar sized companies compete
        }
        
        # Known YC relationship patterns
        self.known_patterns = {
            'stripe_ecosystem': ['Retool', 'Linear', 'Vercel', 'PlanetScale'],
            'openai_ecosystem': ['Anthropic', 'Scale AI', 'Weights & Biases'],
            'airbnb_travel': ['TripActions', 'Gusto'],
            'coinbase_crypto': ['OpenSea', 'Alchemy'],
            'devtools_cluster': ['Vercel', 'PlanetScale', 'Railway', 'Render', 'Fly.io'],
            'fintech_cluster': ['Stripe', 'Brex', 'Mercury', 'Ramp'],
            'ai_cluster': ['OpenAI', 'Anthropic', 'Scale AI', 'Weights & Biases', 'Hugging Face']
        }
        
        print("🔗 YC Relationship Generator initialized")
        print("📊 Ready to generate synthetic relationships based on business patterns")
    
    def generate_relationships(self, companies: List[Dict[str, Any]], 
                             target_relationships: int = 150) -> List[Dict[str, Any]]:
        """
        Generate realistic relationships between YC companies.
        
        Args:
            companies: List of company dictionaries
            target_relationships: Target number of relationships to generate
            
        Returns:
            List of relationship dictionaries for graph edges
        """
        print(f"🎯 Generating {target_relationships} relationships for {len(companies)} companies...")
        
        relationships = []
        company_map = {comp['name']: comp for comp in companies}
        
        # 1. Generate known ecosystem relationships
        relationships.extend(self._generate_ecosystem_relationships(companies, company_map))
        
        # 2. Generate industry-based relationships
        relationships.extend(self._generate_industry_relationships(companies, company_map))
        
        # 3. Generate size-based relationships (acquisitions, investments)
        relationships.extend(self._generate_size_based_relationships(companies, company_map))
        
        # 4. Generate competitive relationships
        relationships.extend(self._generate_competitive_relationships(companies, company_map))
        
        # 5. Generate integration/partnership relationships
        relationships.extend(self._generate_integration_relationships(companies, company_map))
        
        # Limit to target number and remove duplicates
        unique_relationships = self._deduplicate_relationships(relationships)
        final_relationships = unique_relationships[:target_relationships]
        
        print(f"✅ Generated {len(final_relationships)} unique relationships")
        return final_relationships
    
    def _generate_ecosystem_relationships(self, companies: List[Dict], 
                                        company_map: Dict[str, Dict]) -> List[Dict]:
        """Generate relationships based on known YC ecosystems."""
        relationships = []
        
        for ecosystem_name, company_names in self.known_patterns.items():
            available_companies = [name for name in company_names if name in company_map]
            
            if len(available_companies) >= 2:
                # Create partnerships within ecosystem
                for i, company1 in enumerate(available_companies):
                    for company2 in available_companies[i+1:]:
                        if random.random() < 0.7:  # 70% chance of partnership
                            relationships.append(self._create_relationship(
                                company1, company2, 'partnership',
                                f"Strategic partnership within {ecosystem_name.replace('_', ' ')} ecosystem",
                                company_map
                            ))
        
        return relationships
    
    def _generate_industry_relationships(self, companies: List[Dict], 
                                       company_map: Dict[str, Dict]) -> List[Dict]:
        """Generate relationships based on industry patterns."""
        relationships = []
        
        # Group companies by industry
        industry_groups = {}
        for company in companies:
            industry = company.get('industry', 'Technology')
            if industry not in industry_groups:
                industry_groups[industry] = []
            industry_groups[industry].append(company['name'])
        
        # Generate cross-industry relationships
        for industry1, companies1 in industry_groups.items():
            if industry1 in self.industry_relationships:
                patterns = self.industry_relationships[industry1]
                
                for relationship_type, target_industries in patterns.items():
                    for target_industry in target_industries:
                        if target_industry in industry_groups:
                            companies2 = industry_groups[target_industry]
                            
                            # Create some relationships between these industries
                            for company1 in companies1[:3]:  # Limit to avoid too many
                                for company2 in companies2[:2]:
                                    if company1 != company2 and random.random() < 0.3:
                                        relationships.append(self._create_relationship(
                                            company1, company2, relationship_type,
                                            f"{industry1} {relationship_type.replace('_', ' ')} {target_industry}",
                                            company_map
                                        ))
        
        return relationships
    
    def _generate_size_based_relationships(self, companies: List[Dict], 
                                         company_map: Dict[str, Dict]) -> List[Dict]:
        """Generate acquisitions and investments based on company size."""
        relationships = []
        
        # Sort companies by valuation
        sorted_companies = sorted(companies, key=lambda x: x.get('valuation', 0), reverse=True)
        
        large_companies = sorted_companies[:20]  # Top 20 by valuation
        medium_companies = sorted_companies[20:50]  # Medium sized
        small_companies = sorted_companies[50:]  # Smaller companies
        
        # Large companies acquire/invest in smaller ones
        for large_comp in large_companies:
            # Acquisitions
            potential_targets = medium_companies + small_companies
            for target in random.sample(potential_targets, min(3, len(potential_targets))):
                if random.random() < 0.15:  # 15% chance of acquisition
                    deal_value = random.randint(100, 2000) * 1000000  # $100M - $2B
                    relationships.append(self._create_relationship(
                        large_comp['name'], target['name'], 'acquisition',
                        f"Strategic acquisition to expand market presence",
                        company_map, deal_value
                    ))
            
            # Investments
            for target in random.sample(small_companies, min(5, len(small_companies))):
                if random.random() < 0.25:  # 25% chance of investment
                    deal_value = random.randint(10, 500) * 1000000  # $10M - $500M
                    relationships.append(self._create_relationship(
                        large_comp['name'], target['name'], 'investment',
                        f"Strategic investment in emerging technology",
                        company_map, deal_value
                    ))
        
        return relationships
    
    def _generate_competitive_relationships(self, companies: List[Dict], 
                                          company_map: Dict[str, Dict]) -> List[Dict]:
        """Generate competitive relationships between similar companies."""
        relationships = []
        
        # Group by industry for competition
        industry_groups = {}
        for company in companies:
            industry = company.get('industry', 'Technology')
            if industry not in industry_groups:
                industry_groups[industry] = []
            industry_groups[industry].append(company)
        
        # Create competition within industries
        for industry, industry_companies in industry_groups.items():
            if len(industry_companies) >= 2:
                # Sort by valuation to find similar-sized competitors
                sorted_industry = sorted(industry_companies, key=lambda x: x.get('valuation', 0), reverse=True)
                
                for i, company1 in enumerate(sorted_industry):
                    # Compete with companies of similar size
                    for j in range(max(0, i-2), min(len(sorted_industry), i+3)):
                        if i != j and random.random() < 0.4:  # 40% chance of competition
                            company2 = sorted_industry[j]
                            relationships.append(self._create_relationship(
                                company1['name'], company2['name'], 'competition',
                                f"Direct competition in {industry} market",
                                company_map
                            ))
        
        return relationships
    
    def _generate_integration_relationships(self, companies: List[Dict], 
                                          company_map: Dict[str, Dict]) -> List[Dict]:
        """Generate integration and supplier relationships."""
        relationships = []
        
        # DevTools/Infrastructure companies integrate with others
        devtools_companies = [c for c in companies if c.get('industry') in ['DevTools', 'Infrastructure', 'Database', 'Analytics']]
        other_companies = [c for c in companies if c.get('industry') not in ['DevTools', 'Infrastructure', 'Database', 'Analytics']]
        
        for devtool in devtools_companies:
            # Each devtool integrates with several other companies
            targets = random.sample(other_companies, min(8, len(other_companies)))
            for target in targets:
                if random.random() < 0.3:  # 30% chance of integration
                    relationships.append(self._create_relationship(
                        devtool['name'], target['name'], 'integration',
                        f"Platform integration and API partnership",
                        company_map
                    ))
        
        return relationships
    
    def _create_relationship(self, company1: str, company2: str, relationship_type: str,
                           description: str, company_map: Dict[str, Dict], 
                           deal_value: float = None) -> Dict[str, Any]:
        """Create a relationship dictionary."""
        
        # Generate realistic date within last 2 years
        days_ago = random.randint(30, 730)
        deal_date = (datetime.now() - timedelta(days=days_ago)).strftime('%Y-%m-%d')
        
        return {
            'id': str(uuid.uuid4()),
            'source_company': company1,
            'target_company': company2,
            'deal_type': relationship_type,
            'deal_value': deal_value,
            'deal_date': deal_date,
            'description': description,
            'confidence_score': random.uniform(0.7, 0.95),
            'source': 'YC_Relationship_Generator',
            'companies_mentioned': [company1, company2]
        }
    
    def _deduplicate_relationships(self, relationships: List[Dict]) -> List[Dict]:
        """Remove duplicate relationships."""
        seen = set()
        unique_relationships = []
        
        for rel in relationships:
            # Create a key that treats (A,B) and (B,A) as the same for non-directional relationships
            if rel['deal_type'] in ['partnership', 'competition', 'integration']:
                key = tuple(sorted([rel['source_company'], rel['target_company']]) + [rel['deal_type']])
            else:
                key = (rel['source_company'], rel['target_company'], rel['deal_type'])
            
            if key not in seen:
                seen.add(key)
                unique_relationships.append(rel)
        
        return unique_relationships

def enhance_graph_with_relationships(companies: List[Dict], existing_deals: List[Dict] = None) -> List[Dict]:
    """
    Main function to enhance a company dataset with synthetic relationships.
    
    Args:
        companies: List of company dictionaries
        existing_deals: Existing deals to preserve
        
    Returns:
        Combined list of existing and synthetic deals
    """
    generator = YCRelationshipGenerator()
    
    # Generate synthetic relationships
    synthetic_relationships = generator.generate_relationships(companies, target_relationships=200)
    
    # Combine with existing deals
    all_deals = existing_deals or []
    all_deals.extend(synthetic_relationships)
    
    print(f"📊 Total relationships: {len(all_deals)} ({len(existing_deals or [])} real + {len(synthetic_relationships)} synthetic)")
    
    return all_deals

if __name__ == "__main__":
    # Test the relationship generator
    test_companies = [
        {"name": "Stripe", "industry": "Fintech", "valuation": 95000000000},
        {"name": "OpenAI", "industry": "AI", "valuation": 80000000000},
        {"name": "Airbnb", "industry": "Travel", "valuation": 75000000000},
        {"name": "Retool", "industry": "DevTools", "valuation": 3200000000},
        {"name": "Linear", "industry": "DevTools", "valuation": 400000000}
    ]
    
    relationships = enhance_graph_with_relationships(test_companies)
    print(f"Generated {len(relationships)} relationships for testing")
