"""
Learning Models for AI-Teach System
Defines data structures for adaptive learning and user profiling.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from datetime import datetime


class LearningLevel(Enum):
    """User expertise levels for adaptive learning"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate" 
    EXPERT = "expert"


class ConceptDifficulty(Enum):
    """Difficulty levels for concepts"""
    BASIC = 1
    INTERMEDIATE = 3
    ADVANCED = 5
    EXPERT = 7
    MASTER = 9


@dataclass
class Concept:
    """Represents a learning concept in the M&A domain"""
    id: str
    name: str
    description: str
    difficulty_level: ConceptDifficulty
    prerequisites: List[str] = field(default_factory=list)
    examples: List[str] = field(default_factory=list)
    related_concepts: List[str] = field(default_factory=list)
    learning_objectives: List[str] = field(default_factory=list)
    ma_context: Optional[str] = None  # M&A specific context
    real_world_examples: List[str] = field(default_factory=list)


@dataclass
class UserProfile:
    """User learning profile and progress tracking"""
    user_id: str
    current_level: LearningLevel
    background_assessment_score: float = 0.0
    known_concepts: List[str] = field(default_factory=list)
    learning_gaps: List[str] = field(default_factory=list)
    preferred_learning_style: str = "visual"  # visual, auditory, kinesthetic
    session_history: List[Dict[str, Any]] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)
    
    # M&A specific background
    finance_background: bool = False
    business_background: bool = False
    legal_background: bool = False
    previous_ma_experience: bool = False


@dataclass
class LearningSession:
    """Represents a learning session"""
    session_id: str
    user_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    concepts_covered: List[str] = field(default_factory=list)
    questions_asked: List[str] = field(default_factory=list)
    responses_given: List[str] = field(default_factory=list)
    learning_progress: Dict[str, float] = field(default_factory=dict)
    user_feedback: Optional[str] = None


@dataclass
class AssessmentQuestion:
    """Background assessment question"""
    id: str
    question: str
    question_type: str  # multiple_choice, true_false, open_ended
    options: List[str] = field(default_factory=list)
    correct_answer: str = ""
    difficulty_level: ConceptDifficulty = ConceptDifficulty.BASIC
    concept_area: str = ""  # finance, legal, strategy, etc.
    points: int = 1


@dataclass
class ScenarioData:
    """M&A scenario for learning"""
    scenario_id: str
    title: str
    description: str
    companies_involved: List[str]
    deal_type: str  # merger, acquisition, joint_venture, etc.
    deal_value: Optional[float] = None
    industry: str = ""
    complexity_level: ConceptDifficulty = ConceptDifficulty.INTERMEDIATE
    learning_objectives: List[str] = field(default_factory=list)
    key_concepts: List[str] = field(default_factory=list)
    discussion_points: List[str] = field(default_factory=list)


@dataclass
class ExplanationRequest:
    """Request for AI-powered explanation"""
    user_id: str
    question: str
    context: str = ""
    user_level: LearningLevel = LearningLevel.BEGINNER
    preferred_style: str = "detailed"  # brief, detailed, example_heavy
    graph_data: Optional[Dict[str, Any]] = None  # Related graph nodes/edges
