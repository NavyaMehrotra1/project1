#!/usr/bin/env python3
"""
Script to scrape YC company logos and add them to graph_data_for_frontend.json
"""

import asyncio
import aiohttp
import json
import re
from pathlib import Path
from bs4 import BeautifulSoup
import logging
from urllib.parse import urljoin, urlparse
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class YCLogoScraper:
    def __init__(self):
        self.session = None
        self.yc_base_url = "https://www.ycombinator.com"
        self.company_logos = {}
        
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
    
    async def scrape_yc_companies_page(self):
        """Scrape the YC companies directory page"""
        
        companies_url = f"{self.yc_base_url}/companies"
        logger.info(f"Scraping YC companies from: {companies_url}")
        
        try:
            async with self.session.get(companies_url) as response:
                if response.status != 200:
                    logger.error(f"Failed to fetch YC companies page: {response.status}")
                    return {}
                
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                # Find company cards/listings
                company_cards = soup.find_all(['div', 'a'], class_=re.compile(r'company|card|item'))
                
                logos = {}
                
                for card in company_cards:
                    try:
                        # Look for company name and logo
                        name_elem = card.find(['h3', 'h4', 'span', 'div'], string=re.compile(r'^[A-Za-z0-9\s&.-]+$'))
                        img_elem = card.find('img')
                        
                        if name_elem and img_elem:
                            company_name = name_elem.get_text().strip()
                            logo_src = img_elem.get('src') or img_elem.get('data-src')
                            
                            if logo_src and company_name:
                                # Convert relative URLs to absolute
                                if logo_src.startswith('/'):
                                    logo_src = urljoin(self.yc_base_url, logo_src)
                                
                                logos[company_name] = logo_src
                                logger.info(f"Found logo for {company_name}: {logo_src}")
                    
                    except Exception as e:
                        continue
                
                logger.info(f"Scraped {len(logos)} company logos from YC directory")
                return logos
                
        except Exception as e:
            logger.error(f"Error scraping YC companies page: {e}")
            return {}
    
    async def search_yc_company_logo(self, company_name: str) -> str:
        """Search for a specific company's logo on YC website"""
        
        # Try different search approaches
        search_urls = [
            f"{self.yc_base_url}/companies/{company_name.lower().replace(' ', '-')}",
            f"{self.yc_base_url}/companies/{company_name.lower().replace(' ', '')}",
            f"{self.yc_base_url}/companies/{company_name.lower().replace(' ', '_')}",
        ]
        
        for url in search_urls:
            try:
                async with self.session.get(url) as response:
                    if response.status == 200:
                        html = await response.text()
                        soup = BeautifulSoup(html, 'html.parser')
                        
                        # Look for company logo
                        logo_selectors = [
                            'img[alt*="logo"]',
                            'img[src*="logo"]',
                            '.company-logo img',
                            '.logo img',
                            'img[class*="logo"]'
                        ]
                        
                        for selector in logo_selectors:
                            img = soup.select_one(selector)
                            if img:
                                src = img.get('src') or img.get('data-src')
                                if src:
                                    if src.startswith('/'):
                                        src = urljoin(self.yc_base_url, src)
                                    return src
                        
                        # Fallback: look for any image that might be a logo
                        images = soup.find_all('img')
                        for img in images:
                            src = img.get('src') or img.get('data-src')
                            alt = img.get('alt', '').lower()
                            
                            if src and (company_name.lower() in alt or 'logo' in alt):
                                if src.startswith('/'):
                                    src = urljoin(self.yc_base_url, src)
                                return src
                
                await asyncio.sleep(0.5)  # Rate limiting
                
            except Exception as e:
                logger.debug(f"Error checking {url}: {e}")
                continue
        
        return None
    
    async def get_alternative_logo_sources(self, company_name: str) -> str:
        """Get logo from alternative sources"""
        
        # Try Clearbit Logo API (free tier)
        clearbit_url = f"https://logo.clearbit.com/{company_name.lower().replace(' ', '')}.com"
        
        try:
            async with self.session.get(clearbit_url) as response:
                if response.status == 200:
                    return clearbit_url
        except:
            pass
        
        # Try Google Favicon API
        google_favicon_url = f"https://www.google.com/s2/favicons?domain={company_name.lower().replace(' ', '')}.com&sz=128"
        
        try:
            async with self.session.get(google_favicon_url) as response:
                if response.status == 200:
                    return google_favicon_url
        except:
            pass
        
        return None

async def update_graph_data_with_logos():
    """Update graph_data_for_frontend.json with YC company logos"""
    
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
    
    # Extract company names
    companies = []
    for node in nodes:
        company_name = node.get('data', {}).get('name')
        if company_name:
            companies.append(company_name)
    
    logger.info(f"Found {len(companies)} companies to find logos for")
    
    async with YCLogoScraper() as scraper:
        # First, try to scrape the main YC companies page
        yc_logos = await scraper.scrape_yc_companies_page()
        
        updated_count = 0
        
        # Process each company
        for company_name in companies:
            try:
                logo_url = None
                
                # Check if we found it in the YC directory scrape
                if company_name in yc_logos:
                    logo_url = yc_logos[company_name]
                    logger.info(f"✅ Found YC logo for {company_name}")
                else:
                    # Try individual company page search
                    logo_url = await scraper.search_yc_company_logo(company_name)
                    
                    if logo_url:
                        logger.info(f"✅ Found individual YC logo for {company_name}")
                    else:
                        # Try alternative sources
                        logo_url = await scraper.get_alternative_logo_sources(company_name)
                        if logo_url:
                            logger.info(f"✅ Found alternative logo for {company_name}")
                        else:
                            logger.warning(f"❌ No logo found for {company_name}")
                
                # Update all nodes with this company name
                if logo_url:
                    for node in nodes:
                        if node.get('data', {}).get('name') == company_name:
                            node['data']['logo_url'] = logo_url
                            node['data']['logo_updated'] = time.time()
                    
                    updated_count += 1
                
                # Rate limiting
                await asyncio.sleep(0.5)
                
            except Exception as e:
                logger.error(f"Error processing {company_name}: {e}")
        
        # Save updated graph data
        logger.info(f"💾 Saving updated graph data with {updated_count} logos...")
        with open(graph_data_path, 'w') as f:
            json.dump(graph_data, f, indent=2)
        
        logger.info(f"✅ Successfully updated {updated_count}/{len(companies)} companies with logos")
        
        # Print summary
        companies_with_logos = []
        for node in nodes:
            data = node.get('data', {})
            if data.get('logo_url') and data.get('name'):
                companies_with_logos.append(data['name'])
        
        logger.info(f"📊 Total companies with logos: {len(companies_with_logos)}")
        
        if companies_with_logos:
            logger.info("🎨 Companies with logos:")
            for company in companies_with_logos[:10]:  # Show first 10
                logger.info(f"   • {company}")
            if len(companies_with_logos) > 10:
                logger.info(f"   ... and {len(companies_with_logos) - 10} more")

async def main():
    """Main function"""
    print("🚀 Starting YC Logo Scraping")
    print("=" * 50)
    
    try:
        await update_graph_data_with_logos()
        print("\n" + "=" * 50)
        print("✅ YC logo scraping completed!")
        
    except Exception as e:
        print(f"\n❌ Logo scraping failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())
