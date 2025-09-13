"""
AI-Teach: Adaptive Learning System for M&A Education
A comprehensive educational platform with adaptive learning levels and AI-powered explanations.
"""

__version__ = "1.0.0"
__author__ = "AI-Teach Development Team"

from .core.adaptive_learning import AdaptiveLearningEngine
from .core.background_assessment import BackgroundAssessment
from .core.ma_education import MAEducationModule
from .core.scenario_learning import ScenarioLearning
from .services.claude_service import ClaudeService
from .models.learning_models import LearningLevel, UserProfile, Concept

__all__ = [
    "AdaptiveLearningEngine",
    "BackgroundAssessment", 
    "MAEducationModule",
    "ScenarioLearning",
    "ClaudeService",
    "LearningLevel",
    "UserProfile",
    "Concept"
]
