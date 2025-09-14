from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import os
from dotenv import load_dotenv
import asyncio
from datetime import datetime, timedelta

from services.data_ingestion import DataIngestionService
from services.llm_service import LLMService
from services.graph_service import GraphService
from services.logo_service import LogoService
from api.exa_routes import router as exa_router
from api.ma_agent_routes import router as ma_agent_router
from api.extraordinary_routes import router as extraordinary_router
from api.impact_simulation_routes import router as impact_simulation_router
from api.vector_search_routes import router as vector_search_router
from models.schemas import (
    Company, Deal, GraphData, PredictionRequest, 
    WhatIfRequest, EducationRequest, NewsData
)

load_dotenv()

app = FastAPI(title="DealFlow API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://dealflow.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
data_service = DataIngestionService()
llm_service = LLMService()
graph_service = GraphService()

# Include routers
app.include_router(exa_router)
app.include_router(ma_agent_router)
app.include_router(extraordinary_router)
app.include_router(impact_simulation_router)
app.include_router(vector_search_router)

@app.get("/")
async def root():
    return {"message": "DealFlow API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.post("/api/ingest-news")
async def ingest_news(query: str = "merger acquisition", days_back: int = 30):
    """Ingest M&A news from various sources"""
    try:
        news_data = await data_service.fetch_news(query, days_back)
        processed_deals = await data_service.process_news_to_deals(news_data)
        return {
            "success": True,
            "news_count": len(news_data),
            "deals_extracted": len(processed_deals),
            "deals": processed_deals
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/companies")
async def get_companies(include_logos: bool = False):
    """Get all companies in the system"""
    try:
        companies = await data_service.get_companies()
        
        if include_logos:
            async with LogoService() as logo_service:
                companies = await logo_service.enrich_companies_with_logos(companies)
        
        return {"companies": companies}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/companies-with-logos")
async def get_companies_with_logos():
    """Get all companies enriched with logo URLs"""
    try:
        companies = await data_service.get_companies()
        
        # Convert Company objects to dictionaries
        companies_dict = []
        for company in companies:
            company_dict = {
                "id": company.id,
                "name": company.name,
                "industry": company.industry,
                "market_cap": company.market_cap,
                "founded_year": company.founded_year,
                "headquarters": company.headquarters,
                "description": company.description,
                "website": company.website,
                "ticker_symbol": company.ticker_symbol,
                "employee_count": company.employee_count,
                "revenue": company.revenue,
                "is_public": company.is_public,
                "extraordinary_score": company.extraordinary_score
            }
            companies_dict.append(company_dict)
        
        # Enrich with logos
        async with LogoService() as logo_service:
            enriched_companies = await logo_service.enrich_companies_with_logos(companies_dict)
        
        return {"companies": enriched_companies}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/deals")
async def get_deals():
    """Get all deals in the system"""
    try:
        deals = await data_service.get_deals()
        return {"deals": deals}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/graph-data")
async def get_graph_data():
    """Get graph data for visualization"""
    try:
        graph_data = await graph_service.generate_graph_data()
        return graph_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/predict-deals")
async def predict_deals(request: PredictionRequest):
    """Generate LLM predictions for future deals"""
    try:
        predictions = await llm_service.predict_future_deals(
            request.companies,
            request.context,
            request.time_horizon
        )
        return {"predictions": predictions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/what-if")
async def what_if_simulation(request: WhatIfRequest):
    """Simulate 'what if' scenarios"""
    try:
        simulation_result = await llm_service.simulate_scenario(
            request.scenario,
            request.companies_involved,
            request.deal_type
        )
        return simulation_result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/education")
async def education_mode(request: EducationRequest):
    """Educational explanations of deals and concepts"""
    try:
        explanation = await llm_service.explain_concept(
            request.query,
            request.expertise_level,
            request.context
        )
        return {"explanation": explanation}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/company/{company_name}")
async def get_company_profile(company_name: str):
    """Get detailed company profile and connections"""
    try:
        profile = await data_service.get_company_profile(company_name)
        return profile
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Company {company_name} not found")

@app.post("/api/graph/add-node")
async def add_graph_node(company: Company):
    """Add a new company node to the graph"""
    try:
        result = await graph_service.add_company_node(company)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/graph/remove-node/{company_id}")
async def remove_graph_node(company_id: str):
    """Remove a company node from the graph"""
    try:
        result = await graph_service.remove_company_node(company_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/graph/add-edge")
async def add_graph_edge(deal: Deal):
    """Add a new deal edge to the graph"""
    try:
        result = await graph_service.add_deal_edge(deal)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/graph/remove-edge/{deal_id}")
async def remove_graph_edge(deal_id: str):
    """Remove a deal edge from the graph"""
    try:
        result = await graph_service.remove_deal_edge(deal_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
