import asyncio
import json
import os
from typing import Dict, List, Optional
from datetime import datetime
import logging

from .exa_service import ExaService
from .data_ingestion import load_yc_companies

logger = logging.getLogger(__name__)

class DataEnrichmentService:
    def __init__(self):
        self.cache_file = "data/enriched_companies.json"
        self.ensure_cache_directory()
    
    def ensure_cache_directory(self):
        """Ensure the data directory exists"""
        os.makedirs("data", exist_ok=True)
    
    def load_cached_data(self) -> Dict:
        """Load previously enriched data from cache"""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Error loading cached data: {e}")
        return {}
    
    def save_cached_data(self, data: Dict):
        """Save enriched data to cache"""
        try:
            with open(self.cache_file, 'w') as f:
                json.dump(data, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Error saving cached data: {e}")
    
    async def enrich_yc_dataset(self, force_refresh: bool = False) -> Dict:
        """Enrich the entire YC dataset with Exa data"""
        # Load existing YC companies
        yc_companies = load_yc_companies()
        if not yc_companies:
            logger.error("No YC companies found to enrich")
            return {}
        
        # Load cached data
        cached_data = self.load_cached_data() if not force_refresh else {}
        
        # Determine which companies need enrichment
        companies_to_enrich = []
        for company in yc_companies:
            company_name = company.get('name', '')
            if not company_name:
                continue
                
            # Check if we have recent data (less than 7 days old)
            if company_name in cached_data:
                last_updated = cached_data[company_name].get('last_updated')
                if last_updated and not force_refresh:
                    try:
                        last_update_date = datetime.fromisoformat(last_updated.replace('Z', '+00:00'))
                        days_old = (datetime.now() - last_update_date.replace(tzinfo=None)).days
                        if days_old < 7:  # Skip if data is less than 7 days old
                            continue
                    except:
                        pass
            
            companies_to_enrich.append(company_name)
        
        logger.info(f"Enriching {len(companies_to_enrich)} companies with Exa data")
        
        # Enrich companies in batches
        enriched_data = cached_data.copy()
        
        if companies_to_enrich:
            async with ExaService() as exa:
                batch_results = await exa.enrich_company_batch(companies_to_enrich)
                
                for company_name, result in batch_results.items():
                    if "error" not in result:
                        enriched_data[company_name] = result.get('exa_data', {})
                        enriched_data[company_name]['last_updated'] = datetime.now().isoformat()
                    else:
                        logger.warning(f"Failed to enrich {company_name}: {result['error']}")
        
        # Save updated cache
        self.save_cached_data(enriched_data)
        
        # Combine YC data with Exa enrichment
        enhanced_companies = []
        for company in yc_companies:
            company_name = company.get('name', '')
            enhanced_company = company.copy()
            
            if company_name in enriched_data:
                enhanced_company['exa_insights'] = enriched_data[company_name]
            
            enhanced_companies.append(enhanced_company)
        
        return {
            'companies': enhanced_companies,
            'total_companies': len(enhanced_companies),
            'enriched_count': len([c for c in enhanced_companies if 'exa_insights' in c]),
            'last_enrichment': datetime.now().isoformat()
        }
    
    async def get_company_full_profile(self, company_name: str) -> Dict:
        """Get complete company profile with YC + Exa data"""
        # Load YC data
        yc_companies = load_yc_companies()
        yc_company = next((c for c in yc_companies if c.get('name', '').lower() == company_name.lower()), None)
        
        # Load cached Exa data
        cached_data = self.load_cached_data()
        exa_data = cached_data.get(company_name, {})
        
        # If no cached data or data is old, fetch fresh data
        if not exa_data or self._is_data_stale(exa_data):
            async with ExaService() as exa:
                fresh_result = await exa.search_company(company_name)
                if "error" not in fresh_result:
                    exa_data = fresh_result.get('exa_data', {})
                    # Update cache
                    cached_data[company_name] = exa_data
                    self.save_cached_data(cached_data)
        
        # Combine data
        profile = {
            'company_name': company_name,
            'yc_data': yc_company or {},
            'exa_insights': exa_data,
            'profile_completeness': self._calculate_completeness(yc_company, exa_data),
            'last_updated': datetime.now().isoformat()
        }
        
        return profile
    
    def _is_data_stale(self, data: Dict, max_age_days: int = 7) -> bool:
        """Check if cached data is stale"""
        last_updated = data.get('last_updated')
        if not last_updated:
            return True
        
        try:
            last_update_date = datetime.fromisoformat(last_updated.replace('Z', '+00:00'))
            days_old = (datetime.now() - last_update_date.replace(tzinfo=None)).days
            return days_old >= max_age_days
        except:
            return True
    
    def _calculate_completeness(self, yc_data: Optional[Dict], exa_data: Dict) -> Dict:
        """Calculate profile completeness score"""
        score = 0
        max_score = 10
        
        # YC data completeness (5 points)
        if yc_data:
            if yc_data.get('description'): score += 1
            if yc_data.get('website'): score += 1
            if yc_data.get('batch'): score += 1
            if yc_data.get('founders'): score += 1
            if yc_data.get('location'): score += 1
        
        # Exa data completeness (5 points)
        if exa_data:
            if exa_data.get('summary'): score += 1
            if exa_data.get('news_articles'): score += 1
            if exa_data.get('key_highlights'): score += 1
            if exa_data.get('funding_info', {}).get('mentions'): score += 1
            if exa_data.get('data_quality') == 'high': score += 1
        
        return {
            'score': score,
            'max_score': max_score,
            'percentage': round((score / max_score) * 100, 1),
            'level': 'high' if score >= 8 else 'medium' if score >= 5 else 'low'
        }

# Global service instance
enrichment_service = DataEnrichmentService()
