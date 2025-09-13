#!/usr/bin/env python3
"""
Script to update graph_data_for_frontend.json with extraordinary scores
"""

import asyncio
import json
import os
from pathlib import Path
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

from services.extraordinary_research_service import ExtraordinaryResearchService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def update_graph_with_extraordinary_scores():
    """Update graph data with extraordinary scores for all companies"""
    
    # Load graph data
    graph_data_path = Path(__file__).parent.parent / "data_agent" / "data_agent" / "output" / "graph_data_for_frontend.json"
    
    if not graph_data_path.exists():
        print(f"❌ Graph data file not found at {graph_data_path}")
        return
    
    print(f"📊 Loading graph data from {graph_data_path}")
    with open(graph_data_path, 'r') as f:
        graph_data = json.load(f)
    
    nodes = graph_data.get('nodes', [])
    print(f"Found {len(nodes)} nodes in graph data")
    
    # Extract company names
    companies = []
    for node in nodes:
        company_name = node.get('data', {}).get('name')
        if company_name and company_name not in companies:
            companies.append(company_name)
    
    print(f"Found {len(companies)} unique companies to research")
    
    # Process companies in batches
    batch_size = 5
    updated_count = 0
    
    async with ExtraordinaryResearchService() as service:
        for i in range(0, len(companies), batch_size):
            batch = companies[i:i + batch_size]
            print(f"\n🔍 Processing batch {i//batch_size + 1}: {batch}")
            
            for company_name in batch:
                try:
                    print(f"Researching {company_name}...")
                    
                    # Simple scoring based on company data
                    score = await calculate_simple_extraordinary_score(company_name, nodes)
                    
                    # Update all nodes with this company name
                    for node in nodes:
                        if node.get('data', {}).get('name') == company_name:
                            node['data']['extraordinary_score'] = score
                            node['data']['last_extraordinary_update'] = "2024-01-13T18:30:00"
                            
                            # Update visual properties based on score
                            if score >= 80:
                                node['color'] = '#ffd700'  # Gold for exceptional
                                node['size'] = max(node.get('size', 50), 80)
                            elif score >= 60:
                                node['color'] = '#ff6b6b'  # Red for high
                                node['size'] = max(node.get('size', 50), 70)
                            elif score >= 40:
                                node['color'] = '#4ecdc4'  # Teal for medium
                                node['size'] = max(node.get('size', 50), 60)
                            else:
                                node['color'] = '#95a5a6'  # Gray for standard
                                node['size'] = max(node.get('size', 50), 50)
                    
                    updated_count += 1
                    print(f"✅ Updated {company_name}: Score {score}/100")
                    
                except Exception as e:
                    print(f"❌ Error processing {company_name}: {e}")
                    
                # Rate limiting
                await asyncio.sleep(1)
    
    # Save updated graph data
    print(f"\n💾 Saving updated graph data...")
    with open(graph_data_path, 'w') as f:
        json.dump(graph_data, f, indent=2)
    
    print(f"✅ Successfully updated {updated_count}/{len(companies)} companies")
    print(f"📊 Graph data saved to {graph_data_path}")

async def calculate_simple_extraordinary_score(company_name: str, nodes: list) -> int:
    """Calculate a simple extraordinary score based on available data"""
    
    # Find the company node
    company_node = None
    for node in nodes:
        if node.get('data', {}).get('name') == company_name:
            company_node = node
            break
    
    if not company_node:
        return 20  # Default low score
    
    data = company_node.get('data', {})
    score = 0
    
    # Scoring based on available data
    
    # Valuation scoring (30 points max)
    valuation = data.get('valuation', '')
    if isinstance(valuation, str):
        if 'billion' in valuation.lower():
            try:
                val = float(valuation.lower().replace('billion', '').replace('$', '').strip())
                if val >= 100:
                    score += 30
                elif val >= 10:
                    score += 25
                elif val >= 1:
                    score += 20
                else:
                    score += 10
            except:
                score += 10
        elif 'million' in valuation.lower():
            score += 5
    
    # Industry scoring (20 points max)
    industry = data.get('industry', '').lower()
    high_value_industries = ['ai', 'artificial intelligence', 'fintech', 'biotech', 'saas', 'cloud']
    if any(keyword in industry for keyword in high_value_industries):
        score += 20
    elif industry:
        score += 10
    
    # Status scoring (20 points max)
    status = data.get('status', '').lower()
    if 'unicorn' in status:
        score += 20
    elif 'public' in status or 'ipo' in status:
        score += 15
    elif 'private' in status:
        score += 10
    
    # Batch scoring (10 points max)
    batch = data.get('batch', '')
    if batch:
        # YC companies get points
        score += 10
    
    # Founded year scoring (10 points max)
    founded = data.get('founded', 0)
    if founded:
        try:
            founded_year = int(founded)
            current_year = 2024
            age = current_year - founded_year
            if age >= 20:
                score += 10  # Established company
            elif age >= 10:
                score += 8
            elif age >= 5:
                score += 6
            else:
                score += 4  # Young company
        except:
            pass
    
    # Add some randomness for companies with known names
    well_known_companies = [
        'openai', 'stripe', 'figma', 'notion', 'airbnb', 'uber', 'spotify', 
        'dropbox', 'slack', 'zoom', 'tesla', 'spacex', 'palantir'
    ]
    
    if company_name.lower() in well_known_companies:
        score += 15
    
    # Cap at 100
    return min(score, 100)

async def main():
    """Main function"""
    print("🚀 Starting Graph Data Update with Extraordinary Scores")
    print("=" * 60)
    
    try:
        await update_graph_with_extraordinary_scores()
        print("\n" + "=" * 60)
        print("✅ Graph data update completed!")
        
    except Exception as e:
        print(f"\n❌ Update failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())
