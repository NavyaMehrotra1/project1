"""
AI-Teach Main Application
Entry point for the adaptive M&A learning system.
"""

import os
import sys
import asyncio
import json
from typing import Optional, Dict, Any
from datetime import datetime

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.background_assessment import BackgroundAssessment
from core.adaptive_learning import AdaptiveLearningEngine
from core.ma_education import MAEducationModule
from core.scenario_learning import ScenarioLearning
from services.claude_service import ClaudeService
from models.learning_models import UserProfile, LearningLevel


class AITeachApp:
    """Main application class for AI-Teach system"""
    
    def __init__(self):
        """Initialize AI-Teach application"""
        # Initialize Claude service
        try:
            self.claude_service = ClaudeService()
        except ValueError as e:
            print(f"❌ Error initializing Claude service: {e}")
            print("Please set your ANTHROPIC_API_KEY environment variable.")
            sys.exit(1)
        
        # Initialize core modules
        self.background_assessment = BackgroundAssessment(self.claude_service)
        self.adaptive_learning = AdaptiveLearningEngine(self.claude_service)
        self.ma_education = MAEducationModule(self.claude_service)
        self.scenario_learning = ScenarioLearning(self.claude_service)
        
        # User profile
        self.current_user_profile: Optional[UserProfile] = None
        self.graph_data: Optional[Dict[str, Any]] = None
        
        # Load graph data if available
        self._load_graph_data()
    
    def _load_graph_data(self):
        """Load graph data for practical examples"""
        graph_paths = [
            "../knowledge_graph.json",
            "../ai-teacher/knowledge_graph.json",
            "../ai-teacher/web-backend/knowledge_graph.json"
        ]
        
        for path in graph_paths:
            full_path = os.path.join(os.path.dirname(__file__), path)
            if os.path.exists(full_path):
                try:
                    with open(full_path, 'r') as f:
                        self.graph_data = json.load(f)
                    print(f"📊 Loaded graph data from {path}")
                    break
                except Exception as e:
                    print(f"⚠️  Could not load graph data from {path}: {e}")
    
    async def start(self):
        """Start the AI-Teach application"""
        await self._show_welcome()
        
        while True:
            try:
                choice = await self._show_main_menu()
                
                if choice == "1":
                    await self._conduct_assessment()
                elif choice == "2":
                    await self._start_learning_session()
                elif choice == "3":
                    await self._explore_concepts()
                elif choice == "4":
                    await self._run_scenarios()
                elif choice == "5":
                    await self._show_profile()
                elif choice == "6":
                    await self._help_menu()
                elif choice == "7":
                    print("\n👋 Thank you for using AI-Teach! Keep learning!")
                    break
                else:
                    print("❌ Invalid choice. Please try again.")
                
                input("\nPress Enter to continue...")
                
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye! Thanks for using AI-Teach!")
                break
            except Exception as e:
                print(f"\n❌ An error occurred: {e}")
                print("Please try again or contact support.")
    
    async def _show_welcome(self):
        """Show welcome message and introduction"""
        print("\n" + "=" * 70)
        print("🎓 Welcome to AI-Teach: Adaptive M&A Learning System")
        print("=" * 70)
        print("""
🚀 AI-Teach is your personalized M&A education platform that:

   📊 Assesses your background and adapts to your level
   🧠 Provides AI-powered explanations using Claude
   📚 Teaches M&A concepts from basics to advanced topics
   🎭 Offers interactive scenarios and simulations
   🌍 Uses real-world examples and case studies
   📈 Integrates with live deal data for practical learning

💡 The system will start by understanding your background and then
   build your M&A knowledge step by step, ensuring you have a solid
   foundation before moving to advanced concepts.
        """)
        print("=" * 70)
    
    async def _show_main_menu(self) -> str:
        """Show main menu and get user choice"""
        print("\n🎯 AI-Teach Main Menu")
        print("-" * 30)
        print("1. 📋 Take Background Assessment")
        print("2. 📚 Start Learning Session")
        print("3. 🔍 Explore M&A Concepts")
        print("4. 🎭 Run Learning Scenarios")
        print("5. 👤 View My Profile")
        print("6. ❓ Help & Guide")
        print("7. 🚪 Exit")
        
        return input("\nChoose an option (1-7): ").strip()
    
    async def _conduct_assessment(self):
        """Conduct background assessment"""
        print("\n🎓 Starting Background Assessment...")
        
        if self.current_user_profile:
            print("You already have a profile. Would you like to retake the assessment?")
            retake = input("Retake assessment? (y/n): ").strip().lower()
            if retake not in ['y', 'yes']:
                return
        
        user_id = input("Enter your name or ID: ").strip() or "student"
        
        try:
            self.current_user_profile = await self.background_assessment.conduct_assessment(user_id)
            print("\n✅ Assessment completed! Your learning profile has been created.")
        except Exception as e:
            print(f"\n❌ Error during assessment: {e}")
    
    async def _start_learning_session(self):
        """Start adaptive learning session"""
        if not self.current_user_profile:
            print("\n⚠️  Please complete the background assessment first.")
            return
        
        print(f"\n📚 Starting Learning Session for {self.current_user_profile.user_id}")
        
        try:
            session = await self.adaptive_learning.start_learning_session(self.current_user_profile)
            
            # Learn concepts one by one
            concepts_learned = 0
            max_concepts = 3  # Limit per session
            
            while concepts_learned < max_concepts:
                next_concept = await self.adaptive_learning.get_next_concept(
                    self.current_user_profile, session
                )
                
                if not next_concept:
                    print("\n🎉 Great! You've completed all available concepts for your level.")
                    break
                
                print(f"\n📖 Ready to learn about '{next_concept.name}'?")
                proceed = input("Continue? (y/n): ").strip().lower()
                
                if proceed not in ['y', 'yes']:
                    break
                
                await self.adaptive_learning.teach_concept(
                    next_concept, self.current_user_profile, session, self.graph_data
                )
                
                # Update user's known concepts
                if next_concept.id not in self.current_user_profile.known_concepts:
                    self.current_user_profile.known_concepts.append(next_concept.id)
                
                concepts_learned += 1
                
                if concepts_learned < max_concepts:
                    continue_learning = input("\nContinue with next concept? (y/n): ").strip().lower()
                    if continue_learning not in ['y', 'yes']:
                        break
            
            # End session
            summary = await self.adaptive_learning.end_session(session)
            
        except Exception as e:
            print(f"\n❌ Error during learning session: {e}")
    
    async def _explore_concepts(self):
        """Explore M&A concepts and terminology"""
        if not self.current_user_profile:
            print("\n⚠️  Please complete the background assessment first.")
            return
        
        print("\n🔍 M&A Concept Explorer")
        print("-" * 30)
        print("1. Search for a specific term")
        print("2. Browse case studies")
        print("3. Explore industry contexts")
        print("4. Ask a question")
        
        choice = input("\nChoose an option (1-4): ").strip()
        
        try:
            if choice == "1":
                term = input("Enter M&A term to explore: ").strip()
                if term:
                    await self.ma_education.explain_concept(
                        term, self.current_user_profile, graph_data=self.graph_data
                    )
            
            elif choice == "2":
                available_cases = self.ma_education.list_available_case_studies(self.current_user_profile)
                if available_cases:
                    print("\n📊 Available Case Studies:")
                    for i, case_id in enumerate(available_cases, 1):
                        case = self.ma_education.case_studies[case_id]
                        print(f"   {i}. {case['title']}")
                    
                    try:
                        case_choice = int(input("\nSelect case study (number): ")) - 1
                        if 0 <= case_choice < len(available_cases):
                            selected_case = available_cases[case_choice]
                            await self.ma_education.explore_case_study(selected_case, self.current_user_profile)
                    except ValueError:
                        print("Invalid selection.")
                else:
                    print("No case studies available for your level.")
            
            elif choice == "3":
                industries = self.ma_education.list_available_industries()
                print(f"\n🏭 Available Industries: {', '.join(industries)}")
                industry = input("Enter industry to explore: ").strip()
                if industry:
                    await self.ma_education.get_industry_context(industry, self.current_user_profile)
            
            elif choice == "4":
                question = input("Ask your M&A question: ").strip()
                if question:
                    from models.learning_models import ExplanationRequest
                    request = ExplanationRequest(
                        user_id=self.current_user_profile.user_id,
                        question=question,
                        user_level=self.current_user_profile.current_level,
                        graph_data=self.graph_data
                    )
                    result = await self.claude_service.generate_explanation(request)
                    print(f"\n🤖 AI Teacher Response:")
                    print(result['explanation'])
        
        except Exception as e:
            print(f"\n❌ Error exploring concepts: {e}")
    
    async def _run_scenarios(self):
        """Run interactive learning scenarios"""
        if not self.current_user_profile:
            print("\n⚠️  Please complete the background assessment first.")
            return
        
        print("\n🎭 Learning Scenarios")
        print("-" * 25)
        
        available_scenarios = self.scenario_learning.list_available_scenarios(self.current_user_profile)
        
        if not available_scenarios:
            print("No scenarios available for your current level.")
            return
        
        print("Available scenarios:")
        for i, scenario_id in enumerate(available_scenarios, 1):
            summary = self.scenario_learning.get_scenario_summary(scenario_id)
            print(f"   {i}. {summary}")
        
        try:
            choice = int(input("\nSelect scenario (number): ")) - 1
            if 0 <= choice < len(available_scenarios):
                selected_scenario = available_scenarios[choice]
                await self.scenario_learning.present_scenario(
                    selected_scenario, self.current_user_profile, self.graph_data
                )
            else:
                print("Invalid selection.")
        except ValueError:
            print("Invalid selection.")
        except Exception as e:
            print(f"\n❌ Error running scenario: {e}")
    
    async def _show_profile(self):
        """Show user profile and progress"""
        if not self.current_user_profile:
            print("\n⚠️  No profile found. Please complete the background assessment first.")
            return
        
        profile = self.current_user_profile
        
        print(f"\n👤 User Profile: {profile.user_id}")
        print("=" * 40)
        print(f"📊 Learning Level: {profile.current_level.value.title()}")
        print(f"🎯 Assessment Score: {profile.background_assessment_score:.1f}%")
        print(f"📅 Created: {profile.created_at.strftime('%Y-%m-%d %H:%M')}")
        
        print(f"\n🎓 Background:")
        print(f"   • Finance: {'Yes' if profile.finance_background else 'No'}")
        print(f"   • Business: {'Yes' if profile.business_background else 'No'}")
        print(f"   • M&A Experience: {'Yes' if profile.previous_ma_experience else 'No'}")
        
        if profile.known_concepts:
            print(f"\n✅ Known Concepts:")
            for concept in profile.known_concepts:
                print(f"   • {concept.replace('_', ' ').title()}")
        
        if profile.learning_gaps:
            print(f"\n📚 Areas to Focus:")
            for gap in profile.learning_gaps:
                print(f"   • {gap}")
        
        print(f"\n📈 Learning Sessions: {len(profile.session_history)}")
    
    async def _help_menu(self):
        """Show help and guidance"""
        print("\n❓ AI-Teach Help & Guide")
        print("=" * 30)
        print("""
🎯 Getting Started:
   1. Take the background assessment to determine your level
   2. Start with learning sessions to build foundational knowledge
   3. Explore concepts and case studies for deeper understanding
   4. Try scenarios for hands-on experience

📚 Learning Levels:
   • Beginner: New to M&A, focuses on basic concepts
   • Intermediate: Some business background, covers strategic aspects
   • Expert: Advanced learners, complex scenarios and analysis

🔧 Features:
   • Adaptive explanations based on your level
   • Real-world case studies and examples
   • Interactive scenarios with what-if simulations
   • AI-powered responses to your questions
   • Integration with live deal data

💡 Tips:
   • Ask questions anytime during learning sessions
   • Don't skip the assessment - it personalizes your experience
   • Try different scenarios to see various M&A situations
   • Review your profile to track progress

🆘 Need Help?
   • The system adapts to your pace - no pressure!
   • All explanations are tailored to your background
   • You can retake assessments to update your level
        """)


async def main():
    """Main entry point"""
    app = AITeachApp()
    await app.start()


if __name__ == "__main__":
    # Check for required environment variables
    if not os.getenv('ANTHROPIC_API_KEY'):
        print("Warning: ANTHROPIC_API_KEY not found in environment variables.")
        print("Please set it in your .env file or environment.")
        print("Example: export ANTHROPIC_API_KEY='your_api_key_here'")
        print()
    
    asyncio.run(main())
