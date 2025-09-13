from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List, Dict, Optional
from datetime import datetime
import asyncio
import logging

from services.extraordinary_research_service import ExtraordinaryResearchService, ExtraordinaryProfile
from models.schemas import Company

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/extraordinary", tags=["Extraordinary Research"])

@router.post("/research/{entity_name}")
async def research_extraordinary_profile(
    entity_name: str, 
    entity_type: str = "company",
    background_tasks: BackgroundTasks = None
):
    """Research and create extraordinary profile for a company or person"""
    
    try:
        async with ExtraordinaryResearchService() as service:
            profile = await service.research_extraordinary_profile(entity_name, entity_type)
            
            return {
                "status": "success",
                "profile": {
                    "name": profile.name,
                    "type": profile.type,
                    "extraordinary_score": profile.extraordinary_score,
                    "key_stats": profile.key_stats,
                    "notable_achievements": profile.notable_achievements,
                    "awards_recognitions": profile.awards_recognitions,
                    "media_coverage": profile.media_coverage,
                    "innovation_highlights": profile.innovation_highlights,
                    "competitive_advantages": profile.competitive_advantages,
                    "leadership_team": profile.leadership_team,
                    "funding_history": profile.funding_history,
                    "metrics": {
                        "valuation": profile.metrics.valuation,
                        "funding_raised": profile.metrics.funding_raised,
                        "employee_count": profile.metrics.employee_count,
                        "revenue": profile.metrics.revenue,
                        "unicorn_status": profile.metrics.unicorn_status,
                        "ipo_status": profile.metrics.ipo_status,
                        "years_in_business": profile.metrics.years_in_business,
                        "awards_count": profile.metrics.awards_count,
                        "media_mentions": profile.metrics.media_mentions
                    },
                    "created_at": profile.created_at.isoformat()
                }
            }
            
    except Exception as e:
        logger.error(f"Error researching extraordinary profile for {entity_name}: {e}")
        raise HTTPException(status_code=500, detail=f"Research failed: {str(e)}")

@router.post("/batch-research")
async def batch_research_extraordinary_profiles(companies: List[str]):
    """Research extraordinary profiles for multiple companies"""
    
    try:
        results = {}
        
        async with ExtraordinaryResearchService() as service:
            # Process in batches to avoid overwhelming APIs
            batch_size = 3
            for i in range(0, len(companies), batch_size):
                batch = companies[i:i + batch_size]
                batch_tasks = []
                
                for company in batch:
                    batch_tasks.append(service.research_extraordinary_profile(company, "company"))
                
                batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
                
                for company, result in zip(batch, batch_results):
                    if isinstance(result, Exception):
                        logger.error(f"Error processing {company}: {result}")
                        results[company] = {"error": str(result), "extraordinary_score": 0}
                    else:
                        results[company] = {
                            "extraordinary_score": result.extraordinary_score,
                            "key_stats": result.key_stats,
                            "notable_achievements": result.notable_achievements[:3],  # Top 3
                            "status": "success"
                        }
                
                # Rate limiting delay
                await asyncio.sleep(2)
        
        return {
            "status": "success",
            "results": results,
            "total_processed": len(companies),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error in batch research: {e}")
        raise HTTPException(status_code=500, detail=f"Batch research failed: {str(e)}")

@router.get("/score-metrics")
async def get_score_metrics():
    """Get the metrics and weights used for extraordinary score calculation"""
    
    return {
        "score_breakdown": {
            "valuation": {
                "weight": "20%",
                "description": "Company valuation and market value",
                "scoring": {
                    "$100B+": 20,
                    "$10B+": 15,
                    "$1B+ (Unicorn)": 10,
                    "$100M+": 5
                }
            },
            "funding": {
                "weight": "15%", 
                "description": "Total funding raised",
                "scoring": {
                    "$1B+": 15,
                    "$500M+": 12,
                    "$100M+": 8,
                    "$50M+": 5
                }
            },
            "growth_scale": {
                "weight": "15%",
                "description": "Employee count and scale",
                "scoring": {
                    "10,000+ employees": 15,
                    "5,000+ employees": 12,
                    "1,000+ employees": 8,
                    "500+ employees": 5
                }
            },
            "innovation": {
                "weight": "15%",
                "description": "Innovation mentions, patents, breakthroughs",
                "scoring": "2 points per innovation mention (max 15)"
            },
            "market_position": {
                "weight": "10%",
                "description": "Market leadership and dominance",
                "scoring": "2 points per leadership mention (max 10)"
            },
            "recognition": {
                "weight": "10%",
                "description": "Awards, honors, recognitions",
                "scoring": "1 point per award (max 10)"
            },
            "leadership": {
                "weight": "5%",
                "description": "Leadership team quality and recognition",
                "scoring": "1 point per leadership mention (max 5)"
            },
            "impact": {
                "weight": "10%",
                "description": "Industry and social impact",
                "scoring": "1 point per impact mention (max 10)"
            },
            "bonus_points": {
                "unicorn_status": 5,
                "ipo_status": 5
            }
        },
        "max_score": 100,
        "data_sources": [
            "Exa API for comprehensive web search",
            "News articles and press releases",
            "Company websites and official sources",
            "Industry reports and analysis"
        ]
    }

@router.post("/update-graph-scores")
async def update_graph_extraordinary_scores(company_names: Optional[List[str]] = None):
    """Update extraordinary scores in graph data files"""
    
    try:
        import json
        from pathlib import Path
        
        # Load graph data
        graph_data_path = Path(__file__).parent.parent.parent / "data_agent" / "data_agent" / "output" / "graph_data_for_frontend.json"
        
        if not graph_data_path.exists():
            raise HTTPException(status_code=404, detail="Graph data file not found")
        
        with open(graph_data_path, 'r') as f:
            graph_data = json.load(f)
        
        nodes = graph_data.get('nodes', [])
        
        # Get companies to update
        companies_to_update = company_names or [node['data']['name'] for node in nodes if node.get('data', {}).get('name')]
        
        updated_count = 0
        
        async with ExtraordinaryResearchService() as service:
            # Process companies in batches
            batch_size = 5
            for i in range(0, len(companies_to_update), batch_size):
                batch = companies_to_update[i:i + batch_size]
                
                for company_name in batch:
                    try:
                        # Find the node in graph data
                        node = next((n for n in nodes if n.get('data', {}).get('name') == company_name), None)
                        
                        if node:
                            # Research extraordinary profile
                            profile = await service.research_extraordinary_profile(company_name, "company")
                            
                            # Update the node with new extraordinary score and data
                            node['data']['extraordinary_score'] = profile.extraordinary_score
                            node['data']['extraordinary_metrics'] = {
                                'valuation': profile.metrics.valuation,
                                'funding_raised': profile.metrics.funding_raised,
                                'employee_count': profile.metrics.employee_count,
                                'unicorn_status': profile.metrics.unicorn_status,
                                'ipo_status': profile.metrics.ipo_status,
                                'awards_count': profile.metrics.awards_count
                            }
                            node['data']['last_extraordinary_update'] = datetime.now().isoformat()
                            
                            # Update node visual properties based on score
                            if profile.extraordinary_score >= 80:
                                node['color'] = '#ffd700'  # Gold for exceptional
                                node['size'] = max(node.get('size', 50), 80)
                            elif profile.extraordinary_score >= 60:
                                node['color'] = '#ff6b6b'  # Red for high
                                node['size'] = max(node.get('size', 50), 70)
                            elif profile.extraordinary_score >= 40:
                                node['color'] = '#4ecdc4'  # Teal for medium
                                node['size'] = max(node.get('size', 50), 60)
                            
                            updated_count += 1
                            logger.info(f"Updated {company_name} with extraordinary score: {profile.extraordinary_score}")
                    
                    except Exception as e:
                        logger.error(f"Error updating {company_name}: {e}")
                        continue
                
                # Rate limiting
                await asyncio.sleep(1)
        
        # Save updated graph data
        with open(graph_data_path, 'w') as f:
            json.dump(graph_data, f, indent=2)
        
        return {
            "status": "success",
            "updated_companies": updated_count,
            "total_companies": len(companies_to_update),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error updating graph scores: {e}")
        raise HTTPException(status_code=500, detail=f"Update failed: {str(e)}")

@router.get("/leaderboard")
async def get_extraordinary_leaderboard():
    """Get leaderboard of most extraordinary companies"""
    
    try:
        import json
        from pathlib import Path
        
        # Load graph data
        graph_data_path = Path(__file__).parent.parent.parent / "data_agent" / "data_agent" / "output" / "graph_data_for_frontend.json"
        
        with open(graph_data_path, 'r') as f:
            graph_data = json.load(f)
        
        nodes = graph_data.get('nodes', [])
        
        # Extract companies with extraordinary scores
        companies = []
        for node in nodes:
            data = node.get('data', {})
            if data.get('extraordinary_score', 0) > 0:
                companies.append({
                    'name': data.get('name'),
                    'extraordinary_score': data.get('extraordinary_score', 0),
                    'industry': data.get('industry'),
                    'valuation': data.get('valuation'),
                    'batch': data.get('batch'),
                    'status': data.get('status'),
                    'metrics': data.get('extraordinary_metrics', {})
                })
        
        # Sort by extraordinary score
        companies.sort(key=lambda x: x['extraordinary_score'], reverse=True)
        
        return {
            "leaderboard": companies[:20],  # Top 20
            "total_companies": len(companies),
            "average_score": sum(c['extraordinary_score'] for c in companies) / len(companies) if companies else 0,
            "top_score": companies[0]['extraordinary_score'] if companies else 0
        }
        
    except Exception as e:
        logger.error(f"Error generating leaderboard: {e}")
        raise HTTPException(status_code=500, detail=f"Leaderboard generation failed: {str(e)}")

@router.get("/data-sources")
async def get_available_data_sources():
    """Get information about available data sources for extraordinary research"""
    
    from services.extraordinary_research_service import ADDITIONAL_DATA_SOURCES
    
    return {
        "currently_integrated": {
            "exa_api": {
                "description": "Comprehensive web search with AI-powered results",
                "coverage": "News articles, company websites, press releases, industry reports",
                "cost": "Pay per search",
                "status": "active"
            }
        },
        "recommended_integrations": ADDITIONAL_DATA_SOURCES,
        "integration_priority": [
            {
                "source": "Crunchbase API",
                "reason": "Comprehensive startup database with funding, team, and metrics data",
                "estimated_cost": "$500-2000/month",
                "value": "High - structured company data"
            },
            {
                "source": "PitchBook API", 
                "reason": "Private market intelligence and accurate valuations",
                "estimated_cost": "$1000+/month",
                "value": "High - valuation accuracy"
            },
            {
                "source": "LinkedIn API",
                "reason": "Employee count, leadership team, company growth metrics",
                "estimated_cost": "$100-500/month",
                "value": "Medium - team insights"
            },
            {
                "source": "Patent databases (USPTO, Google Patents)",
                "reason": "Innovation metrics and intellectual property analysis",
                "estimated_cost": "Free - $200/month",
                "value": "Medium - innovation scoring"
            }
        ]
    }
