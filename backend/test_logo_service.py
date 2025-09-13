#!/usr/bin/env python3
"""
Test script for the Logo Service to verify logo scraping functionality
"""

import asyncio
import json
from services.logo_service import LogoService

async def test_logo_service():
    """Test the logo service with sample companies"""
    
    # Sample companies to test
    test_companies = [
        {"id": "openai", "name": "OpenAI", "website": "https://openai.com"},
        {"id": "stripe", "name": "Stripe", "website": "https://stripe.com"},
        {"id": "airbnb", "name": "Airbnb", "website": "https://airbnb.com"},
        {"id": "microsoft", "name": "Microsoft Corporation", "website": "https://microsoft.com"},
        {"id": "google", "name": "Alphabet Inc.", "website": "https://google.com"},
        {"id": "meta", "name": "Meta Platforms", "website": "https://meta.com"},
        {"id": "anthropic", "name": "Anthropic", "website": "https://anthropic.com"},
        {"id": "apple", "name": "Apple Inc.", "website": "https://apple.com"},
        {"id": "tesla", "name": "Tesla", "website": "https://tesla.com"},
        {"id": "netflix", "name": "Netflix", "website": "https://netflix.com"}
    ]
    
    print("🔍 Testing Logo Service...")
    print("=" * 50)
    
    async with LogoService() as logo_service:
        # Test individual company logo fetching
        print("\n📋 Testing individual logo fetching:")
        for company in test_companies[:3]:  # Test first 3 companies
            print(f"\n🏢 Testing {company['name']}...")
            logo_url = await logo_service.get_company_logo(
                company['name'], 
                company.get('website')
            )
            
            if logo_url:
                print(f"   ✅ Logo found: {logo_url}")
            else:
                print(f"   ❌ No logo found")
        
        # Test batch enrichment
        print(f"\n📦 Testing batch enrichment for {len(test_companies)} companies...")
        enriched_companies = await logo_service.enrich_companies_with_logos(test_companies)
        
        print("\n📊 Results Summary:")
        print("-" * 30)
        
        logos_found = 0
        for company in enriched_companies:
            status = "✅" if company.get('logo_url') else "❌"
            print(f"{status} {company['name']:<20} | {company.get('logo_url', 'No logo')}")
            if company.get('logo_url'):
                logos_found += 1
        
        print(f"\n📈 Success Rate: {logos_found}/{len(test_companies)} ({logos_found/len(test_companies)*100:.1f}%)")
        
        # Save results to file
        with open('logo_test_results.json', 'w') as f:
            json.dump(enriched_companies, f, indent=2)
        
        print(f"\n💾 Results saved to 'logo_test_results.json'")
        
        return enriched_companies

async def test_api_endpoint():
    """Test the API endpoint for logo enrichment"""
    import aiohttp
    
    print("\n🌐 Testing API endpoint...")
    print("-" * 30)
    
    try:
        async with aiohttp.ClientSession() as session:
            # Test the companies-with-logos endpoint
            async with session.get('http://localhost:8000/api/companies-with-logos') as response:
                if response.status == 200:
                    data = await response.json()
                    companies = data.get('companies', [])
                    
                    print(f"✅ API endpoint working! Retrieved {len(companies)} companies")
                    
                    logos_count = sum(1 for c in companies if c.get('logo_url'))
                    print(f"📊 Companies with logos: {logos_count}/{len(companies)}")
                    
                    # Show first few companies with logos
                    print("\n🖼️  Sample companies with logos:")
                    for company in companies[:5]:
                        if company.get('logo_url'):
                            print(f"   • {company['name']}: {company['logo_url']}")
                
                else:
                    print(f"❌ API endpoint failed with status: {response.status}")
                    
    except Exception as e:
        print(f"❌ API test failed: {e}")
        print("   Make sure the backend server is running on localhost:8000")

if __name__ == "__main__":
    print("🚀 Logo Service Test Suite")
    print("=" * 50)
    
    # Run logo service tests
    asyncio.run(test_logo_service())
    
    # Run API endpoint tests
    asyncio.run(test_api_endpoint())
    
    print("\n✨ Test completed!")
