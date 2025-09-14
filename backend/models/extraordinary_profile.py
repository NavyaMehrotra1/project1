"""
Extraordinary Profile Models
Data structures for comprehensive company research profiles
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class ArticleType(str, Enum):
    NEWS = "news"
    FEATURE = "feature"
    INTERVIEW = "interview"
    ANALYSIS = "analysis"
    PRESS_RELEASE = "press_release"
    BLOG_POST = "blog_post"

class RecognitionType(str, Enum):
    AWARD = "award"
    RANKING = "ranking"
    CERTIFICATION = "certification"
    PATENT = "patent"
    MILESTONE = "milestone"
    MEDIA_MENTION = "media_mention"

class FeatType(str, Enum):
    TECHNICAL = "technical"
    BUSINESS = "business"
    SOCIAL_IMPACT = "social_impact"
    INNOVATION = "innovation"
    GROWTH = "growth"
    LEADERSHIP = "leadership"

class NotableArticle(BaseModel):
    title: str
    url: str
    source: str
    published_date: Optional[datetime] = None
    article_type: ArticleType
    summary: str
    key_quotes: List[str] = []
    relevance_score: float = Field(ge=0, le=1)
    sentiment: str = "neutral"  # positive, negative, neutral
    word_count: Optional[int] = None
    author: Optional[str] = None

class Recognition(BaseModel):
    title: str
    organization: str
    year: int
    recognition_type: RecognitionType
    description: str
    url: Optional[str] = None
    rank_position: Optional[int] = None
    total_candidates: Optional[int] = None
    significance_score: float = Field(ge=0, le=1)

class ExtraordinaryFeat(BaseModel):
    title: str
    description: str
    feat_type: FeatType
    date_achieved: Optional[datetime] = None
    metrics: Dict[str, Any] = {}
    impact_description: str
    sources: List[str] = []
    impressiveness_score: float = Field(ge=0, le=1)

class CompanyStats(BaseModel):
    # Financial metrics
    valuation: Optional[int] = None
    revenue: Optional[int] = None
    revenue_growth_rate: Optional[float] = None
    funding_raised: Optional[int] = None
    funding_rounds: Optional[int] = None
    
    # Growth metrics
    employee_count: Optional[int] = None
    employee_growth_rate: Optional[float] = None
    customer_count: Optional[int] = None
    user_count: Optional[int] = None
    
    # Market metrics
    market_share: Optional[float] = None
    countries_operating: Optional[int] = None
    languages_supported: Optional[int] = None
    
    # Product metrics
    products_launched: Optional[int] = None
    patents_filed: Optional[int] = None
    api_calls_per_day: Optional[int] = None
    
    # Social metrics
    github_stars: Optional[int] = None
    social_media_followers: Optional[int] = None
    app_downloads: Optional[int] = None
    
    # Performance metrics
    uptime_percentage: Optional[float] = None
    response_time_ms: Optional[float] = None
    customer_satisfaction: Optional[float] = None
    
    # Last updated
    last_updated: datetime = Field(default_factory=datetime.now)

class ResearchSource(BaseModel):
    name: str
    type: str  # "exa_api", "web_scraping", "api", "manual"
    url: Optional[str] = None
    reliability_score: float = Field(ge=0, le=1)
    last_accessed: datetime = Field(default_factory=datetime.now)

class ExtraordinaryProfile(BaseModel):
    # Basic info
    company_id: str
    company_name: str
    industry: str
    
    # Profile metadata
    profile_id: str
    generated_at: datetime = Field(default_factory=datetime.now)
    last_updated: datetime = Field(default_factory=datetime.now)
    research_depth_score: float = Field(ge=0, le=1)
    
    # Core profile data
    notable_articles: List[NotableArticle] = []
    recognitions: List[Recognition] = []
    extraordinary_feats: List[ExtraordinaryFeat] = []
    company_stats: CompanyStats = Field(default_factory=CompanyStats)
    
    # Research metadata
    sources_used: List[ResearchSource] = []
    research_queries_performed: List[str] = []
    total_sources_analyzed: int = 0
    
    # Profile quality metrics
    article_quality_score: float = 0.0
    recognition_prestige_score: float = 0.0
    feat_impressiveness_score: float = 0.0
    data_completeness_score: float = 0.0
    overall_profile_score: float = 0.0
    
    # Integration with existing system
    extraordinary_score: Optional[float] = None
    yc_batch: Optional[str] = None
    status: Optional[str] = None
    
    def calculate_profile_scores(self):
        """Calculate various profile quality scores"""
        # Article quality score
        if self.notable_articles:
            self.article_quality_score = sum(
                article.relevance_score for article in self.notable_articles
            ) / len(self.notable_articles)
        
        # Recognition prestige score
        if self.recognitions:
            self.recognition_prestige_score = sum(
                recognition.significance_score for recognition in self.recognitions
            ) / len(self.recognitions)
        
        # Feat impressiveness score
        if self.extraordinary_feats:
            self.feat_impressiveness_score = sum(
                feat.impressiveness_score for feat in self.extraordinary_feats
            ) / len(self.extraordinary_feats)
        
        # Data completeness score (0-1 based on filled fields)
        stats_fields = [
            self.company_stats.valuation, self.company_stats.revenue,
            self.company_stats.employee_count, self.company_stats.funding_raised
        ]
        filled_stats = sum(1 for field in stats_fields if field is not None)
        stats_completeness = filled_stats / len(stats_fields)
        
        content_completeness = min(1.0, (
            len(self.notable_articles) / 10 +  # Target 10 articles
            len(self.recognitions) / 5 +       # Target 5 recognitions
            len(self.extraordinary_feats) / 5   # Target 5 feats
        ) / 3)
        
        self.data_completeness_score = (stats_completeness + content_completeness) / 2
        
        # Overall profile score
        self.overall_profile_score = (
            self.article_quality_score * 0.3 +
            self.recognition_prestige_score * 0.25 +
            self.feat_impressiveness_score * 0.25 +
            self.data_completeness_score * 0.2
        )
        
        # Research depth score
        self.research_depth_score = min(1.0, (
            len(self.sources_used) / 20 +      # Target 20 sources
            len(self.research_queries_performed) / 50  # Target 50 queries
        ) / 2)

class ProfileGenerationRequest(BaseModel):
    company_id: str
    company_name: str
    industry: Optional[str] = None
    force_regenerate: bool = False
    research_depth: str = "deep"  # "basic", "standard", "deep", "comprehensive"
    focus_areas: List[str] = []  # ["articles", "recognitions", "feats", "stats"]

class ProfileSearchQuery(BaseModel):
    query: str
    company_context: str
    search_type: str  # "articles", "recognitions", "achievements", "stats"
    time_range: Optional[str] = None  # "1y", "2y", "5y", "all"
    source_types: List[str] = []  # ["news", "academic", "social", "official"]
