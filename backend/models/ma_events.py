from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class EventType(str, Enum):
    MERGER_ACQUISITION = "merger_acquisition"
    BUSINESS_PARTNERSHIP = "business_partnership"
    CONSOLIDATION = "consolidation"
    JOINT_VENTURE = "joint_venture"
    STRATEGIC_ALLIANCE = "strategic_alliance"

class EventStatus(str, Enum):
    RUMORED = "rumored"
    ANNOUNCED = "announced"
    PENDING = "pending"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class CompanyInfo(BaseModel):
    name: str
    industry: Optional[str] = None
    valuation: Optional[float] = None
    batch: Optional[str] = None  # For YC companies
    status: Optional[str] = None  # Public/Private

class MAEvent(BaseModel):
    id: str = Field(..., description="Unique identifier for the event")
    event_type: EventType
    status: EventStatus = EventStatus.ANNOUNCED
    
    # Companies involved
    primary_company: CompanyInfo
    secondary_company: Optional[CompanyInfo] = None
    other_companies: List[CompanyInfo] = Field(default_factory=list)
    
    # Event details
    title: str
    description: str
    deal_value: Optional[float] = None
    deal_currency: str = "USD"
    
    # Metadata
    announced_date: Optional[datetime] = None
    expected_completion: Optional[datetime] = None
    actual_completion: Optional[datetime] = None
    
    # Sources and confidence
    sources: List[Dict[str, Any]] = Field(default_factory=list)
    confidence_score: float = Field(default=0.5, ge=0.0, le=1.0)
    
    # Impact analysis
    ecosystem_impact: Dict[str, Any] = Field(default_factory=dict)
    affected_companies: List[str] = Field(default_factory=list)
    
    # Tracking
    discovered_at: datetime = Field(default_factory=datetime.now)
    last_updated: datetime = Field(default_factory=datetime.now)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class EcosystemImpact(BaseModel):
    event_id: str
    affected_companies: List[str]
    impact_type: str  # "competitive", "supply_chain", "market_share", etc.
    impact_score: float = Field(ge=0.0, le=1.0)
    description: str
    created_at: datetime = Field(default_factory=datetime.now)

class AgentActivity(BaseModel):
    id: str
    timestamp: datetime = Field(default_factory=datetime.now)
    activity_type: str  # "search", "analysis", "notification", "update"
    description: str
    events_found: int = 0
    events_updated: int = 0
    sources_checked: List[str] = Field(default_factory=list)
    execution_time: float = 0.0  # in seconds
    status: str = "completed"  # "running", "completed", "failed"
    
class NotificationEvent(BaseModel):
    id: str
    event_id: str
    notification_type: str  # "new_event", "event_update", "impact_analysis"
    title: str
    message: str
    priority: str = "medium"  # "low", "medium", "high", "critical"
    created_at: datetime = Field(default_factory=datetime.now)
    read: bool = False
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
