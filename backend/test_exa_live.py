#!/usr/bin/env python3
"""
Live test script to see what data Exa API is pulling
"""

import asyncio
import json
import sys
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.ma_intelligence_service import MAIntelligenceService

async def test_exa_live():
    """Test Exa API live and show exactly what data it returns"""
    
    print("🔍 Testing Exa API Live Data Retrieval")
    print("=" * 60)
    
    if not os.getenv('EXA_API_KEY'):
        print("❌ EXA_API_KEY not set in environment")
        return
    
    async with MAIntelligenceService() as service:
        print("✅ Connected to Exa API")
        print()
        
        # Test a single search query
        query = "merger acquisition startup tech company announced"
        print(f"🔎 Testing query: '{query}'")
        print("⏳ Searching...")
        
        # Make raw API call to see exact response
        headers = {
            "Authorization": f"Bearer {service.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "query": query,
            "type": "neural",
            "useAutoprompt": True,
            "numResults": 5,  # Just 5 for testing
            "contents": {
                "text": True,
                "highlights": True,
                "summary": True
            },
            "startPublishedDate": "2024-01-01T00:00:00.000Z",
            "category": "company"
        }
        
        try:
            async with service.session.post(
                f"{service.base_url}/search",
                headers=headers,
                json=payload
            ) as response:
                if response.status == 200:
                    raw_data = await response.json()
                    
                    print(f"✅ Found {len(raw_data.get('results', []))} results")
                    print()
                    
                    # Show raw API response structure
                    print("📋 RAW EXA API RESPONSE:")
                    print("-" * 40)
                    print(json.dumps(raw_data, indent=2)[:2000] + "..." if len(str(raw_data)) > 2000 else json.dumps(raw_data, indent=2))
                    print()
                    
                    # Process through our intelligence service
                    print("🧠 PROCESSED M&A EVENTS:")
                    print("-" * 40)
                    events = await service._process_search_results(raw_data, query)
                    
                    for i, event in enumerate(events, 1):
                        print(f"{i}. {event.title}")
                        print(f"   Type: {event.event_type.value}")
                        print(f"   Companies: {event.primary_company.name}", end="")
                        if event.secondary_company:
                            print(f" → {event.secondary_company.name}")
                        else:
                            print()
                        if event.deal_value:
                            print(f"   Deal Value: ${event.deal_value:,.0f}")
                        print(f"   Confidence: {event.confidence_score}")
                        print(f"   Source: {event.sources[0]['url'] if event.sources else 'N/A'}")
                        print()
                    
                    if not events:
                        print("   No M&A events extracted from results")
                        print("   (Results may not contain relevant M&A activity)")
                
                else:
                    error_text = await response.text()
                    print(f"❌ API Error: {response.status}")
                    print(f"Response: {error_text}")
                    
        except Exception as e:
            print(f"❌ Error: {e}")

async def test_full_monitoring_cycle():
    """Test a full monitoring cycle to see what the agent finds"""
    
    print("\n" + "=" * 60)
    print("🤖 Testing Full Monitoring Cycle")
    print("=" * 60)
    
    async with MAIntelligenceService() as service:
        # Search for events in the last 7 days
        events = await service.search_ma_events(time_range_hours=168)
        
        print(f"📊 MONITORING RESULTS:")
        print(f"   Total events found: {len(events)}")
        print()
        
        if events:
            print("🏆 TOP 5 EVENTS:")
            print("-" * 40)
            for i, event in enumerate(events[:5], 1):
                print(f"{i}. {event.title[:80]}...")
                print(f"   {event.primary_company.name} | {event.event_type.value}")
                if event.deal_value:
                    print(f"   💰 ${event.deal_value:,.0f}")
                print(f"   📅 {event.discovered_at.strftime('%Y-%m-%d %H:%M')}")
                print()
        else:
            print("   No M&A events found in recent timeframe")
            print("   Try expanding the search timeframe or checking API limits")

async def main():
    """Run all tests"""
    print("🚀 Exa API Live Testing")
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    await test_exa_live()
    await test_full_monitoring_cycle()
    
    print("\n" + "=" * 60)
    print("✅ Testing Complete!")

if __name__ == "__main__":
    asyncio.run(main())
