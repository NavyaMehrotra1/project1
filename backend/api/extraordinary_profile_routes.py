"""
Extraordinary Profile API Routes
Deep research profiles with articles, feats, recognitions, and stats
"""

from fastapi import APIRouter, HTTPException, Query, BackgroundTasks
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
import logging
import os

from models.extraordinary_profile import (
    ExtraordinaryProfile, ProfileGenerationRequest, 
    NotableArticle, Recognition, ExtraordinaryFeat, CompanyStats
)
from services.extraordinary_profile_service import ExtraordinaryProfileService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/extraordinary-profiles", tags=["extraordinary-profiles"])

# Global service instance
profile_service: Optional[ExtraordinaryProfileService] = None

def get_profile_service() -> ExtraordinaryProfileService:
    """Get or initialize profile service"""
    global profile_service
    
    if profile_service is None:
        exa_api_key = os.getenv("EXA_API_KEY")
        if not exa_api_key:
            logger.warning("EXA_API_KEY not found. Profile generation will be limited.")
        
        profile_service = ExtraordinaryProfileService(exa_api_key=exa_api_key)
    
    return profile_service

class ProfileResponse(BaseModel):
    profile: ExtraordinaryProfile
    generation_time_seconds: Optional[float] = None
    research_summary: Dict[str, Any] = {}

class ProfileListResponse(BaseModel):
    profiles: List[ExtraordinaryProfile]
    total_count: int
    average_score: float

class ProfileStatsResponse(BaseModel):
    total_profiles: int
    average_overall_score: float
    average_article_count: int
    average_recognition_count: int
    average_feat_count: int
    top_scoring_companies: List[Dict[str, Any]]

@router.post("/generate", response_model=ProfileResponse)
async def generate_profile(
    request: ProfileGenerationRequest,
    background_tasks: BackgroundTasks
):
    """
    Generate an extraordinary profile for a company with deep research
    """
    try:
        import time
        start_time = time.time()
        
        service = get_profile_service()
        profile = await service.generate_extraordinary_profile(request)
        
        generation_time = time.time() - start_time
        
        # Create research summary
        research_summary = {
            "queries_performed": len(profile.research_queries_performed),
            "sources_analyzed": profile.total_sources_analyzed,
            "articles_found": len(profile.notable_articles),
            "recognitions_found": len(profile.recognitions),
            "feats_identified": len(profile.extraordinary_feats),
            "research_depth_score": profile.research_depth_score,
            "data_completeness": profile.data_completeness_score
        }
        
        return ProfileResponse(
            profile=profile,
            generation_time_seconds=generation_time,
            research_summary=research_summary
        )
        
    except Exception as e:
        logger.error(f"Error generating profile: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/company/{company_id}", response_model=ProfileResponse)
async def get_company_profile(company_id: str):
    """
    Get existing extraordinary profile for a company
    """
    try:
        service = get_profile_service()
        profile = await service.load_profile(company_id)
        
        if not profile:
            raise HTTPException(
                status_code=404, 
                detail=f"Profile not found for company: {company_id}"
            )
        
        research_summary = {
            "last_updated": profile.last_updated.isoformat(),
            "articles_count": len(profile.notable_articles),
            "recognitions_count": len(profile.recognitions),
            "feats_count": len(profile.extraordinary_feats),
            "overall_score": profile.overall_profile_score
        }
        
        return ProfileResponse(
            profile=profile,
            research_summary=research_summary
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving profile: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=ProfileListResponse)
async def list_profiles(
    min_score: float = Query(0.0, description="Minimum profile score filter"),
    limit: int = Query(50, description="Maximum number of profiles to return"),
    sort_by: str = Query("score", description="Sort by: score, updated, company_name")
):
    """
    List all extraordinary profiles with filtering and sorting
    """
    try:
        service = get_profile_service()
        all_profiles = await service.get_all_profiles()
        
        # Filter by minimum score
        filtered_profiles = [p for p in all_profiles if p.overall_profile_score >= min_score]
        
        # Sort profiles
        if sort_by == "score":
            filtered_profiles.sort(key=lambda x: x.overall_profile_score, reverse=True)
        elif sort_by == "updated":
            filtered_profiles.sort(key=lambda x: x.last_updated, reverse=True)
        elif sort_by == "company_name":
            filtered_profiles.sort(key=lambda x: x.company_name.lower())
        
        # Apply limit
        limited_profiles = filtered_profiles[:limit]
        
        # Calculate average score
        avg_score = sum(p.overall_profile_score for p in filtered_profiles) / len(filtered_profiles) if filtered_profiles else 0.0
        
        return ProfileListResponse(
            profiles=limited_profiles,
            total_count=len(filtered_profiles),
            average_score=avg_score
        )
        
    except Exception as e:
        logger.error(f"Error listing profiles: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/search", response_model=ProfileListResponse)
async def search_profiles(
    q: str = Query(..., description="Search query"),
    min_score: float = Query(0.0, description="Minimum profile score"),
    limit: int = Query(20, description="Maximum results")
):
    """
    Search extraordinary profiles by company name, industry, or content
    """
    try:
        service = get_profile_service()
        profiles = await service.search_profiles(q, min_score)
        
        # Apply limit
        limited_profiles = profiles[:limit]
        
        avg_score = sum(p.overall_profile_score for p in profiles) / len(profiles) if profiles else 0.0
        
        return ProfileListResponse(
            profiles=limited_profiles,
            total_count=len(profiles),
            average_score=avg_score
        )
        
    except Exception as e:
        logger.error(f"Error searching profiles: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats", response_model=ProfileStatsResponse)
async def get_profile_stats():
    """
    Get comprehensive statistics about all extraordinary profiles
    """
    try:
        service = get_profile_service()
        all_profiles = await service.get_all_profiles()
        
        if not all_profiles:
            return ProfileStatsResponse(
                total_profiles=0,
                average_overall_score=0.0,
                average_article_count=0,
                average_recognition_count=0,
                average_feat_count=0,
                top_scoring_companies=[]
            )
        
        # Calculate statistics
        total_profiles = len(all_profiles)
        avg_score = sum(p.overall_profile_score for p in all_profiles) / total_profiles
        avg_articles = sum(len(p.notable_articles) for p in all_profiles) / total_profiles
        avg_recognitions = sum(len(p.recognitions) for p in all_profiles) / total_profiles
        avg_feats = sum(len(p.extraordinary_feats) for p in all_profiles) / total_profiles
        
        # Top scoring companies
        top_companies = sorted(all_profiles, key=lambda x: x.overall_profile_score, reverse=True)[:10]
        top_scoring = [
            {
                "company_name": p.company_name,
                "industry": p.industry,
                "overall_score": p.overall_profile_score,
                "articles_count": len(p.notable_articles),
                "recognitions_count": len(p.recognitions),
                "feats_count": len(p.extraordinary_feats)
            }
            for p in top_companies
        ]
        
        return ProfileStatsResponse(
            total_profiles=total_profiles,
            average_overall_score=avg_score,
            average_article_count=int(avg_articles),
            average_recognition_count=int(avg_recognitions),
            average_feat_count=int(avg_feats),
            top_scoring_companies=top_scoring
        )
        
    except Exception as e:
        logger.error(f"Error getting profile stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/batch-generate")
async def batch_generate_profiles(
    company_ids: List[str],
    background_tasks: BackgroundTasks,
    research_depth: str = "standard"
):
    """
    Generate extraordinary profiles for multiple companies in batch
    """
    try:
        service = get_profile_service()
        
        # Add batch generation task to background
        async def batch_process():
            results = []
            for company_id in company_ids:
                try:
                    # Load company data from graph
                    graph_data = await load_company_from_graph(company_id)
                    if graph_data:
                        request = ProfileGenerationRequest(
                            company_id=company_id,
                            company_name=graph_data.get('name', company_id),
                            industry=graph_data.get('industry'),
                            research_depth=research_depth
                        )
                        
                        profile = await service.generate_extraordinary_profile(request)
                        results.append({
                            "company_id": company_id,
                            "status": "success",
                            "profile_score": profile.overall_profile_score
                        })
                    else:
                        results.append({
                            "company_id": company_id,
                            "status": "error",
                            "error": "Company not found in graph data"
                        })
                        
                except Exception as e:
                    results.append({
                        "company_id": company_id,
                        "status": "error",
                        "error": str(e)
                    })
            
            logger.info(f"Batch generation completed: {len(results)} companies processed")
        
        background_tasks.add_task(batch_process)
        
        return {
            "message": f"Batch generation started for {len(company_ids)} companies",
            "company_ids": company_ids,
            "status": "processing"
        }
        
    except Exception as e:
        logger.error(f"Error starting batch generation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/company/{company_id}/refresh")
async def refresh_company_profile(
    company_id: str,
    force_regenerate: bool = Query(False, description="Force complete regeneration")
):
    """
    Refresh/update an existing company profile with latest data
    """
    try:
        service = get_profile_service()
        
        # Load existing profile
        existing_profile = await service.load_profile(company_id)
        if not existing_profile:
            raise HTTPException(
                status_code=404,
                detail=f"Profile not found for company: {company_id}"
            )
        
        # Create refresh request
        request = ProfileGenerationRequest(
            company_id=company_id,
            company_name=existing_profile.company_name,
            industry=existing_profile.industry,
            force_regenerate=force_regenerate,
            research_depth="standard"
        )
        
        # Update profile
        updated_profile = await service.generate_extraordinary_profile(request)
        
        return {
            "message": f"Profile refreshed for {existing_profile.company_name}",
            "company_id": company_id,
            "previous_score": existing_profile.overall_profile_score,
            "new_score": updated_profile.overall_profile_score,
            "improvement": updated_profile.overall_profile_score - existing_profile.overall_profile_score
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error refreshing profile: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/company/{company_id}/articles")
async def get_company_articles(company_id: str):
    """
    Get just the notable articles for a company
    """
    try:
        service = get_profile_service()
        profile = await service.load_profile(company_id)
        
        if not profile:
            raise HTTPException(
                status_code=404,
                detail=f"Profile not found for company: {company_id}"
            )
        
        return {
            "company_name": profile.company_name,
            "articles": profile.notable_articles,
            "total_articles": len(profile.notable_articles),
            "article_quality_score": profile.article_quality_score
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting articles: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/company/{company_id}/recognitions")
async def get_company_recognitions(company_id: str):
    """
    Get awards and recognitions for a company
    """
    try:
        service = get_profile_service()
        profile = await service.load_profile(company_id)
        
        if not profile:
            raise HTTPException(
                status_code=404,
                detail=f"Profile not found for company: {company_id}"
            )
        
        return {
            "company_name": profile.company_name,
            "recognitions": profile.recognitions,
            "total_recognitions": len(profile.recognitions),
            "recognition_prestige_score": profile.recognition_prestige_score
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting recognitions: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/company/{company_id}/feats")
async def get_company_feats(company_id: str):
    """
    Get extraordinary feats and achievements for a company
    """
    try:
        service = get_profile_service()
        profile = await service.load_profile(company_id)
        
        if not profile:
            raise HTTPException(
                status_code=404,
                detail=f"Profile not found for company: {company_id}"
            )
        
        return {
            "company_name": profile.company_name,
            "extraordinary_feats": profile.extraordinary_feats,
            "total_feats": len(profile.extraordinary_feats),
            "feat_impressiveness_score": profile.feat_impressiveness_score
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting feats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def load_company_from_graph(company_id: str) -> Optional[Dict[str, Any]]:
    """Helper function to load company data from graph"""
    try:
        import json
        from pathlib import Path
        
        graph_path = Path(__file__).parent.parent.parent / "data_agent" / "data_agent" / "output" / "graph_data_for_frontend.json"
        
        if graph_path.exists():
            with open(graph_path, 'r') as f:
                graph_data = json.load(f)
                
            for node in graph_data.get('nodes', []):
                if node.get('id') == company_id:
                    return node.get('data', {})
        
        return None
        
    except Exception as e:
        logger.error(f"Error loading company from graph: {e}")
        return None
