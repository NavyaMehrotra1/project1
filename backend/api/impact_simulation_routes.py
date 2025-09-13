from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List, Dict, Optional
from datetime import datetime
import asyncio
import logging

from services.impact_simulation_service import ImpactSimulationService, SCENARIO_TEMPLATES
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/impact-simulation", tags=["Impact Simulation"])

class SimulationRequest(BaseModel):
    scenario: str
    companies: Optional[List[str]] = None
    apply_to_graph: bool = True

class QuickSimulationRequest(BaseModel):
    template: str
    company1: str
    company2: Optional[str] = None
    industry: Optional[str] = None

@router.post("/simulate")
async def simulate_impact(request: SimulationRequest):
    """Run an impact simulation for a given scenario"""
    
    try:
        async with ImpactSimulationService() as service:
            # Generate impact analysis
            result = await service.simulate_impact(
                scenario=request.scenario,
                companies=request.companies
            )
            
            # Apply to graph if requested
            updated_graph = None
            if request.apply_to_graph:
                updated_graph = await service.apply_simulation_to_graph(result)
            
            return {
                "status": "success",
                "simulation": {
                    "scenario": result.scenario,
                    "primary_companies": result.primary_companies,
                    "affected_companies": result.affected_companies,
                    "new_connections": result.new_connections,
                    "market_impact": result.market_impact,
                    "timeline": result.timeline,
                    "confidence": result.confidence,
                    "reasoning": result.reasoning,
                    "created_at": result.created_at.isoformat()
                },
                "updated_graph": updated_graph,
                "timestamp": datetime.now().isoformat()
            }
            
    except Exception as e:
        logger.error(f"Error in impact simulation: {e}")
        raise HTTPException(status_code=500, detail=f"Simulation failed: {str(e)}")

@router.post("/quick-simulate")
async def quick_simulate(request: QuickSimulationRequest):
    """Run a quick simulation using predefined templates"""
    
    try:
        # Build scenario from template
        scenario = request.template.format(
            company1=request.company1,
            company2=request.company2 or "TechCorp",
            industry=request.industry or "AI"
        )
        
        companies = [request.company1]
        if request.company2:
            companies.append(request.company2)
        
        async with ImpactSimulationService() as service:
            result = await service.simulate_impact(
                scenario=scenario,
                companies=companies
            )
            
            updated_graph = await service.apply_simulation_to_graph(result)
            
            return {
                "status": "success",
                "scenario": scenario,
                "simulation": {
                    "scenario": result.scenario,
                    "primary_companies": result.primary_companies,
                    "affected_companies": result.affected_companies,
                    "new_connections": result.new_connections,
                    "market_impact": result.market_impact,
                    "timeline": result.timeline,
                    "confidence": result.confidence,
                    "reasoning": result.reasoning,
                    "created_at": result.created_at.isoformat()
                },
                "updated_graph": updated_graph
            }
            
    except Exception as e:
        logger.error(f"Error in quick simulation: {e}")
        raise HTTPException(status_code=500, detail=f"Quick simulation failed: {str(e)}")

@router.get("/templates")
async def get_scenario_templates():
    """Get available scenario templates for quick simulations"""
    
    return {
        "templates": SCENARIO_TEMPLATES,
        "description": "Use {company1}, {company2}, {industry} as placeholders"
    }

@router.get("/companies")
async def get_available_companies():
    """Get list of companies available for simulations"""
    
    try:
        import json
        from pathlib import Path
        
        # Load graph data
        graph_data_path = Path(__file__).parent.parent.parent / "data_agent" / "data_agent" / "output" / "graph_data_for_frontend.json"
        
        with open(graph_data_path, 'r') as f:
            graph_data = json.load(f)
        
        companies = []
        for node in graph_data.get('nodes', []):
            data = node.get('data', {})
            if data.get('name'):
                companies.append({
                    'name': data['name'],
                    'industry': data.get('industry'),
                    'batch': data.get('batch'),
                    'extraordinary_score': data.get('extraordinary_score', 0),
                    'valuation': data.get('valuation')
                })
        
        # Sort by extraordinary score
        companies.sort(key=lambda x: x['extraordinary_score'], reverse=True)
        
        return {
            "companies": companies,
            "total": len(companies)
        }
        
    except Exception as e:
        logger.error(f"Error loading companies: {e}")
        raise HTTPException(status_code=500, detail="Failed to load companies")

@router.post("/batch-simulate")
async def batch_simulate(scenarios: List[str]):
    """Run multiple simulations in batch"""
    
    try:
        results = []
        
        async with ImpactSimulationService() as service:
            for scenario in scenarios:
                try:
                    result = await service.simulate_impact(scenario)
                    results.append({
                        "scenario": scenario,
                        "success": True,
                        "result": {
                            "primary_companies": result.primary_companies,
                            "affected_companies": result.affected_companies,
                            "confidence": result.confidence,
                            "timeline": result.timeline
                        }
                    })
                except Exception as e:
                    results.append({
                        "scenario": scenario,
                        "success": False,
                        "error": str(e)
                    })
                
                # Rate limiting
                await asyncio.sleep(1)
        
        return {
            "status": "success",
            "results": results,
            "total_scenarios": len(scenarios),
            "successful": len([r for r in results if r["success"]])
        }
        
    except Exception as e:
        logger.error(f"Error in batch simulation: {e}")
        raise HTTPException(status_code=500, detail=f"Batch simulation failed: {str(e)}")

@router.get("/history")
async def get_simulation_history():
    """Get history of recent simulations (mock endpoint)"""
    
    # In a real implementation, this would load from a database
    mock_history = [
        {
            "scenario": "What if OpenAI partners with Epic Games?",
            "timestamp": "2024-01-13T18:30:00",
            "confidence": 0.75,
            "affected_companies": 3
        },
        {
            "scenario": "What if Stripe acquires Plaid?",
            "timestamp": "2024-01-13T17:45:00", 
            "confidence": 0.82,
            "affected_companies": 5
        }
    ]
    
    return {
        "history": mock_history,
        "total": len(mock_history)
    }
