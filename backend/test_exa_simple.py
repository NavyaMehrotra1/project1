#!/usr/bin/env python3
"""
Simple test script for Exa API integration
Tests core Exa functionality without dependencies on other services
"""

import asyncio
import os
import sys
from dotenv import load_dotenv

# Add the current directory to Python path
sys.path.append('.')

# Load environment variables
load_dotenv()

async def test_exa_basic():
    """Test basic Exa service functionality"""
    print("🔍 Testing Exa API Integration...")
    print("=" * 50)
    
    # Check API key
    api_key = os.getenv('EXA_API_KEY')
    if not api_key:
        print("❌ EXA_API_KEY not found in environment variables")
        return False
    
    print(f"✅ API Key found: {api_key[:10]}...")
    
    # Import and test Exa service
    try:
        from services.exa_service import ExaService
        print("✅ Exa service imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import Exa service: {e}")
        return False
    
    # Test single company enrichment
    test_companies = ["OpenAI", "Stripe", "Airbnb"]
    
    async with ExaService() as exa:
        print(f"\n📊 Testing single company enrichment...")
        
        for company in test_companies:
            print(f"\n🏢 Enriching: {company}")
            try:
                result = await exa.search_company(company, num_results=5)
                
                if "error" in result:
                    print(f"❌ Error: {result['error']}")
                    continue
                
                exa_data = result.get('exa_data', {})
                print(f"✅ Success!")
                print(f"   - Summary: {exa_data.get('summary', 'N/A')[:100]}...")
                print(f"   - News articles: {len(exa_data.get('news_articles', []))}")
                print(f"   - Key highlights: {len(exa_data.get('key_highlights', []))}")
                print(f"   - Data quality: {exa_data.get('data_quality', 'unknown')}")
                print(f"   - Has funding info: {exa_data.get('funding_info', {}).get('has_recent_funding', False)}")
                
                # Show first few highlights
                highlights = exa_data.get('key_highlights', [])
                if highlights:
                    print(f"   - Sample highlights:")
                    for i, highlight in enumerate(highlights[:3]):
                        print(f"     {i+1}. {highlight[:80]}...")
                
                break  # Test just one company to avoid rate limits
                
            except Exception as e:
                print(f"❌ Exception: {str(e)}")
                return False
    
    print(f"\n🎉 Basic Exa integration test completed successfully!")
    return True

async def test_api_endpoints():
    """Test API endpoints with curl commands"""
    print(f"\n🌐 API Endpoint Test Commands")
    print("=" * 50)
    print("To test the API endpoints, run these commands in another terminal:")
    print()
    print("1. Start the FastAPI server:")
    print("   cd backend && python main.py")
    print()
    print("2. Test health endpoint:")
    print("   curl http://localhost:8000/api/exa/health")
    print()
    print("3. Test company enrichment:")
    print("   curl -X POST http://localhost:8000/api/exa/enrich-company \\")
    print("        -H 'Content-Type: application/json' \\")
    print("        -d '{\"company_name\": \"OpenAI\", \"num_results\": 5}'")
    print()
    print("4. Test batch enrichment:")
    print("   curl -X POST http://localhost:8000/api/exa/enrich-batch \\")
    print("        -H 'Content-Type: application/json' \\")
    print("        -d '{\"companies\": [\"OpenAI\", \"Stripe\"]}'")

async def main():
    """Main test function"""
    print("🚀 DealFlow Exa Integration Test Suite")
    print("=" * 60)
    
    # Test basic Exa functionality
    success = await test_exa_basic()
    
    if success:
        # Show API endpoint tests
        await test_api_endpoints()
        
        print("\n" + "=" * 60)
        print("🎉 Test suite completed successfully!")
        print("\nNext steps:")
        print("1. Start the backend server: python main.py")
        print("2. Test the API endpoints using the curl commands above")
        print("3. Check the enhanced company profiles in the frontend")
    else:
        print("\n" + "=" * 60)
        print("❌ Test suite failed!")
        print("Please check your Exa API key and network connection")

if __name__ == "__main__":
    asyncio.run(main())
