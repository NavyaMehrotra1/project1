#!/usr/bin/env python3
"""
Test script for Exa API integration
Run this to verify the Exa service is working correctly
"""

import asyncio
import os
from dotenv import load_dotenv
from services.exa_service import ExaService
from services.data_enrichment import enrichment_service

# Load environment variables
load_dotenv()

async def test_exa_service():
    """Test basic Exa service functionality"""
    print("🔍 Testing Exa API Integration...")
    print("=" * 50)
    
    # Check API key
    api_key = os.getenv('EXA_API_KEY')
    if not api_key:
        print("❌ EXA_API_KEY not found in environment variables")
        print("Please add your Exa API key to the .env file")
        return False
    
    print(f"✅ API Key found: {api_key[:10]}...")
    
    # Test single company enrichment
    test_companies = ["OpenAI", "Anthropic", "Stripe"]
    
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
                
            except Exception as e:
                print(f"❌ Exception: {str(e)}")
    
    # Test batch enrichment
    print(f"\n📦 Testing batch enrichment...")
    try:
        async with ExaService() as exa:
            batch_results = await exa.enrich_company_batch(test_companies[:2])
            
            print(f"✅ Batch enrichment completed!")
            print(f"   - Companies processed: {len(batch_results)}")
            
            for company, result in batch_results.items():
                if "error" in result:
                    print(f"   - {company}: ❌ {result['error']}")
                else:
                    print(f"   - {company}: ✅ Success")
                    
    except Exception as e:
        print(f"❌ Batch enrichment failed: {str(e)}")
    
    return True

async def test_data_enrichment_service():
    """Test the data enrichment service"""
    print(f"\n🔧 Testing Data Enrichment Service...")
    print("=" * 50)
    
    try:
        # Test company profile retrieval
        test_company = "OpenAI"
        print(f"📋 Getting full profile for: {test_company}")
        
        profile = await enrichment_service.get_company_full_profile(test_company)
        
        print(f"✅ Profile retrieved!")
        print(f"   - Company name: {profile.get('company_name', 'N/A')}")
        print(f"   - Has YC data: {'yc_data' in profile and bool(profile['yc_data'])}")
        print(f"   - Has Exa insights: {'exa_insights' in profile and bool(profile['exa_insights'])}")
        
        completeness = profile.get('profile_completeness', {})
        if completeness:
            print(f"   - Completeness: {completeness.get('percentage', 0)}% ({completeness.get('level', 'unknown')})")
        
    except Exception as e:
        print(f"❌ Data enrichment service failed: {str(e)}")

def test_api_endpoints():
    """Test API endpoints (requires server to be running)"""
    print(f"\n🌐 API Endpoint Tests")
    print("=" * 50)
    print("To test API endpoints, run the following commands:")
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
    print("        -d '{\"companies\": [\"OpenAI\", \"Anthropic\"]}'")

async def main():
    """Main test function"""
    print("🚀 DealFlow Exa Integration Test Suite")
    print("=" * 60)
    
    # Test Exa service
    success = await test_exa_service()
    
    if success:
        # Test data enrichment service
        await test_data_enrichment_service()
    
    # Show API endpoint tests
    test_api_endpoints()
    
    print("\n" + "=" * 60)
    print("🎉 Test suite completed!")
    print("\nNext steps:")
    print("1. Add your EXA_API_KEY to backend/.env")
    print("2. Start the backend server: cd backend && python main.py")
    print("3. Test the frontend integration")
    print("4. Check the enhanced company profiles in the UI")

if __name__ == "__main__":
    asyncio.run(main())
