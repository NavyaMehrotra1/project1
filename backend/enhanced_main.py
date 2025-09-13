from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import os
import json
import asyncio
import csv
from datetime import datetime, timedelta
from dotenv import load_dotenv
import socketio

from models.schemas import (
    Company, Deal, GraphData, PredictionRequest, 
    WhatIfRequest, EducationRequest, NewsData, DealType, SimulationResult
)
from ai_relationship_engine import relationship_engine

load_dotenv()

# Create Socket.IO server
sio = socketio.AsyncServer(
    async_mode='asgi',
    cors_allowed_origins=["http://localhost:3000", "https://dealflow.vercel.app"]
)

app = FastAPI(title="Enhanced DealFlow API", version="2.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://dealflow.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Socket.IO event handlers
@sio.event
async def connect(sid, environ):
    print(f"Client {sid} connected")
    await sio.emit('connection_status', {
        'status': 'connected',
        'timestamp': datetime.now().isoformat()
    }, room=sid)

@sio.event
async def disconnect(sid):
    print(f"Client {sid} disconnected")

@sio.event
async def ping(sid, data):
    await sio.emit('pong', {
        'timestamp': datetime.now().isoformat()
    }, room=sid)

@sio.event
async def request_update(sid, data):
    # Send current graph data
    try:
        graph_data = await get_graph_data()
        await sio.emit('graph_update', graph_data, room=sid)
    except Exception as e:
        await sio.emit('error', {'message': str(e)}, room=sid)

# In-memory data storage (replace with database in production)
companies_db = {}
deals_db = {}

def load_yc_data():
    """Load YC Top 100 companies data"""
    yc_file_path = os.path.join(os.path.dirname(__file__), "..", "data_agent", "data_agent", "yc_top_100.csv")
    
    try:
        with open(yc_file_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if not row['name']:  # Skip empty rows
                    continue
                    
                company_id = row['name'].lower().replace(' ', '_').replace('.', '_').replace('&', 'and')
                
                # Convert valuation to float
                valuation = 0
                try:
                    valuation = float(row['valuation']) if row['valuation'] else 0
                except:
                    valuation = 0
                
                # Map industry categories
                industry_mapping = {
                    'Fintech': 'Finance',
                    'AI': 'Artificial Intelligence',
                    'Travel': 'Travel & Hospitality',
                    'Crypto': 'Cryptocurrency',
                    'Food Delivery': 'Food & Delivery',
                    'Design': 'Design & Creative',
                    'Grocery': 'Retail',
                    'Autonomous Vehicles': 'Transportation',
                    'Collaboration': 'Productivity',
                    'DevTools': 'Developer Tools',
                    'Communication': 'Communication',
                    'IoT': 'Internet of Things',
                    'B2B Marketplace': 'B2B',
                    'HR Tech': 'Human Resources',
                    'Database': 'Data & Analytics',
                    'Productivity': 'Productivity',
                    'Social Media': 'Social Media',
                    'Cloud Storage': 'Cloud Infrastructure',
                    'Logistics': 'Logistics',
                    'Data': 'Data & Analytics',
                    'Delivery': 'Food & Delivery',
                    'Automation': 'Automation',
                    'Social Audio': 'Social Media',
                    'Aerospace': 'Aerospace',
                    'Web Building': 'Web Development',
                    'Creator Economy': 'Media & Entertainment',
                    'Analytics': 'Data & Analytics',
                    'Security': 'Cybersecurity',
                    'Legal Tech': 'Legal Technology',
                    'Biotech': 'Biotechnology',
                    'DevOps': 'Developer Tools',
                    'Search': 'Search & Discovery',
                    'Healthcare': 'Healthcare',
                    'Accounting': 'Finance',
                    'AI/ML': 'Artificial Intelligence',
                    'Gaming': 'Gaming',
                    'Video': 'Media & Entertainment',
                    'Email': 'Communication',
                    'Publishing': 'Media & Entertainment',
                    'Project Management': 'Productivity',
                    'Infrastructure': 'Cloud Infrastructure',
                    'Events': 'Events & Conferences',
                    'E-commerce': 'E-commerce'
                }
                
                mapped_industry = industry_mapping.get(row['industry'], row['industry'])
                
                # Calculate extraordinary score based on valuation and status
                extraordinary_score = 0.5
                if valuation > 10000000000:  # >$10B
                    extraordinary_score = 0.95
                elif valuation > 5000000000:  # >$5B
                    extraordinary_score = 0.85
                elif valuation > 1000000000:  # >$1B
                    extraordinary_score = 0.75
                elif valuation > 500000000:  # >$500M
                    extraordinary_score = 0.65
                
                if row['status'] == 'Public':
                    extraordinary_score += 0.1
                elif row['status'] == 'Acquired':
                    extraordinary_score += 0.05
                
                company = Company(
                    id=company_id,
                    name=row['name'],
                    industry=mapped_industry,
                    market_cap=valuation,
                    founded_year=None,  # Not in YC data
                    headquarters="San Francisco, CA",  # Default for YC companies
                    description=f"{row['name']} is a {row['batch']} YC company in the {mapped_industry} space.",
                    is_public=(row['status'] == 'Public'),
                    extraordinary_score=min(1.0, extraordinary_score)
                )
                
                companies_db[company_id] = company
                
        print(f"Loaded {len(companies_db)} companies from YC data")
        
    except FileNotFoundError:
        print("YC data file not found, using sample data only")
        load_sample_data()
    except Exception as e:
        print(f"Error loading YC data: {e}, using sample data")
        load_sample_data()

def load_sample_data():
    """Load sample data if YC data is not available"""
    sample_companies = [
        {
            "id": "openai",
            "name": "OpenAI",
            "industry": "Artificial Intelligence",
            "market_cap": 80000000000,
            "founded_year": 2015,
            "headquarters": "San Francisco, CA",
            "description": "AI research and deployment company",
            "is_public": False,
            "extraordinary_score": 0.95
        },
        {
            "id": "stripe",
            "name": "Stripe",
            "industry": "Finance",
            "market_cap": 95000000000,
            "founded_year": 2010,
            "headquarters": "San Francisco, CA",
            "description": "Online payment processing platform",
            "is_public": False,
            "extraordinary_score": 0.92
        },
        {
            "id": "airbnb",
            "name": "Airbnb",
            "industry": "Travel & Hospitality",
            "market_cap": 75000000000,
            "founded_year": 2008,
            "headquarters": "San Francisco, CA",
            "description": "Online marketplace for lodging and tourism experiences",
            "is_public": True,
            "extraordinary_score": 0.88
        }
    ]
    
    for company_data in sample_companies:
        company = Company(**company_data)
        companies_db[company.id] = company

def generate_sample_deals():
    """Generate realistic sample deals between companies"""
    if len(companies_db) < 2:
        return
    
    company_ids = list(companies_db.keys())
    deal_types = [DealType.ACQUISITION, DealType.MERGER, DealType.PARTNERSHIP, DealType.INVESTMENT]
    
    # Generate some historical deals
    sample_deals = [
        {
            "source": "microsoft",
            "target": "openai",
            "type": DealType.INVESTMENT,
            "value": 10000000000,
            "date": datetime(2023, 1, 23),
            "description": "Microsoft invests $10B in OpenAI partnership"
        },
        {
            "source": "stripe",
            "target": "airbnb",
            "type": DealType.PARTNERSHIP,
            "value": None,
            "date": datetime(2022, 8, 15),
            "description": "Stripe partners with Airbnb for payment processing"
        }
    ]
    
    # Add some predicted deals
    import random
    for i in range(5):
        source_id = random.choice(company_ids)
        target_id = random.choice([cid for cid in company_ids if cid != source_id])
        
        deal = Deal(
            id=f"predicted_deal_{i}",
            source_company_id=source_id,
            target_company_id=target_id,
            deal_type=random.choice(deal_types),
            deal_value=random.randint(100000000, 5000000000),
            deal_date=datetime.now() + timedelta(days=random.randint(30, 365)),
            description=f"Predicted {random.choice(deal_types).value} between {companies_db[source_id].name} and {companies_db[target_id].name}",
            status="predicted",
            confidence_score=random.uniform(0.6, 0.9),
            is_predicted=True
        )
        deals_db[deal.id] = deal
    
    # Add historical deals
    for deal_data in sample_deals:
        if deal_data["source"] in companies_db and deal_data["target"] in companies_db:
            deal = Deal(
                id=f"deal_{deal_data['source']}_{deal_data['target']}",
                source_company_id=deal_data["source"],
                target_company_id=deal_data["target"],
                deal_type=deal_data["type"],
                deal_value=deal_data["value"],
                deal_date=deal_data["date"],
                description=deal_data["description"],
                status="completed",
                confidence_score=1.0,
                is_predicted=False
            )
            deals_db[deal.id] = deal

# Initialize data on startup
load_yc_data()
generate_sample_deals()

@app.get("/")
async def root():
    return {"message": "Enhanced DealFlow API is running", "companies": len(companies_db), "deals": len(deals_db)}

@app.get("/health")
async def health_check():
    return {
        "status": "healthy", 
        "timestamp": datetime.now().isoformat(),
        "data_stats": {
            "companies": len(companies_db),
            "deals": len(deals_db),
            "predicted_deals": len([d for d in deals_db.values() if d.is_predicted])
        }
    }

@app.get("/api/graph-data")
async def get_graph_data():
    """Get graph data for visualization with AI-inferred relationships"""
    try:
        companies = list(companies_db.values())
        deals = list(deals_db.values())
        
        # Generate AI-inferred relationships
        company_dicts = [company.dict() for company in companies]
        ai_relationships = relationship_engine.predict_missing_relationships(company_dicts, max_predictions=15)
        
        # Add AI relationships to deals
        for ai_rel in ai_relationships:
            deal_id = f"ai_inferred_{ai_rel['source_company_id']}_{ai_rel['target_company_id']}"
            ai_deal = Deal(
                id=deal_id,
                source_company_id=ai_rel['source_company_id'],
                target_company_id=ai_rel['target_company_id'],
                deal_type=DealType.PARTNERSHIP,  # Default to partnership
                deal_value=None,
                deal_date=ai_rel['predicted_date'],
                description=f"AI-inferred {ai_rel['relationship_type']} (Confidence: {ai_rel['confidence_score']:.2f})",
                status="ai_predicted",
                confidence_score=ai_rel['confidence_score'],
                is_predicted=True
            )
            deals.append(ai_deal)
        
        # Create nodes
        nodes = []
        for company in companies:
            # Calculate node size based on market cap
            base_size = 24  # Smaller base size for modern look
            if company.market_cap:
                size_multiplier = max(1, min(2, company.market_cap / 10000000000))  # Cap at 2x
                base_size = int(base_size * size_multiplier)
            
            # Industry color mapping
            industry_colors = {
                "Artificial Intelligence": "#8b5cf6",
                "Finance": "#10b981", 
                "Travel & Hospitality": "#f59e0b",
                "Cryptocurrency": "#ef4444",
                "Food & Delivery": "#ec4899",
                "Design & Creative": "#06b6d4",
                "Retail": "#84cc16",
                "Transportation": "#6366f1",
                "Productivity": "#3b82f6",
                "Developer Tools": "#64748b",
                "Communication": "#f97316",
                "Internet of Things": "#8b5cf6",
                "B2B": "#10b981",
                "Human Resources": "#f59e0b",
                "Data & Analytics": "#06b6d4",
                "Social Media": "#ef4444",
                "Cloud Infrastructure": "#64748b",
                "Logistics": "#84cc16",
                "Automation": "#6366f1",
                "Aerospace": "#f97316",
                "Web Development": "#3b82f6",
                "Media & Entertainment": "#ec4899",
                "Cybersecurity": "#ef4444",
                "Legal Technology": "#64748b",
                "Biotechnology": "#10b981",
                "Search & Discovery": "#06b6d4",
                "Healthcare": "#f59e0b",
                "Gaming": "#8b5cf6",
                "Events & Conferences": "#ec4899",
                "E-commerce": "#84cc16"
            }
            
            color = industry_colors.get(company.industry, "#64748b")
            
            nodes.append({
                "id": company.id,
                "label": company.name,
                "size": base_size,
                "color": color,
                "data": {
                    "industry": company.industry,
                    "market_cap": company.market_cap,
                    "is_public": company.is_public,
                    "extraordinary_score": company.extraordinary_score,
                    "headquarters": company.headquarters,
                    "description": company.description
                }
            })
        
        # Create edges (undirected)
        edges = []
        for deal in deals:
            # Skip if companies don't exist
            if deal.source_company_id not in companies_db or deal.target_company_id not in companies_db:
                continue
            
            # Relationship type colors for undirected graph
            relationship_colors = {
                "partnership": "#10b981",
                "strategic_alliance": "#06b6d4", 
                "investment": "#3b82f6",
                "acquisition": "#ef4444",
                "merger": "#8b5cf6",
                "joint_venture": "#f97316"
            }
            
            color = relationship_colors.get(deal.deal_type.value, "#64748b")
            if deal.is_predicted:
                color = "#fbbf24"  # Yellow for AI predictions
            
            # Edge weight based on confidence and deal value
            weight = 2
            if deal.deal_value:
                weight = max(1, min(6, deal.deal_value / 2000000000))  # 1-6 range
            elif deal.confidence_score:
                weight = max(1, deal.confidence_score * 4)  # Scale confidence to weight
            
            edges.append({
                "id": deal.id,
                "source": deal.source_company_id,
                "target": deal.target_company_id,
                "label": f"{deal.deal_type.value}" if not deal.is_predicted else "AI Predicted",
                "weight": weight,
                "color": color,
                "data": {
                    "deal_type": deal.deal_type.value,
                    "deal_value": deal.deal_value,
                    "deal_date": deal.deal_date.isoformat(),
                    "description": deal.description,
                    "is_predicted": deal.is_predicted,
                    "confidence_score": deal.confidence_score,
                    "status": deal.status
                }
            })
        
        graph_data = {
            "nodes": nodes,
            "edges": edges,
            "metadata": {
                "total_companies": len(nodes),
                "total_deals": len(edges),
                "predicted_deals": len([e for e in edges if e["data"]["is_predicted"]]),
                "ai_inferred_relationships": len(ai_relationships),
                "industries": list(set([n["data"]["industry"] for n in nodes])),
                "deal_types": list(set([e["data"]["deal_type"] for e in edges]))
            }
        }
        
        return graph_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/companies")
async def get_companies():
    """Get all companies"""
    return {"companies": list(companies_db.values())}

@app.get("/api/deals")
async def get_deals():
    """Get all deals"""
    return {"deals": list(deals_db.values())}

@app.get("/api/company/{company_id}")
async def get_company_profile(company_id: str):
    """Get detailed company profile"""
    if company_id not in companies_db:
        # Try to find by name
        for cid, company in companies_db.items():
            if company.name.lower().replace(" ", "_") == company_id.lower():
                company_id = cid
                break
        else:
            raise HTTPException(status_code=404, detail=f"Company {company_id} not found")
    
    company = companies_db[company_id]
    
    # Get related deals
    connections = [
        deal for deal in deals_db.values()
        if deal.source_company_id == company_id or deal.target_company_id == company_id
    ]
    
    # Get predictions
    predictions = [deal for deal in connections if deal.is_predicted]
    
    # Mock financial metrics
    financial_metrics = {
        "revenue_growth": 0.15,
        "profit_margin": 0.25,
        "debt_to_equity": 0.3,
        "current_ratio": 2.1,
        "market_cap": company.market_cap
    }
    
    return {
        "company": company,
        "connections": connections,
        "predictions": predictions,
        "financial_metrics": financial_metrics,
        "news_sentiment": 0.75,
        "extraordinary_factors": [
            "Market Leader", 
            "Strong Growth", 
            "Innovation Focus"
        ] if company.extraordinary_score and company.extraordinary_score > 0.8 else []
    }

@app.post("/api/what-if")
async def what_if_simulation(request: WhatIfRequest):
    """Simulate what-if scenarios using AI relationship engine"""
    try:
        companies = list(companies_db.values())
        company_dicts = [company.dict() for company in companies]
        
        # Use AI engine for realistic simulation
        if len(request.companies_involved) >= 2:
            source_id = request.companies_involved[0]
            target_id = request.companies_involved[1]
            
            impact_analysis = relationship_engine.simulate_relationship_impact(
                source_id, target_id, company_dicts
            )
            
            if "error" not in impact_analysis:
                simulation_result = SimulationResult(
                    scenario=request.scenario,
                    impact_analysis=impact_analysis['relationship']['reasoning'][0] if impact_analysis['relationship']['reasoning'] else "Strategic relationship formation",
                    affected_companies=[comp['company_name'] for comp in impact_analysis['market_impact']['affected_companies'][:5]],
                    market_implications=f"Market concentration: {impact_analysis['market_impact']['market_concentration'].get('market_dominance_level', 'medium')} impact",
                    confidence_score=impact_analysis['relationship']['confidence'],
                    timeline=impact_analysis['timeline']['short_term']
                )
            else:
                # Fallback to basic simulation
                simulation_result = SimulationResult(
                    scenario=request.scenario,
                    impact_analysis="Companies not found in system",
                    affected_companies=[],
                    market_implications="Unable to assess impact",
                    confidence_score=0.1,
                    timeline="Unknown"
                )
        else:
            simulation_result = SimulationResult(
                scenario=request.scenario,
                impact_analysis="Insufficient companies specified for analysis",
                affected_companies=[],
                market_implications="Need at least 2 companies for relationship simulation",
                confidence_score=0.1,
                timeline="N/A"
            )
        
        # Broadcast update to connected clients
        await sio.emit('simulation_update', simulation_result.dict())
        
        return simulation_result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/predict-deals")
async def predict_deals(request: PredictionRequest):
    """Generate AI predictions for future deals"""
    try:
        import random
        
        predictions = []
        company_ids = list(companies_db.keys())
        
        for _ in range(min(3, len(request.companies))):
            source_id = random.choice(request.companies)
            target_id = random.choice([cid for cid in company_ids if cid != source_id])
            
            if source_id in companies_db and target_id in companies_db:
                deal_types = [DealType.ACQUISITION, DealType.MERGER, DealType.PARTNERSHIP, DealType.INVESTMENT]
                
                prediction = Deal(
                    id=f"prediction_{len(predictions)}_{source_id}_{target_id}",
                    source_company_id=source_id,
                    target_company_id=target_id,
                    deal_type=random.choice(deal_types),
                    deal_value=random.randint(500000000, 10000000000),
                    deal_date=datetime.now() + timedelta(days=random.randint(30, 365)),
                    description=f"AI predicted {random.choice(deal_types).value} between {companies_db[source_id].name} and {companies_db[target_id].name}",
                    status="predicted",
                    confidence_score=random.uniform(0.6, 0.9),
                    is_predicted=True
                )
                
                predictions.append(prediction)
                deals_db[prediction.id] = prediction
        
        # Broadcast update
        await sio.emit('predictions_update', [p.dict() for p in predictions])
        
        return {"predictions": predictions}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Mount Socket.IO app
socket_app = socketio.ASGIApp(sio, app)

# Periodic data updates (simulate real-time changes)
@app.on_event("startup")
async def startup_event():
    async def periodic_updates():
        while True:
            await asyncio.sleep(30)  # Update every 30 seconds
            
            # Simulate new deal or company update
            if len(companies_db) > 1:
                import random
                company_ids = list(companies_db.keys())
                
                # Randomly update a company's extraordinary score
                company_id = random.choice(company_ids)
                company = companies_db[company_id]
                company.extraordinary_score = min(1.0, company.extraordinary_score + random.uniform(-0.05, 0.05))
                
                # Broadcast update
                await sio.emit('company_update', {
                    "company_id": company_id,
                    "extraordinary_score": company.extraordinary_score
                })
    
    # Start background task
    asyncio.create_task(periodic_updates())

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(socket_app, host="0.0.0.0", port=8000, reload=True)
