"""
Adaptive Learning Engine for AI-Teach
Manages personalized learning experiences based on user level and progress.
"""

import json
import asyncio
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import asdict
from models.learning_models import (
    LearningLevel, UserProfile, Concept, LearningSession, ConceptDifficulty
)
from services.claude_service import ClaudeService


class AdaptiveLearningEngine:
    """Core engine for adaptive learning with personalized content delivery"""
    
    def __init__(self, claude_service: ClaudeService):
        self.claude_service = claude_service
        self.ma_concepts = self._load_ma_concepts()
        self.learning_paths = self._define_learning_paths()
        self.active_sessions: Dict[str, LearningSession] = {}
    
    def _load_ma_concepts(self) -> Dict[str, Concept]:
        """Load M&A concepts with difficulty levels and relationships"""
        concepts = {
            # Basic Concepts
            "company_basics": Concept(
                id="company_basics",
                name="Company Fundamentals",
                description="Understanding what companies are and how they operate",
                difficulty_level=ConceptDifficulty.BASIC,
                prerequisites=[],
                examples=["Apple Inc.", "Microsoft Corporation", "Local restaurant"],
                learning_objectives=["Understand corporate structure", "Know business basics"],
                ma_context="Foundation for understanding M&A transactions",
                real_world_examples=["Public vs private companies", "Different business models"]
            ),
            
            "merger_vs_acquisition": Concept(
                id="merger_vs_acquisition",
                name="Mergers vs Acquisitions",
                description="Key differences between mergers and acquisitions",
                difficulty_level=ConceptDifficulty.BASIC,
                prerequisites=["company_basics"],
                examples=["Disney + Pixar (acquisition)", "Exxon + Mobil (merger)"],
                learning_objectives=["Distinguish merger from acquisition", "Understand deal structures"],
                ma_context="Fundamental M&A transaction types",
                real_world_examples=["Facebook acquiring Instagram", "AT&T merging with Time Warner"]
            ),
            
            "due_diligence": Concept(
                id="due_diligence",
                name="Due Diligence Process",
                description="Comprehensive investigation before M&A transactions",
                difficulty_level=ConceptDifficulty.INTERMEDIATE,
                prerequisites=["merger_vs_acquisition"],
                examples=["Financial DD", "Legal DD", "Commercial DD"],
                learning_objectives=["Understand DD process", "Know DD types"],
                ma_context="Critical risk assessment phase in M&A",
                real_world_examples=["Verizon's acquisition of Yahoo", "Microsoft's acquisition of LinkedIn"]
            ),
            
            # Financial Concepts
            "financial_statements": Concept(
                id="financial_statements",
                name="Financial Statements Analysis",
                description="Understanding income statement, balance sheet, cash flow",
                difficulty_level=ConceptDifficulty.INTERMEDIATE,
                prerequisites=["company_basics"],
                examples=["P&L statement", "Balance sheet", "Cash flow statement"],
                learning_objectives=["Read financial statements", "Analyze company performance"],
                ma_context="Essential for valuation and due diligence",
                real_world_examples=["Apple's annual 10-K", "Amazon's quarterly earnings"]
            ),
            
            "valuation_methods": Concept(
                id="valuation_methods",
                name="Company Valuation Methods",
                description="Different approaches to value companies in M&A",
                difficulty_level=ConceptDifficulty.ADVANCED,
                prerequisites=["financial_statements", "due_diligence"],
                examples=["DCF analysis", "Comparable company analysis", "Precedent transactions"],
                learning_objectives=["Apply valuation methods", "Compare valuation approaches"],
                ma_context="Core to determining fair deal price",
                real_world_examples=["Tesla's valuation methods", "Zoom's IPO valuation"]
            ),
            
            # Strategic Concepts
            "synergies": Concept(
                id="synergies",
                name="Synergies in M&A",
                description="Value creation through combining companies",
                difficulty_level=ConceptDifficulty.ADVANCED,
                prerequisites=["merger_vs_acquisition", "financial_statements"],
                examples=["Cost synergies", "Revenue synergies", "Tax synergies"],
                learning_objectives=["Identify synergy types", "Quantify synergy value"],
                ma_context="Key driver of M&A value creation",
                real_world_examples=["Disney + Marvel synergies", "Amazon + Whole Foods synergies"]
            ),
            
            "integration_planning": Concept(
                id="integration_planning",
                name="Post-Merger Integration",
                description="Combining companies after deal completion",
                difficulty_level=ConceptDifficulty.EXPERT,
                prerequisites=["synergies", "due_diligence"],
                examples=["Cultural integration", "System integration", "Workforce integration"],
                learning_objectives=["Plan integration process", "Manage integration risks"],
                ma_context="Critical for realizing M&A value",
                real_world_examples=["Microsoft + GitHub integration", "Disney + Fox integration"]
            ),
            
            # Advanced Financial Concepts
            "accretion_dilution": Concept(
                id="accretion_dilution",
                name="Accretion/Dilution Analysis",
                description="Impact of M&A on earnings per share",
                difficulty_level=ConceptDifficulty.EXPERT,
                prerequisites=["valuation_methods", "financial_statements"],
                examples=["EPS accretion", "EPS dilution", "Breakeven analysis"],
                learning_objectives=["Calculate EPS impact", "Understand timing effects"],
                ma_context="Key metric for public company M&A",
                real_world_examples=["Broadcom's acquisition strategy", "Berkshire Hathaway deals"]
            )
        }
        
        return concepts
    
    def _define_learning_paths(self) -> Dict[LearningLevel, List[str]]:
        """Define learning paths for each level"""
        return {
            LearningLevel.BEGINNER: [
                "company_basics",
                "merger_vs_acquisition", 
                "due_diligence",
                "financial_statements"
            ],
            LearningLevel.INTERMEDIATE: [
                "merger_vs_acquisition",
                "due_diligence", 
                "financial_statements",
                "valuation_methods",
                "synergies"
            ],
            LearningLevel.EXPERT: [
                "valuation_methods",
                "synergies",
                "integration_planning",
                "accretion_dilution"
            ]
        }
    
    async def start_learning_session(self, user_profile: UserProfile) -> LearningSession:
        """Start a new adaptive learning session"""
        session = LearningSession(
            session_id=f"session_{user_profile.user_id}_{len(self.active_sessions)}",
            user_id=user_profile.user_id,
            start_time=datetime.now()
        )
        
        self.active_sessions[session.session_id] = session
        
        # Welcome message based on user level
        await self._provide_session_welcome(user_profile, session)
        
        return session
    
    async def get_next_concept(self, user_profile: UserProfile, session: LearningSession) -> Optional[Concept]:
        """Get the next concept to learn based on adaptive logic"""
        
        # Get learning path for user's level
        path = self.learning_paths[user_profile.current_level]
        
        # Filter out concepts already covered in this session
        remaining_concepts = [cid for cid in path if cid not in session.concepts_covered]
        
        # Check prerequisites
        available_concepts = []
        for concept_id in remaining_concepts:
            concept = self.ma_concepts[concept_id]
            if self._prerequisites_met(concept, user_profile.known_concepts):
                available_concepts.append(concept_id)
        
        if not available_concepts:
            return None
        
        # Return the next concept in the path
        next_concept_id = available_concepts[0]
        return self.ma_concepts[next_concept_id]
    
    async def teach_concept(self, concept: Concept, user_profile: UserProfile, 
                          session: LearningSession, graph_data: Optional[Dict] = None) -> str:
        """Teach a concept with adaptive explanation"""
        
        print(f"\n📚 Learning: {concept.name}")
        print("=" * 50)
        
        # Create explanation request
        from ..models.learning_models import ExplanationRequest
        
        request = ExplanationRequest(
            user_id=user_profile.user_id,
            question=f"Please explain {concept.name} in the context of M&A",
            context=f"Concept: {concept.description}. Prerequisites: {concept.prerequisites}",
            user_level=user_profile.current_level,
            preferred_style="detailed",
            graph_data=graph_data
        )
        
        # Get AI explanation
        explanation_result = await self.claude_service.generate_explanation(request)
        explanation = explanation_result["explanation"]
        
        # Display explanation
        print(f"\n{explanation}")
        
        # Show examples if beginner level
        if user_profile.current_level == LearningLevel.BEGINNER and concept.examples:
            print(f"\n💡 Examples:")
            for example in concept.examples[:3]:
                print(f"   • {example}")
        
        # Show real-world examples
        if concept.real_world_examples:
            print(f"\n🌍 Real-World Examples:")
            for example in concept.real_world_examples[:2]:
                print(f"   • {example}")
        
        # Interactive Q&A
        await self._interactive_qa(concept, user_profile, session)
        
        # Update session
        session.concepts_covered.append(concept.id)
        session.learning_progress[concept.id] = await self._assess_understanding(concept, user_profile)
        
        return explanation
    
    async def _interactive_qa(self, concept: Concept, user_profile: UserProfile, session: LearningSession):
        """Interactive Q&A session for the concept"""
        print(f"\n❓ Let's check your understanding of {concept.name}:")
        
        # Generate questions based on learning objectives
        questions = self._generate_concept_questions(concept, user_profile.current_level)
        
        for i, question in enumerate(questions[:2], 1):  # Ask 2 questions max
            print(f"\n{i}. {question}")
            
            user_response = input("Your answer: ").strip()
            session.questions_asked.append(question)
            session.responses_given.append(user_response)
            
            # Get AI feedback on the response
            feedback = await self._get_response_feedback(question, user_response, concept, user_profile)
            print(f"\n💬 {feedback}")
        
        # Ask if they want to explore more
        print(f"\n🤔 Do you have any questions about {concept.name}?")
        user_question = input("Ask me anything (or press Enter to continue): ").strip()
        
        if user_question:
            from ..models.learning_models import ExplanationRequest
            
            request = ExplanationRequest(
                user_id=user_profile.user_id,
                question=user_question,
                context=f"We just learned about {concept.name}: {concept.description}",
                user_level=user_profile.current_level
            )
            
            response = await self.claude_service.generate_explanation(request)
            print(f"\n🎓 {response['explanation']}")
    
    def _generate_concept_questions(self, concept: Concept, level: LearningLevel) -> List[str]:
        """Generate questions based on concept and user level"""
        questions = []
        
        if level == LearningLevel.BEGINNER:
            questions = [
                f"In your own words, what is {concept.name}?",
                f"Can you give me an example of {concept.name}?"
            ]
        elif level == LearningLevel.INTERMEDIATE:
            questions = [
                f"How does {concept.name} relate to M&A transactions?",
                f"What are the key benefits and challenges of {concept.name}?"
            ]
        else:  # EXPERT
            questions = [
                f"How would you apply {concept.name} in a complex M&A scenario?",
                f"What are the strategic implications of {concept.name}?"
            ]
        
        return questions
    
    async def _get_response_feedback(self, question: str, response: str, concept: Concept, 
                                   user_profile: UserProfile) -> str:
        """Get AI feedback on user's response"""
        
        feedback_prompt = f"""
        Question: {question}
        User Response: {response}
        Concept: {concept.name} - {concept.description}
        User Level: {user_profile.current_level.value}
        
        Provide encouraging feedback on the user's response. If correct, reinforce the learning.
        If incorrect or incomplete, gently guide them to the right understanding.
        """
        
        try:
            from ..models.learning_models import ExplanationRequest
            
            request = ExplanationRequest(
                user_id=user_profile.user_id,
                question=feedback_prompt,
                context="Provide feedback on student response",
                user_level=user_profile.current_level
            )
            
            result = await self.claude_service.generate_explanation(request)
            return result["explanation"]
            
        except Exception as e:
            return "Great thinking! Let's continue exploring this concept."
    
    async def _assess_understanding(self, concept: Concept, user_profile: UserProfile) -> float:
        """Assess user's understanding of the concept (0-1 scale)"""
        # Simplified assessment - could be enhanced with more sophisticated evaluation
        
        if user_profile.current_level == LearningLevel.BEGINNER:
            base_score = 0.7  # Give benefit of doubt for beginners
        elif user_profile.current_level == LearningLevel.INTERMEDIATE:
            base_score = 0.8
        else:
            base_score = 0.9
        
        # Adjust based on concept difficulty vs user level
        difficulty_gap = concept.difficulty_level.value - self._get_level_numeric(user_profile.current_level)
        if difficulty_gap > 2:
            base_score *= 0.8  # Harder concept
        elif difficulty_gap < 0:
            base_score = min(1.0, base_score * 1.1)  # Easier concept
        
        return base_score
    
    def _get_level_numeric(self, level: LearningLevel) -> int:
        """Convert learning level to numeric value"""
        mapping = {
            LearningLevel.BEGINNER: 3,
            LearningLevel.INTERMEDIATE: 5,
            LearningLevel.EXPERT: 7
        }
        return mapping[level]
    
    def _prerequisites_met(self, concept: Concept, known_concepts: List[str]) -> bool:
        """Check if prerequisites for a concept are met"""
        return all(prereq in known_concepts for prereq in concept.prerequisites)
    
    async def _provide_session_welcome(self, user_profile: UserProfile, session: LearningSession):
        """Provide personalized welcome message for the session"""
        print(f"\n🎓 Welcome to your AI-Teach M&A Learning Session!")
        print("=" * 50)
        print(f"👤 Learning Level: {user_profile.current_level.value.title()}")
        print(f"📊 Your Score: {user_profile.background_assessment_score:.1f}%")
        
        if user_profile.known_concepts:
            print(f"✅ You already know: {', '.join(user_profile.known_concepts[:3])}")
        
        learning_path = self.learning_paths[user_profile.current_level]
        remaining_concepts = [cid for cid in learning_path if cid not in user_profile.known_concepts]
        
        print(f"\n📚 Today's Learning Path:")
        for i, concept_id in enumerate(remaining_concepts[:4], 1):
            concept = self.ma_concepts[concept_id]
            print(f"   {i}. {concept.name}")
        
        print(f"\n💡 Remember: I'll adapt the explanations to your level and background.")
        print(f"Feel free to ask questions anytime!")
        print("=" * 50)
    
    async def end_session(self, session: LearningSession) -> Dict[str, Any]:
        """End learning session and provide summary"""
        from datetime import datetime
        
        session.end_time = datetime.now()
        duration = (session.end_time - session.start_time).total_seconds() / 60
        
        print(f"\n🎯 Session Complete!")
        print("=" * 30)
        print(f"⏱️  Duration: {duration:.1f} minutes")
        print(f"📚 Concepts Covered: {len(session.concepts_covered)}")
        print(f"❓ Questions Asked: {len(session.questions_asked)}")
        
        if session.concepts_covered:
            print(f"\n✅ What you learned today:")
            for concept_id in session.concepts_covered:
                concept = self.ma_concepts[concept_id]
                progress = session.learning_progress.get(concept_id, 0)
                print(f"   • {concept.name} ({progress*100:.0f}% mastery)")
        
        # Ask for feedback
        print(f"\n💭 How was your learning experience today?")
        feedback = input("Your feedback (optional): ").strip()
        if feedback:
            session.user_feedback = feedback
        
        # Remove from active sessions
        if session.session_id in self.active_sessions:
            del self.active_sessions[session.session_id]
        
        return {
            "session_summary": asdict(session),
            "concepts_learned": len(session.concepts_covered),
            "duration_minutes": duration,
            "average_progress": sum(session.learning_progress.values()) / len(session.learning_progress) if session.learning_progress else 0
        }
