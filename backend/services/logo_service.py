import aiohttp
import asyncio
import re
from typing import Dict, List, Optional
from urllib.parse import urljoin, urlparse
import base64
from io import BytesIO
import logging

logger = logging.getLogger(__name__)

class LogoService:
    """Service to scrape and fetch company logos from various sources"""
    
    def __init__(self):
        self.session = None
        self.logo_apis = [
            "https://logo.clearbit.com/{domain}",
            "https://img.logo.dev/{domain}?token=pk_X-1ZO13GSgeOoUrIuJ6GMQ",  # Logo.dev API
            "https://api.brandfetch.io/v2/brands/{domain}",  # Brandfetch API
        ]
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=10),
            headers={'User-Agent': 'DealFlow-LogoService/1.0'}
        )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def extract_domain_from_company(self, company_name: str) -> str:
        """Extract likely domain from company name"""
        # Clean company name
        name = company_name.lower()
        name = re.sub(r'\b(inc|corp|corporation|ltd|llc|co|company)\b', '', name)
        name = re.sub(r'[^\w\s]', '', name)
        name = name.strip().replace(' ', '')
        
        # Common domain mappings
        domain_mappings = {
            'openai': 'openai.com',
            'microsoft': 'microsoft.com',
            'google': 'google.com',
            'alphabet': 'abc.xyz',
            'meta': 'meta.com',
            'facebook': 'meta.com',
            'anthropic': 'anthropic.com',
            'apple': 'apple.com',
            'amazon': 'amazon.com',
            'netflix': 'netflix.com',
            'tesla': 'tesla.com',
            'nvidia': 'nvidia.com',
            'salesforce': 'salesforce.com',
            'adobe': 'adobe.com',
            'oracle': 'oracle.com',
            'ibm': 'ibm.com',
            'intel': 'intel.com',
            'cisco': 'cisco.com',
            'vmware': 'vmware.com',
            'servicenow': 'servicenow.com',
            'zoom': 'zoom.us',
            'slack': 'slack.com',
            'stripe': 'stripe.com',
            'shopify': 'shopify.com',
            'square': 'squareup.com',
            'paypal': 'paypal.com',
            'uber': 'uber.com',
            'lyft': 'lyft.com',
            'airbnb': 'airbnb.com',
            'spotify': 'spotify.com',
            'twitter': 'x.com',
            'linkedin': 'linkedin.com',
            'snapchat': 'snap.com',
            'pinterest': 'pinterest.com',
            'reddit': 'reddit.com',
            'discord': 'discord.com',
            'twitch': 'twitch.tv',
            'dropbox': 'dropbox.com',
            'box': 'box.com',
            'atlassian': 'atlassian.com',
            'github': 'github.com',
            'gitlab': 'gitlab.com',
            'docker': 'docker.com',
            'mongodb': 'mongodb.com',
            'redis': 'redis.io',
            'elastic': 'elastic.co',
            'databricks': 'databricks.com',
            'snowflake': 'snowflake.com',
            'palantir': 'palantir.com',
            'cloudflare': 'cloudflare.com',
            'okta': 'okta.com',
            'crowdstrike': 'crowdstrike.com',
            'paloaltonetworks': 'paloaltonetworks.com',
            'fortinet': 'fortinet.com',
            'zscaler': 'zscaler.com'
        }
        
        return domain_mappings.get(name, f"{name}.com")
    
    async def fetch_logo_from_clearbit(self, domain: str) -> Optional[str]:
        """Fetch logo from Clearbit API"""
        try:
            url = f"https://logo.clearbit.com/{domain}"
            async with self.session.get(url) as response:
                if response.status == 200:
                    return url
        except Exception as e:
            logger.debug(f"Clearbit failed for {domain}: {e}")
        return None
    
    async def fetch_logo_from_logodev(self, domain: str) -> Optional[str]:
        """Fetch logo from Logo.dev API"""
        try:
            url = f"https://img.logo.dev/{domain}?token=pk_X-1ZO13GSgeOoUrIuJ6GMQ"
            async with self.session.get(url) as response:
                if response.status == 200:
                    return url
        except Exception as e:
            logger.debug(f"Logo.dev failed for {domain}: {e}")
        return None
    
    async def fetch_logo_from_brandfetch(self, domain: str) -> Optional[str]:
        """Fetch logo from Brandfetch API"""
        try:
            url = f"https://api.brandfetch.io/v2/brands/{domain}"
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    if 'logos' in data and data['logos']:
                        # Get the first logo format
                        logo = data['logos'][0]
                        if 'formats' in logo and logo['formats']:
                            return logo['formats'][0]['src']
        except Exception as e:
            logger.debug(f"Brandfetch failed for {domain}: {e}")
        return None
    
    async def fetch_favicon(self, domain: str) -> Optional[str]:
        """Fetch favicon as fallback"""
        try:
            favicon_urls = [
                f"https://{domain}/favicon.ico",
                f"https://www.{domain}/favicon.ico",
                f"https://{domain}/apple-touch-icon.png",
                f"https://www.{domain}/apple-touch-icon.png"
            ]
            
            for favicon_url in favicon_urls:
                try:
                    async with self.session.get(favicon_url) as response:
                        if response.status == 200:
                            return favicon_url
                except:
                    continue
        except Exception as e:
            logger.debug(f"Favicon failed for {domain}: {e}")
        return None
    
    async def get_company_logo(self, company_name: str, website: Optional[str] = None) -> Optional[str]:
        """Get logo URL for a company"""
        # Determine domain
        if website:
            parsed = urlparse(website)
            domain = parsed.netloc or parsed.path
            domain = domain.replace('www.', '')
        else:
            domain = self.extract_domain_from_company(company_name)
        
        # Try different logo sources
        logo_methods = [
            self.fetch_logo_from_clearbit,
            self.fetch_logo_from_logodev,
            self.fetch_logo_from_brandfetch,
            self.fetch_favicon
        ]
        
        for method in logo_methods:
            try:
                logo_url = await method(domain)
                if logo_url:
                    logger.info(f"Found logo for {company_name}: {logo_url}")
                    return logo_url
            except Exception as e:
                logger.debug(f"Logo method failed for {company_name}: {e}")
                continue
        
        logger.warning(f"No logo found for {company_name}")
        return None
    
    async def enrich_companies_with_logos(self, companies: List[Dict]) -> List[Dict]:
        """Enrich a list of companies with logo URLs"""
        enriched_companies = []
        
        # Process companies in batches to avoid overwhelming APIs
        batch_size = 5
        for i in range(0, len(companies), batch_size):
            batch = companies[i:i + batch_size]
            tasks = []
            
            for company in batch:
                task = self.get_company_logo(
                    company.get('name', ''),
                    company.get('website')
                )
                tasks.append(task)
            
            # Execute batch
            logo_urls = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Add logos to companies
            for j, company in enumerate(batch):
                company_copy = company.copy()
                logo_url = logo_urls[j]
                
                if isinstance(logo_url, str):
                    company_copy['logo_url'] = logo_url
                else:
                    company_copy['logo_url'] = None
                
                enriched_companies.append(company_copy)
            
            # Small delay between batches
            await asyncio.sleep(0.5)
        
        return enriched_companies

# Convenience function for single use
async def get_logos_for_companies(companies: List[Dict]) -> List[Dict]:
    """Convenience function to get logos for companies"""
    async with LogoService() as logo_service:
        return await logo_service.enrich_companies_with_logos(companies)
