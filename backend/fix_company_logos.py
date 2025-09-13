#!/usr/bin/env python3
"""
Script to fix and improve company logos in graph_data_for_frontend.json
"""

import asyncio
import aiohttp
import json
import time
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ImprovedLogoScraper:
    def __init__(self):
        self.session = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            headers={
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
        )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def get_clearbit_logo(self, company_name: str) -> str:
        """Get logo from Clearbit Logo API"""
        
        # Try different domain variations
        domain_variations = [
            f"{company_name.lower().replace(' ', '').replace('.', '')}.com",
            f"{company_name.lower().replace(' ', '-').replace('.', '')}.com",
            f"{company_name.lower().replace(' ', '').replace('.', '')}.io",
            f"{company_name.lower().replace(' ', '-').replace('.', '')}.ai"
        ]
        
        for domain in domain_variations:
            try:
                clearbit_url = f"https://logo.clearbit.com/{domain}"
                async with self.session.get(clearbit_url) as response:
                    if response.status == 200:
                        # Check if it's actually an image (not a 404 page)
                        content_type = response.headers.get('content-type', '')
                        if 'image' in content_type:
                            logger.info(f"✅ Found Clearbit logo for {company_name}: {clearbit_url}")
                            return clearbit_url
            except Exception as e:
                continue
        
        return None
    
    async def get_logo_dev_logo(self, company_name: str) -> str:
        """Get logo from Logo.dev API"""
        
        domain_variations = [
            f"{company_name.lower().replace(' ', '').replace('.', '')}.com",
            f"{company_name.lower().replace(' ', '-').replace('.', '')}.com"
        ]
        
        for domain in domain_variations:
            try:
                logo_dev_url = f"https://img.logo.dev/{domain}?token=pk_X-1ZO13GSgeOoUrIuJ6GMQ"
                async with self.session.get(logo_dev_url) as response:
                    if response.status == 200:
                        content_type = response.headers.get('content-type', '')
                        if 'image' in content_type:
                            logger.info(f"✅ Found Logo.dev logo for {company_name}: {logo_dev_url}")
                            return logo_dev_url
            except Exception as e:
                continue
        
        return None
    
    async def get_brandfetch_logo(self, company_name: str) -> str:
        """Get logo from Brandfetch-style URLs"""
        
        domain_variations = [
            f"{company_name.lower().replace(' ', '').replace('.', '')}.com",
            f"{company_name.lower().replace(' ', '-').replace('.', '')}.com"
        ]
        
        for domain in domain_variations:
            try:
                # Try different Brandfetch-style URLs
                brandfetch_urls = [
                    f"https://asset.brandfetch.io/{domain}/logo",
                    f"https://asset.brandfetch.io/{domain}/icon"
                ]
                
                for url in brandfetch_urls:
                    async with self.session.get(url) as response:
                        if response.status == 200:
                            content_type = response.headers.get('content-type', '')
                            if 'image' in content_type:
                                logger.info(f"✅ Found Brandfetch logo for {company_name}: {url}")
                                return url
            except Exception as e:
                continue
        
        return None
    
    async def get_company_logo(self, company_name: str) -> str:
        """Get the best available logo for a company"""
        
        # Manual overrides for well-known companies with specific logo URLs
        manual_logos = {
            "Stripe": "https://images.ctfassets.net/fzn2n1nzq965/HTTOloNPhisV9P4hlMPNA/cacf1bb88b9fc492dfad34378d844280/Stripe_icon_-_square.svg",
            "OpenAI": "https://cdn.openai.com/API/logo-openai.svg",
            "Airbnb": "https://a0.muscache.com/airbnb/static/logos/belo-200.png",
            "Figma": "https://cdn.sanity.io/images/599r6htc/localized/46a76c802176eb17b04e12108de7e7e0f3736dc6-1024x1024.png?w=804&h=804&q=75&fit=max&auto=format",
            "Notion": "https://upload.wikimedia.org/wikipedia/commons/4/45/Notion_app_logo.png",
            "Discord": "https://assets-global.website-files.com/6257adef93867e50d84d30e2/636e0a6918e57475a843dcf5_icon_clyde_black_RGB.svg",
            "Dropbox": "https://cfl.dropboxstatic.com/static/images/logo_catalog/dropbox_logo_glyph_blue_m1@2x-vflJ5vCl4.png",
            "Reddit": "https://www.redditstatic.com/shreddit/assets/favicon/192x192.png",
            "Coinbase": "https://images.ctfassets.net/q5ulk4bp65r7/3TBS4oVkD1ghowTqVQJlqj/2dfd4ea3b623a7c0d8deb2ff445dee9e/Consumer_Wordmark.svg",
            "DoorDash": "https://cdn.doordash.com/media/consumer/home/landing/new/DoorDash_Logo_Red.svg",
            "Canva": "https://static.canva.com/web/images/12487a1e0770d29351bd4ce4f87ec8fe.svg",
            "GitLab": "https://about.gitlab.com/images/press/logo/svg/gitlab-logo-gray-rgb.svg",
            "Anthropic": "https://www.anthropic.com/_next/static/media/anthropic-logomark.d90c4ea4.svg",
            "Plaid": "https://plaid.com/assets/img/logo-plaid.svg"
        }
        
        if company_name in manual_logos:
            logger.info(f"✅ Using manual logo for {company_name}")
            return manual_logos[company_name]
        
        # Try different logo services
        logo_sources = [
            self.get_clearbit_logo,
            self.get_logo_dev_logo,
            self.get_brandfetch_logo
        ]
        
        for source in logo_sources:
            try:
                logo_url = await source(company_name)
                if logo_url:
                    return logo_url
                await asyncio.sleep(0.2)  # Small delay between attempts
            except Exception as e:
                continue
        
        logger.warning(f"❌ No logo found for {company_name}")
        return None

async def fix_company_logos():
    """Fix and improve company logos in graph data"""
    
    # Load graph data
    graph_data_path = Path(__file__).parent.parent / "data_agent" / "data_agent" / "output" / "graph_data_for_frontend.json"
    
    if not graph_data_path.exists():
        logger.error(f"Graph data file not found at {graph_data_path}")
        return
    
    logger.info(f"Loading graph data from {graph_data_path}")
    with open(graph_data_path, 'r') as f:
        graph_data = json.load(f)
    
    nodes = graph_data.get('nodes', [])
    logger.info(f"Found {len(nodes)} nodes in graph data")
    
    async with ImprovedLogoScraper() as scraper:
        updated_count = 0
        
        for node in nodes:
            data = node.get('data', {})
            company_name = data.get('name')
            current_logo = data.get('logo_url')
            
            if not company_name:
                continue
            
            # Skip if we already have a good logo (not the YC X logo)
            if current_logo and 'x-logo.svg' not in current_logo and 'favicon' not in current_logo:
                logger.info(f"⏭️ Skipping {company_name} - already has good logo")
                continue
            
            logger.info(f"🔍 Fixing logo for {company_name}")
            
            try:
                new_logo_url = await scraper.get_company_logo(company_name)
                
                if new_logo_url:
                    data['logo_url'] = new_logo_url
                    data['logo_updated'] = time.time()
                    data['logo_source'] = 'improved_scraper'
                    updated_count += 1
                    logger.info(f"✅ Updated logo for {company_name}")
                else:
                    logger.warning(f"❌ Could not find improved logo for {company_name}")
                
                await asyncio.sleep(0.5)  # Rate limiting
                
            except Exception as e:
                logger.error(f"Error processing {company_name}: {e}")
        
        # Save updated graph data
        logger.info(f"💾 Saving updated graph data with {updated_count} improved logos...")
        with open(graph_data_path, 'w') as f:
            json.dump(graph_data, f, indent=2)
        
        logger.info(f"✅ Successfully updated {updated_count} company logos")
        
        # Print summary
        companies_with_logos = []
        manual_logos = []
        for node in nodes:
            data = node.get('data', {})
            if data.get('logo_url') and data.get('name'):
                companies_with_logos.append(data['name'])
                if data.get('logo_source') == 'improved_scraper':
                    manual_logos.append(data['name'])
        
        logger.info(f"📊 Total companies with logos: {len(companies_with_logos)}")
        logger.info(f"🎨 Companies with improved logos: {len(manual_logos)}")

async def main():
    """Main function"""
    print("🚀 Starting Logo Improvement Process")
    print("=" * 50)
    
    try:
        await fix_company_logos()
        print("\n" + "=" * 50)
        print("✅ Logo improvement completed!")
        
    except Exception as e:
        print(f"\n❌ Logo improvement failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())
