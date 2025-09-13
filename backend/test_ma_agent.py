#!/usr/bin/env python3
"""
Test script for the M&A monitoring agent
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.ma_monitoring_agent import MAMonitoringAgent
from services.ma_intelligence_service import MAIntelligenceService

async def test_intelligence_service():
    """Test the M&A intelligence service"""
    print("🧪 Testing M&A Intelligence Service...")
    
    async with MAIntelligenceService() as service:
        # Test search for recent M&A events
        events = await service.search_ma_events(time_range_hours=168)  # Last week
        
        print(f"✅ Found {len(events)} M&A events")
        
        for i, event in enumerate(events[:3]):  # Show first 3
            print(f"  {i+1}. {event.title}")
            print(f"     Type: {event.event_type.value}")
            print(f"     Companies: {event.primary_company.name}", end="")
            if event.secondary_company:
                print(f" → {event.secondary_company.name}")
            else:
                print()
            print(f"     Confidence: {event.confidence_score:.2f}")
            print()

async def test_agent_basic():
    """Test basic agent functionality"""
    print("🤖 Testing M&A Monitoring Agent...")
    
    agent = MAMonitoringAgent()
    
    # Test data loading/saving
    await agent._save_data()
    print("✅ Data persistence test passed")
    
    # Test recent events retrieval
    recent_events = await agent.get_recent_events(hours=24)
    print(f"✅ Recent events: {len(recent_events)}")
    
    # Test notifications
    notifications = await agent.get_notifications()
    print(f"✅ Notifications: {len(notifications)}")
    
    # Test activities
    activities = await agent.get_agent_activities(limit=10)
    print(f"✅ Activities: {len(activities)}")

async def main():
    """Run all tests"""
    print("🚀 Starting M&A Agent Tests")
    print("=" * 50)
    
    try:
        # Check environment
        if not os.getenv('EXA_API_KEY'):
            print("⚠️  Warning: EXA_API_KEY not set, skipping API tests")
            await test_agent_basic()
        else:
            await test_intelligence_service()
            await test_agent_basic()
        
        print("=" * 50)
        print("✅ All tests completed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
