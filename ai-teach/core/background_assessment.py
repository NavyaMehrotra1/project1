"""
Background Assessment System for AI-Teach
Determines user's knowledge level and builds learning foundation.
"""

import json
import asyncio
from typing import List, Dict, Optional, Tuple, Any
from dataclasses import asdict
from models.learning_models import (
    LearningLevel, UserProfile, AssessmentQuestion, ConceptDifficulty
)
from services.claude_service import ClaudeService


class BackgroundAssessment:
    """Handles user background assessment and knowledge level determination"""
    
    def __init__(self, claude_service: ClaudeService):
        self.claude_service = claude_service
        self.assessment_questions = self._load_assessment_questions()
        self.concept_hierarchy = self._build_concept_hierarchy()
    
    def _load_assessment_questions(self) -> List[AssessmentQuestion]:
        """Load predefined assessment questions for different M&A areas"""
        questions = [
            # Basic Business Concepts
            AssessmentQuestion(
                id="basic_1",
                question="What is the primary difference between a merger and an acquisition?",
                question_type="multiple_choice",
                options=[
                    "There is no difference - they're the same thing",
                    "In a merger, companies combine as equals; in acquisition, one buys another",
                    "Mergers are always hostile; acquisitions are friendly",
                    "Mergers involve cash; acquisitions involve stock"
                ],
                correct_answer="In a merger, companies combine as equals; in acquisition, one buys another",
                difficulty_level=ConceptDifficulty.BASIC,
                concept_area="basic_concepts",
                points=1
            ),
            
            AssessmentQuestion(
                id="basic_2", 
                question="What does 'due diligence' mean in M&A?",
                question_type="multiple_choice",
                options=[
                    "The legal requirement to announce deals publicly",
                    "The process of investigating a company before buying it",
                    "The duty of directors to shareholders",
                    "The timeline for completing a transaction"
                ],
                correct_answer="The process of investigating a company before buying it",
                difficulty_level=ConceptDifficulty.BASIC,
                concept_area="process",
                points=1
            ),
            
            # Financial Concepts
            AssessmentQuestion(
                id="finance_1",
                question="What is EBITDA and why is it important in M&A?",
                question_type="open_ended",
                correct_answer="Earnings Before Interest, Taxes, Depreciation, and Amortization - used for valuation",
                difficulty_level=ConceptDifficulty.INTERMEDIATE,
                concept_area="finance",
                points=2
            ),
            
            AssessmentQuestion(
                id="finance_2",
                question="True or False: A higher P/E ratio always means a company is overvalued.",
                question_type="true_false",
                correct_answer="False",
                difficulty_level=ConceptDifficulty.INTERMEDIATE,
                concept_area="valuation",
                points=2
            ),
            
            # Advanced Concepts
            AssessmentQuestion(
                id="advanced_1",
                question="Explain the concept of synergies in M&A and provide an example.",
                question_type="open_ended",
                correct_answer="Benefits from combining companies - cost savings or revenue enhancement",
                difficulty_level=ConceptDifficulty.ADVANCED,
                concept_area="strategy",
                points=3
            ),
            
            AssessmentQuestion(
                id="advanced_2",
                question="What is the difference between accretive and dilutive acquisitions?",
                question_type="open_ended",
                correct_answer="Accretive increases EPS, dilutive decreases EPS",
                difficulty_level=ConceptDifficulty.EXPERT,
                concept_area="financial_impact",
                points=4
            ),
            
            # Background Questions
            AssessmentQuestion(
                id="background_1",
                question="What is your educational or professional background?",
                question_type="open_ended",
                difficulty_level=ConceptDifficulty.BASIC,
                concept_area="background",
                points=0
            ),
            
            AssessmentQuestion(
                id="background_2",
                question="Have you worked in finance, consulting, or investment banking?",
                question_type="true_false",
                difficulty_level=ConceptDifficulty.BASIC,
                concept_area="background",
                points=0
            )
        ]
        
        return questions
    
    def _build_concept_hierarchy(self) -> Dict[str, List[str]]:
        """Build hierarchy of concepts from basic to advanced"""
        return {
            "basic_concepts": ["company", "business", "profit", "revenue"],
            "ma_fundamentals": ["merger", "acquisition", "due_diligence", "deal_structure"],
            "financial_analysis": ["financial_statements", "ratios", "cash_flow", "ebitda"],
            "valuation": ["dcf", "comparable_analysis", "precedent_transactions", "multiples"],
            "strategy": ["synergies", "integration", "market_analysis", "competitive_advantage"],
            "advanced_topics": ["accretion_dilution", "financing_structures", "regulatory", "tax_implications"]
        }
    
    async def conduct_assessment(self, user_id: str) -> UserProfile:
        """Conduct comprehensive background assessment"""
        print("🎓 Starting AI-Teach Background Assessment")
        print("=" * 50)
        print("I'll ask you some questions to understand your background and")
        print("determine the best starting point for your M&A learning journey.\n")
        
        # Start with background questions
        background_responses = await self._assess_background()
        
        # Adaptive questioning based on background
        technical_responses = await self._adaptive_technical_assessment(background_responses)
        
        # Analyze responses with Claude
        all_questions = [q.question for q in self.assessment_questions]
        all_responses = background_responses + technical_responses
        
        assessment_result = await self.claude_service.assess_background_knowledge(
            all_responses, all_questions
        )
        
        # Create user profile
        profile = UserProfile(
            user_id=user_id,
            current_level=assessment_result["recommended_level"],
            background_assessment_score=self._calculate_score(technical_responses),
            known_concepts=self._identify_known_concepts(technical_responses),
            learning_gaps=assessment_result["knowledge_gaps"],
            finance_background=self._has_finance_background(background_responses),
            business_background=self._has_business_background(background_responses),
            previous_ma_experience=self._has_ma_experience(background_responses)
        )
        
        # Provide assessment summary
        await self._provide_assessment_summary(profile, assessment_result)
        
        return profile
    
    async def _assess_background(self) -> List[str]:
        """Assess user's educational and professional background"""
        background_questions = [q for q in self.assessment_questions if q.concept_area == "background"]
        responses = []
        
        print("📋 First, let's learn about your background:\n")
        
        for question in background_questions:
            response = await self._ask_question(question)
            responses.append(response)
        
        return responses
    
    async def _adaptive_technical_assessment(self, background_responses: List[str]) -> List[str]:
        """Conduct adaptive technical assessment based on background"""
        responses = []
        
        # Determine starting difficulty based on background
        has_finance_bg = any("finance" in resp.lower() or "banking" in resp.lower() 
                           for resp in background_responses)
        has_business_bg = any("business" in resp.lower() or "mba" in resp.lower() 
                            for resp in background_responses)
        
        if has_finance_bg:
            start_level = ConceptDifficulty.INTERMEDIATE
            print("\n💼 I see you have a finance background. Let's start with intermediate concepts:\n")
        elif has_business_bg:
            start_level = ConceptDifficulty.BASIC
            print("\n🎯 I see you have business experience. Let's start with M&A fundamentals:\n")
        else:
            start_level = ConceptDifficulty.BASIC
            print("\n📚 Let's start with the basics and build up your knowledge:\n")
        
        # Ask questions adaptively
        current_level = start_level
        correct_count = 0
        total_asked = 0
        
        for question in self.assessment_questions:
            if question.concept_area == "background":
                continue
                
            # Skip if too easy or too hard based on current performance
            if total_asked > 0:
                success_rate = correct_count / total_asked
                if success_rate > 0.8 and question.difficulty_level.value < current_level.value:
                    continue  # Skip easier questions
                elif success_rate < 0.3 and question.difficulty_level.value > current_level.value:
                    continue  # Skip harder questions
            
            if question.difficulty_level.value <= current_level.value + 2:
                response = await self._ask_question(question)
                responses.append(response)
                
                # Check if answer is correct (simplified)
                is_correct = self._evaluate_response(question, response)
                if is_correct:
                    correct_count += 1
                    print("✅ Good understanding!\n")
                else:
                    print("📝 Let's explore this concept further.\n")
                
                total_asked += 1
                
                # Adjust difficulty based on performance
                if total_asked >= 3:
                    success_rate = correct_count / total_asked
                    if success_rate > 0.7:
                        current_level = ConceptDifficulty(min(current_level.value + 2, 9))
                    elif success_rate < 0.4:
                        current_level = ConceptDifficulty(max(current_level.value - 2, 1))
        
        return responses
    
    async def _ask_question(self, question: AssessmentQuestion) -> str:
        """Ask a single assessment question and get user response"""
        print(f"❓ {question.question}")
        
        if question.question_type == "multiple_choice":
            for i, option in enumerate(question.options, 1):
                print(f"   {i}. {option}")
            print()
            
            while True:
                try:
                    choice = input("Your answer (1-4): ").strip()
                    choice_num = int(choice)
                    if 1 <= choice_num <= len(question.options):
                        return question.options[choice_num - 1]
                    else:
                        print("Please enter a number between 1 and 4.")
                except ValueError:
                    print("Please enter a valid number.")
        
        elif question.question_type == "true_false":
            while True:
                response = input("Your answer (True/False): ").strip().lower()
                if response in ['true', 't', 'false', 'f']:
                    return 'True' if response in ['true', 't'] else 'False'
                else:
                    print("Please answer True or False.")
        
        else:  # open_ended
            response = input("Your answer: ").strip()
            print()
            return response
    
    def _evaluate_response(self, question: AssessmentQuestion, response: str) -> bool:
        """Evaluate if response is correct (simplified evaluation)"""
        if question.question_type in ["multiple_choice", "true_false"]:
            return response.lower() == question.correct_answer.lower()
        else:
            # For open-ended, check for key terms (simplified)
            key_terms = question.correct_answer.lower().split()
            response_lower = response.lower()
            return any(term in response_lower for term in key_terms if len(term) > 3)
    
    def _calculate_score(self, responses: List[str]) -> float:
        """Calculate assessment score based on responses"""
        # Simplified scoring - could be enhanced with Claude evaluation
        total_points = 0
        earned_points = 0
        
        technical_questions = [q for q in self.assessment_questions if q.concept_area != "background"]
        
        for i, question in enumerate(technical_questions):
            if i < len(responses):
                total_points += question.points
                if self._evaluate_response(question, responses[i]):
                    earned_points += question.points
        
        return (earned_points / total_points) * 100 if total_points > 0 else 0
    
    def _identify_known_concepts(self, responses: List[str]) -> List[str]:
        """Identify concepts the user already knows"""
        known = []
        technical_questions = [q for q in self.assessment_questions if q.concept_area != "background"]
        
        for i, question in enumerate(technical_questions):
            if i < len(responses) and self._evaluate_response(question, responses[i]):
                known.append(question.concept_area)
        
        return list(set(known))  # Remove duplicates
    
    def _has_finance_background(self, responses: List[str]) -> bool:
        """Check if user has finance background"""
        finance_terms = ["finance", "banking", "investment", "accounting", "cfa", "mba"]
        return any(any(term in resp.lower() for term in finance_terms) for resp in responses)
    
    def _has_business_background(self, responses: List[str]) -> bool:
        """Check if user has business background"""
        business_terms = ["business", "management", "consulting", "strategy", "mba"]
        return any(any(term in resp.lower() for term in business_terms) for resp in responses)
    
    def _has_ma_experience(self, responses: List[str]) -> bool:
        """Check if user has M&A experience"""
        ma_terms = ["merger", "acquisition", "m&a", "deal", "investment banking"]
        return any(any(term in resp.lower() for term in ma_terms) for resp in responses)
    
    async def _provide_assessment_summary(self, profile: UserProfile, assessment_result: Dict[str, Any]):
        """Provide summary of assessment results"""
        print("\n" + "=" * 50)
        print("🎯 ASSESSMENT COMPLETE!")
        print("=" * 50)
        
        print(f"\n📊 Your Learning Profile:")
        print(f"   • Recommended Level: {profile.current_level.value.title()}")
        print(f"   • Assessment Score: {profile.background_assessment_score:.1f}%")
        print(f"   • Known Concepts: {', '.join(profile.known_concepts) if profile.known_concepts else 'Starting fresh!'}")
        
        if profile.learning_gaps:
            print(f"   • Areas to Focus: {', '.join(profile.learning_gaps)}")
        
        print(f"\n🎓 Background Summary:")
        print(f"   • Finance Background: {'Yes' if profile.finance_background else 'No'}")
        print(f"   • Business Background: {'Yes' if profile.business_background else 'No'}")
        print(f"   • M&A Experience: {'Yes' if profile.previous_ma_experience else 'No'}")
        
        print(f"\n📚 Recommended Learning Path:")
        learning_path = self._generate_learning_path(profile)
        for i, concept in enumerate(learning_path[:5], 1):
            print(f"   {i}. {concept}")
        
        print(f"\n💡 {assessment_result.get('assessment', 'Ready to start learning!')}")
        print("\n" + "=" * 50)
    
    def _generate_learning_path(self, profile: UserProfile) -> List[str]:
        """Generate personalized learning path based on profile"""
        all_concepts = []
        for level, concepts in self.concept_hierarchy.items():
            all_concepts.extend(concepts)
        
        # Filter out known concepts and order by difficulty
        unknown_concepts = [c for c in all_concepts if c not in profile.known_concepts]
        
        # Customize based on level
        if profile.current_level == LearningLevel.BEGINNER:
            return self.concept_hierarchy["basic_concepts"] + self.concept_hierarchy["ma_fundamentals"]
        elif profile.current_level == LearningLevel.INTERMEDIATE:
            return self.concept_hierarchy["ma_fundamentals"] + self.concept_hierarchy["financial_analysis"]
        else:
            return self.concept_hierarchy["valuation"] + self.concept_hierarchy["strategy"]
