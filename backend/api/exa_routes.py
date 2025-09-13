from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List, Dict, Optional
import asyncio
from pydantic import BaseModel
import logging

from services.exa_service import ExaService, get_enhanced_company_data, enrich_yc_companies

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/exa", tags=["exa"])

class CompanyEnrichmentRequest(BaseModel):
    company_name: str
    include_domains: Optional[List[str]] = None
    num_results: Optional[int] = 10

class BatchEnrichmentRequest(BaseModel):
    companies: List[str]
    max_concurrent: Optional[int] = 5

class EnrichmentResponse(BaseModel):
    company_name: str
    exa_data: Dict
    status: str = "success"
    error: Optional[str] = None

@router.post("/enrich-company", response_model=EnrichmentResponse)
async def enrich_single_company(request: CompanyEnrichmentRequest):
    """Enrich a single company with Exa API data"""
    try:
        result = await get_enhanced_company_data(request.company_name)
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return EnrichmentResponse(
            company_name=request.company_name,
            exa_data=result.get("exa_data", {}),
            status="success"
        )
    
    except Exception as e:
        logger.error(f"Error enriching company {request.company_name}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/enrich-batch")
async def enrich_company_batch(request: BatchEnrichmentRequest):
    """Enrich multiple companies with Exa API data"""
    try:
        if len(request.companies) > 50:
            raise HTTPException(
                status_code=400, 
                detail="Maximum 50 companies allowed per batch request"
            )
        
        results = await enrich_yc_companies(request.companies)
        
        enriched_companies = []
        for company, data in results.items():
            if "error" in data:
                enriched_companies.append(
                    EnrichmentResponse(
                        company_name=company,
                        exa_data={},
                        status="error",
                        error=data["error"]
                    )
                )
            else:
                enriched_companies.append(
                    EnrichmentResponse(
                        company_name=company,
                        exa_data=data.get("exa_data", {}),
                        status="success"
                    )
                )
        
        return {
            "total_companies": len(request.companies),
            "successful": len([r for r in enriched_companies if r.status == "success"]),
            "failed": len([r for r in enriched_companies if r.status == "error"]),
            "results": enriched_companies
        }
    
    except Exception as e:
        logger.error(f"Error in batch enrichment: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/company/{company_name}")
async def get_company_insights(company_name: str):
    """Get cached or fresh Exa insights for a company"""
    try:
        # TODO: Add caching layer here
        result = await get_enhanced_company_data(company_name)
        
        if "error" in result:
            raise HTTPException(status_code=404, detail=f"No data found for {company_name}")
        
        return result
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting insights for {company_name}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health_check():
    """Health check endpoint for Exa service"""
    try:
        # Test Exa API connectivity
        async with ExaService() as exa:
            if not exa.api_key:
                return {
                    "status": "unhealthy",
                    "message": "EXA_API_KEY not configured"
                }
        
        return {
            "status": "healthy",
            "message": "Exa service is operational"
        }
    
    except Exception as e:
        return {
            "status": "unhealthy",
            "message": f"Exa service error: {str(e)}"
        }
