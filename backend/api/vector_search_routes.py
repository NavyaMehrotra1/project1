"""
Vector Search API Routes
Provides semantic search endpoints using the vector database
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
import logging

from services.vector_database_service import VectorDatabaseService, load_vector_db
from services.vector_db_integration_service import get_vector_db_integration

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/vector-search", tags=["vector-search"])

# Global vector database instance
vector_db: Optional[VectorDatabaseService] = None

class SearchRequest(BaseModel):
    query: str
    k: int = 5
    filter_type: Optional[str] = None

class SearchResponse(BaseModel):
    results: List[Dict[str, Any]]
    query: str
    total_results: int
    search_type: str

class SimilarCompaniesRequest(BaseModel):
    company_name: str
    k: int = 5

def get_vector_db() -> VectorDatabaseService:
    """Get or initialize vector database"""
    global vector_db
    
    if vector_db is None:
        # Try to load existing database first
        vector_db = load_vector_db("./chroma_db")
        
        if vector_db is None:
            # Create new database from graph data
            from services.vector_database_service import create_vector_db_from_graph
            graph_path = "../data_agent/data_agent/output/graph_data_for_frontend.json"
            vector_db = create_vector_db_from_graph(graph_path, "./chroma_db")
            
            if vector_db is None:
                raise HTTPException(
                    status_code=500, 
                    detail="Failed to initialize vector database"
                )
    
    return vector_db

@router.post("/search", response_model=SearchResponse)
async def semantic_search(request: SearchRequest):
    """
    Perform semantic search across companies and relationships
    """
    try:
        db = get_vector_db()
        results = db.semantic_search(
            query=request.query,
            k=request.k,
            filter_type=request.filter_type
        )
        
        return SearchResponse(
            results=results,
            query=request.query,
            total_results=len(results),
            search_type=request.filter_type or "all"
        )
        
    except Exception as e:
        logger.error(f"Error in semantic search: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/search")
async def semantic_search_get(
    q: str = Query(..., description="Search query"),
    k: int = Query(5, description="Number of results to return"),
    type: Optional[str] = Query(None, description="Filter by type: 'company' or 'relationship'")
):
    """
    GET endpoint for semantic search
    """
    try:
        db = get_vector_db()
        results = db.semantic_search(query=q, k=k, filter_type=type)
        
        return {
            "results": results,
            "query": q,
            "total_results": len(results),
            "search_type": type or "all"
        }
        
    except Exception as e:
        logger.error(f"Error in semantic search: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/companies/search", response_model=SearchResponse)
async def search_companies(request: SearchRequest):
    """
    Search specifically for companies
    """
    try:
        db = get_vector_db()
        results = db.search_companies(query=request.query, k=request.k)
        
        return SearchResponse(
            results=results,
            query=request.query,
            total_results=len(results),
            search_type="company"
        )
        
    except Exception as e:
        logger.error(f"Error searching companies: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/relationships/search", response_model=SearchResponse)
async def search_relationships(request: SearchRequest):
    """
    Search specifically for relationships
    """
    try:
        db = get_vector_db()
        results = db.search_relationships(query=request.query, k=request.k)
        
        return SearchResponse(
            results=results,
            query=request.query,
            total_results=len(results),
            search_type="relationship"
        )
        
    except Exception as e:
        logger.error(f"Error searching relationships: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/companies/similar")
async def find_similar_companies(request: SimilarCompaniesRequest):
    """
    Find companies similar to a given company
    """
    try:
        db = get_vector_db()
        results = db.get_similar_companies(
            company_name=request.company_name,
            k=request.k
        )
        
        return {
            "similar_companies": results,
            "reference_company": request.company_name,
            "total_results": len(results)
        }
        
    except Exception as e:
        logger.error(f"Error finding similar companies: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/companies/similar/{company_name}")
async def find_similar_companies_get(
    company_name: str,
    k: int = Query(5, description="Number of similar companies to return")
):
    """
    GET endpoint to find companies similar to a given company
    """
    try:
        db = get_vector_db()
        results = db.get_similar_companies(company_name=company_name, k=k)
        
        return {
            "similar_companies": results,
            "reference_company": company_name,
            "total_results": len(results)
        }
        
    except Exception as e:
        logger.error(f"Error finding similar companies: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats")
async def get_database_stats():
    """
    Get statistics about the vector database
    """
    try:
        db = get_vector_db()
        stats = db.get_database_stats()
        return stats
        
    except Exception as e:
        logger.error(f"Error getting database stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/rebuild")
async def rebuild_database():
    """
    Rebuild the vector database from the latest graph data
    """
    try:
        global vector_db
        
        from services.vector_database_service import create_vector_db_from_graph
        graph_path = "../data_agent/data_agent/output/graph_data_for_frontend.json"
        
        # Create new database
        new_db = create_vector_db_from_graph(graph_path, "./chroma_db")
        
        if new_db is None:
            raise HTTPException(
                status_code=500,
                detail="Failed to rebuild vector database"
            )
        
        # Update global instance
        vector_db = new_db
        
        stats = vector_db.get_database_stats()
        
        return {
            "message": "Vector database rebuilt successfully",
            "stats": stats
        }
        
    except Exception as e:
        logger.error(f"Error rebuilding database: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Example queries for testing
@router.post("/ma-events/search", response_model=SearchResponse)
async def search_ma_events(request: SearchRequest):
    """
    Search specifically for M&A events
    """
    try:
        db = get_vector_db()
        results = db.search_ma_events(query=request.query, k=request.k)
        
        return SearchResponse(
            results=results,
            query=request.query,
            total_results=len(results),
            search_type="ma_event"
        )
        
    except Exception as e:
        logger.error(f"Error searching MA events: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/ma-events/recent")
async def get_recent_ma_events(
    hours: int = Query(24, description="Hours to look back for recent events"),
    k: int = Query(10, description="Number of events to return")
):
    """
    Get recent M&A events from the vector database
    """
    try:
        integration_service = get_vector_db_integration()
        results = await integration_service.get_recent_ma_events(hours=hours, k=k)
        
        return {
            "recent_ma_events": results,
            "hours_back": hours,
            "total_results": len(results)
        }
        
    except Exception as e:
        logger.error(f"Error getting recent MA events: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/sync-ma-events")
async def sync_ma_events():
    """
    Manually sync existing M&A events with vector database
    """
    try:
        integration_service = get_vector_db_integration()
        success = await integration_service.sync_with_ma_data()
        
        if success:
            stats = integration_service.get_vector_db_stats()
            return {
                "message": "M&A events synced successfully",
                "stats": stats
            }
        else:
            raise HTTPException(
                status_code=500,
                detail="Failed to sync M&A events"
            )
        
    except Exception as e:
        logger.error(f"Error syncing MA events: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/examples")
async def get_example_queries():
    """
    Get example queries for testing the vector search
    """
    return {
        "company_searches": [
            "AI companies with high valuations",
            "fintech startups in payments",
            "companies similar to Stripe",
            "exceptional performers with extraordinary scores above 80",
            "Y Combinator companies in healthcare"
        ],
        "relationship_searches": [
            "partnerships between AI companies",
            "connections in the fintech space",
            "companies that work together"
        ],
        "ma_event_searches": [
            "recent acquisitions in AI space",
            "merger and acquisition deals",
            "partnerships between fintech companies",
            "joint ventures in healthcare",
            "high value acquisition deals"
        ],
        "similarity_searches": [
            "OpenAI",
            "Stripe", 
            "Airbnb",
            "Coinbase"
        ]
    }
