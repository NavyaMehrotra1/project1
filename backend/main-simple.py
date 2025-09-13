from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import json
from datetime import datetime, timedelta

app = FastAPI(title="DealFlow API - Simple", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple data models
class Company(BaseModel):
    id: str
    name: str
    industry: str
    market_cap: Optional[float] = None
    is_public: bool = True
    extraordinary_score: Optional[float] = None

class Deal(BaseModel):
    id: str
    source_company_id: str
    target_company_id: str
    deal_type: str
    deal_value: Optional[float] = None
    deal_date: str
    description: str
    is_predicted: bool = False

class GraphNode(BaseModel):
    id: str
    label: str
    size: float = 20
    color: str = "#3b82f6"
    data: Dict[str, Any] = {}

class GraphEdge(BaseModel):
    id: str
    source: str
    target: str
    label: str
    weight: float = 1
    color: str = "#64748b"
    data: Dict[str, Any] = {}

class GraphData(BaseModel):
    nodes: List[GraphNode]
    edges: List[GraphEdge]
    metadata: Dict[str, Any] = {}

# Mock data
MOCK_COMPANIES = [
    Company(
        id="openai",
        name="OpenAI",
        industry="Artificial Intelligence",
        market_cap=80000000000,
        is_public=False,
        extraordinary_score=0.95
    ),
    Company(
        id="microsoft",
        name="Microsoft Corporation",
        industry="Technology",
        market_cap=2800000000000,
        is_public=True,
        extraordinary_score=0.85
    ),
    Company(
        id="google",
        name="Alphabet Inc.",
        industry="Technology",
        market_cap=1700000000000,
        is_public=True,
        extraordinary_score=0.88
    ),
    Company(
        id="meta",
        name="Meta Platforms",
        industry="Social Media",
        market_cap=800000000000,
        is_public=True,
        extraordinary_score=0.82
    ),
    Company(
        id="anthropic",
        name="Anthropic",
        industry="Artificial Intelligence",
        market_cap=15000000000,
        is_public=False,
        extraordinary_score=0.92
    )
]

MOCK_DEALS = [
    Deal(
        id="deal_1",
        source_company_id="microsoft",
        target_company_id="openai",
        deal_type="investment",
        deal_value=10000000000,
        deal_date="2023-01-23",
        description="Microsoft invests $10B in OpenAI partnership",
        is_predicted=False
    ),
    Deal(
        id="deal_2",
        source_company_id="google",
        target_company_id="anthropic",
        deal_type="investment",
        deal_value=300000000,
        deal_date="2022-05-15",
        description="Google invests $300M in Anthropic",
        is_predicted=False
    )
]

@app.get("/")
async def root():
    return {"message": "DealFlow Simple API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/api/companies")
async def get_companies():
    return {"companies": MOCK_COMPANIES}

@app.get("/api/deals")
async def get_deals():
    return {"deals": MOCK_DEALS}

@app.get("/api/graph-data")
async def get_graph_data():
    # Create nodes
    nodes = []
    for company in MOCK_COMPANIES:
        size = 30
        if company.market_cap:
            size = min(80, max(20, (company.market_cap / 1e11) * 20 + 20))
        
        if company.extraordinary_score and company.extraordinary_score > 0.8:
            size *= 1.5
        
        color = "#8b5cf6" if company.industry == "Artificial Intelligence" else "#3b82f6"
        
        node = GraphNode(
            id=company.id,
            label=company.name,
            size=size,
            color=color,
            data={
                "industry": company.industry,
                "market_cap": company.market_cap,
                "extraordinary_score": company.extraordinary_score
            }
        )
        nodes.append(node)
    
    # Create edges
    edges = []
    for deal in MOCK_DEALS:
        color = "#fbbf24" if deal.is_predicted else "#10b981"
        
        edge = GraphEdge(
            id=deal.id,
            source=deal.source_company_id,
            target=deal.target_company_id,
            label=f"{deal.deal_type} ({deal.deal_date[:4]})",
            weight=2,
            color=color,
            data={
                "deal_type": deal.deal_type,
                "deal_value": deal.deal_value,
                "is_predicted": deal.is_predicted
            }
        )
        edges.append(edge)
    
    return GraphData(
        nodes=nodes,
        edges=edges,
        metadata={
            "total_companies": len(nodes),
            "total_deals": len(edges),
            "predicted_deals": len([e for e in edges if e.data.get("is_predicted")]),
            "industries": list(set([n.data.get("industry") for n in nodes]))
        }
    )

@app.post("/api/predict-deals")
async def predict_deals(request: dict):
    # Simple mock predictions
    mock_predictions = [
        Deal(
            id="prediction_1",
            source_company_id="microsoft",
            target_company_id="openai",
            deal_type="acquisition",
            deal_value=50000000000,
            deal_date=(datetime.now() + timedelta(days=180)).isoformat(),
            description="Microsoft could acquire OpenAI for $50B",
            is_predicted=True
        )
    ]
    return {"predictions": mock_predictions}

@app.post("/api/what-if")
async def what_if_simulation(request: dict):
    return {
        "scenario": request.get("scenario", "Unknown scenario"),
        "impact_analysis": "This scenario would significantly impact the competitive landscape.",
        "affected_companies": ["Microsoft", "Google", "Meta"],
        "market_implications": "Industry consolidation would accelerate.",
        "confidence_score": 0.75,
        "timeline": "12-18 months for full impact realization"
    }

@app.post("/api/education")
async def education_mode(request: dict):
    query = request.get("query", "")
    level = request.get("expertise_level", "intermediate")
    
    responses = {
        "beginner": f"Let me explain '{query}' in simple terms: This is when companies work together or one buys another to become stronger in business.",
        "intermediate": f"'{query}' involves strategic business combinations where companies merge resources to achieve competitive advantages.",
        "expert": f"'{query}' represents complex corporate restructuring with due diligence, valuation analysis, and integration strategies."
    }
    
    return {"explanation": responses.get(level, responses["intermediate"])}

@app.get("/api/company/{company_id}")
async def get_company_profile(company_id: str):
    company = next((c for c in MOCK_COMPANIES if c.id == company_id), None)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    related_deals = [d for d in MOCK_DEALS if d.source_company_id == company_id or d.target_company_id == company_id]
    
    return {
        "company": company,
        "connections": related_deals,
        "financial_metrics": {"revenue_growth": 0.15, "profit_margin": 0.25},
        "news_sentiment": 0.75,
        "extraordinary_factors": ["AI Leadership", "Market Innovation"] if company.extraordinary_score and company.extraordinary_score > 0.8 else []
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
