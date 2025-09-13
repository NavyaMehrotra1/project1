from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum

class DealType(str, Enum):
    MERGER = "merger"
    ACQUISITION = "acquisition"
    PARTNERSHIP = "partnership"
    INVESTMENT = "investment"
    IPO = "ipo"
    JOINT_VENTURE = "joint_venture"

class ExpertiseLevel(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    EXPERT = "expert"

class Company(BaseModel):
    id: str
    name: str
    industry: str
    market_cap: Optional[float] = None
    founded_year: Optional[int] = None
    headquarters: Optional[str] = None
    description: Optional[str] = None
    website: Optional[str] = None
    ticker_symbol: Optional[str] = None
    employee_count: Optional[int] = None
    revenue: Optional[float] = None
    is_public: bool = True
    extraordinary_score: Optional[float] = None
    logo_url: Optional[str] = None

class Deal(BaseModel):
    id: str
    source_company_id: str
    target_company_id: str
    deal_type: DealType
    deal_value: Optional[float] = None
    deal_date: datetime
    description: str
    status: str = "completed"
    confidence_score: Optional[float] = None
    is_predicted: bool = False

class NewsData(BaseModel):
    title: str
    content: str
    source: str
    published_date: datetime
    url: str
    companies_mentioned: List[str] = []

class GraphNode(BaseModel):
    id: str
    label: str
    size: float = 10
    color: str = "#3b82f6"
    x: Optional[float] = None
    y: Optional[float] = None
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

class PredictionRequest(BaseModel):
    companies: List[str]
    context: Optional[str] = None
    time_horizon: int = Field(default=12, description="Months to predict ahead")

class WhatIfRequest(BaseModel):
    scenario: str
    companies_involved: List[str]
    deal_type: Optional[DealType] = None

class EducationRequest(BaseModel):
    query: str
    expertise_level: ExpertiseLevel = ExpertiseLevel.INTERMEDIATE
    context: Optional[str] = None

class SimulationResult(BaseModel):
    scenario: str
    impact_analysis: str
    affected_companies: List[str]
    market_implications: str
    confidence_score: float
    timeline: str

class CompanyProfile(BaseModel):
    company: Company
    connections: List[Deal]
    predictions: List[Deal]
    financial_metrics: Dict[str, Any]
    news_sentiment: float
    extraordinary_factors: List[str] = []
