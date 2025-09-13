#!/usr/bin/env python3
"""
Test script for Extraordinary Research Service
Tests the research functionality and score calculation
"""

import asyncio
import json
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from services.extraordinary_research_service import ExtraordinaryResearchService

async def test_single_company_research():
    """Test researching a single company"""
    print("🔍 Testing single company research...")
    
    async with ExtraordinaryResearchService() as service:
        # Test with a well-known company
        company_name = "OpenAI"
        print(f"\nResearching: {company_name}")
        
        try:
            profile = await service.research_extraordinary_profile(company_name, "company")
            
            print(f"\n✅ Research completed for {profile.name}")
            print(f"📊 Extraordinary Score: {profile.extraordinary_score}/100")
            print(f"🏢 Type: {profile.type}")
            
            print(f"\n📈 Key Stats:")
            for stat in profile.key_stats[:3]:
                print(f"  • {stat}")
            
            print(f"\n🏆 Notable Achievements:")
            for achievement in profile.notable_achievements[:3]:
                print(f"  • {achievement}")
            
            print(f"\n🎖️ Awards & Recognition:")
            for award in profile.awards_recognitions[:3]:
                print(f"  • {award}")
            
            print(f"\n📰 Media Coverage:")
            for media in profile.media_coverage[:2]:
                print(f"  • {media}")
            
            print(f"\n💡 Innovation Highlights:")
            for innovation in profile.innovation_highlights[:2]:
                print(f"  • {innovation}")
            
            print(f"\n🎯 Competitive Advantages:")
            for advantage in profile.competitive_advantages[:2]:
                print(f"  • {advantage}")
            
            print(f"\n👥 Leadership Team:")
            for leader in profile.leadership_team[:2]:
                print(f"  • {leader}")
            
            print(f"\n💰 Funding History:")
            for funding in profile.funding_history[:2]:
                print(f"  • {funding}")
            
            print(f"\n📊 Detailed Metrics:")
            metrics = profile.metrics
            print(f"  • Valuation: {metrics.valuation}")
            print(f"  • Funding Raised: {metrics.funding_raised}")
            print(f"  • Employee Count: {metrics.employee_count}")
            print(f"  • Revenue: {metrics.revenue}")
            print(f"  • Unicorn Status: {metrics.unicorn_status}")
            print(f"  • IPO Status: {metrics.ipo_status}")
            print(f"  • Years in Business: {metrics.years_in_business}")
            print(f"  • Awards Count: {metrics.awards_count}")
            print(f"  • Media Mentions: {metrics.media_mentions}")
            
            return profile
            
        except Exception as e:
            print(f"❌ Error researching {company_name}: {e}")
            return None

async def test_batch_research():
    """Test batch research of multiple companies"""
    print("\n🔍 Testing batch company research...")
    
    companies = ["Stripe", "Figma", "Notion"]
    results = {}
    
    async with ExtraordinaryResearchService() as service:
        for company in companies:
            print(f"\nResearching: {company}")
            try:
                profile = await service.research_extraordinary_profile(company, "company")
                results[company] = {
                    "extraordinary_score": profile.extraordinary_score,
                    "key_stats": profile.key_stats[:2],
                    "notable_achievements": profile.notable_achievements[:2]
                }
                print(f"✅ {company}: Score {profile.extraordinary_score}/100")
                
                # Rate limiting
                await asyncio.sleep(2)
                
            except Exception as e:
                print(f"❌ Error with {company}: {e}")
                results[company] = {"error": str(e)}
    
    print(f"\n📊 Batch Research Results:")
    for company, data in results.items():
        if "error" not in data:
            print(f"  • {company}: {data['extraordinary_score']}/100")
        else:
            print(f"  • {company}: Error - {data['error']}")
    
    return results

async def test_score_calculation():
    """Test the score calculation logic"""
    print("\n🧮 Testing score calculation logic...")
    
    async with ExtraordinaryResearchService() as service:
        # Test with mock data
        test_data = """
        OpenAI is a leading artificial intelligence company valued at $80 billion.
        The company has raised over $11 billion in funding and employs more than 1,500 people.
        OpenAI is known for breakthrough innovations in AI including GPT models and ChatGPT.
        The company has received numerous awards for AI innovation and has significant market leadership.
        Founded by notable leaders including Sam Altman, the company has major industry impact.
        """
        
        metrics = await service._extract_metrics(test_data, "OpenAI")
        score = await service._calculate_extraordinary_score(metrics, test_data)
        
        print(f"📊 Test Metrics Extracted:")
        print(f"  • Valuation: {metrics.valuation}")
        print(f"  • Funding: {metrics.funding_raised}")
        print(f"  • Employees: {metrics.employee_count}")
        print(f"  • Unicorn: {metrics.unicorn_status}")
        print(f"  • Awards: {metrics.awards_count}")
        
        print(f"\n🎯 Calculated Score: {score}/100")
        
        return score

async def test_graph_data_update():
    """Test updating graph data with extraordinary scores"""
    print("\n📈 Testing graph data update...")
    
    try:
        import json
        from pathlib import Path
        
        # Load graph data
        graph_data_path = Path(__file__).parent.parent / "data_agent" / "data_agent" / "output" / "graph_data_for_frontend.json"
        
        if not graph_data_path.exists():
            print(f"❌ Graph data file not found at {graph_data_path}")
            return False
        
        with open(graph_data_path, 'r') as f:
            graph_data = json.load(f)
        
        nodes = graph_data.get('nodes', [])
        print(f"📊 Found {len(nodes)} nodes in graph data")
        
        # Test updating a few companies
        test_companies = []
        for node in nodes[:3]:  # Test first 3 companies
            company_name = node.get('data', {}).get('name')
            if company_name:
                test_companies.append(company_name)
        
        if not test_companies:
            print("❌ No companies found in graph data")
            return False
        
        print(f"🎯 Testing score updates for: {test_companies}")
        
        async with ExtraordinaryResearchService() as service:
            updated_count = 0
            for company_name in test_companies:
                try:
                    print(f"\nResearching {company_name}...")
                    profile = await service.research_extraordinary_profile(company_name, "company")
                    
                    # Find and update the node
                    node = next((n for n in nodes if n.get('data', {}).get('name') == company_name), None)
                    if node:
                        node['data']['extraordinary_score'] = profile.extraordinary_score
                        node['data']['extraordinary_metrics'] = {
                            'valuation': profile.metrics.valuation,
                            'funding_raised': profile.metrics.funding_raised,
                            'employee_count': profile.metrics.employee_count,
                            'unicorn_status': profile.metrics.unicorn_status,
                            'awards_count': profile.metrics.awards_count
                        }
                        
                        # Update visual properties
                        if profile.extraordinary_score >= 80:
                            node['color'] = '#ffd700'  # Gold
                        elif profile.extraordinary_score >= 60:
                            node['color'] = '#ff6b6b'  # Red
                        elif profile.extraordinary_score >= 40:
                            node['color'] = '#4ecdc4'  # Teal
                        
                        updated_count += 1
                        print(f"✅ Updated {company_name}: Score {profile.extraordinary_score}/100")
                    
                    await asyncio.sleep(2)  # Rate limiting
                    
                except Exception as e:
                    print(f"❌ Error updating {company_name}: {e}")
        
        print(f"\n📊 Successfully updated {updated_count}/{len(test_companies)} companies")
        return updated_count > 0
        
    except Exception as e:
        print(f"❌ Error in graph data update test: {e}")
        return False

async def main():
    """Run all tests"""
    print("🚀 Starting Extraordinary Research Service Tests")
    print("=" * 60)
    
    # Check if EXA_API_KEY is set
    if not os.getenv('EXA_API_KEY'):
        print("❌ EXA_API_KEY not found in environment variables")
        print("Please set EXA_API_KEY in backend/.env file")
        return
    
    try:
        # Test 1: Single company research
        profile = await test_single_company_research()
        
        # Test 2: Score calculation logic
        await test_score_calculation()
        
        # Test 3: Batch research
        await test_batch_research()
        
        # Test 4: Graph data update
        await test_graph_data_update()
        
        print("\n" + "=" * 60)
        print("✅ All tests completed!")
        
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())
