"""
Scenario-Based Learning Module for AI-Teach
Integrates with what-if simulator for experiential M&A learning.
"""

import json
import asyncio
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import asdict, dataclass
from datetime import datetime
from models.learning_models import (
    LearningLevel, UserProfile, ScenarioData, ExplanationRequest, ConceptDifficulty
)
from services.claude_service import ClaudeService


@dataclass
class SimulationResult:
    """Results from what-if simulation"""
    scenario_id: str
    user_inputs: Dict[str, Any]
    predicted_outcomes: Dict[str, Any]
    market_impact: Dict[str, float]
    learning_insights: List[str]
    confidence_score: float


class ScenarioLearning:
    """Scenario-based learning with what-if simulator integration"""
    
    def __init__(self, claude_service: ClaudeService):
        self.claude_service = claude_service
        self.scenarios = self._load_learning_scenarios()
        self.simulation_templates = self._load_simulation_templates()
    
    def _load_learning_scenarios(self) -> Dict[str, ScenarioData]:
        """Load predefined learning scenarios for different levels"""
        scenarios = {
            "tech_startup_acquisition": ScenarioData(
                scenario_id="tech_startup_acquisition",
                title="Tech Giant Acquires AI Startup",
                description="A major technology company is considering acquiring a promising AI startup to enhance its machine learning capabilities",
                companies_involved=["TechCorp (Acquirer)", "AI Innovations (Target)"],
                deal_type="strategic_acquisition",
                deal_value=500.0,  # million USD
                industry="technology",
                complexity_level=ConceptDifficulty.INTERMEDIATE,
                learning_objectives=[
                    "Understand strategic rationale for tech acquisitions",
                    "Analyze synergy potential in technology deals",
                    "Evaluate integration challenges for startups"
                ],
                key_concepts=["strategic_fit", "talent_acquisition", "technology_integration"],
                discussion_points=[
                    "What are the key risks in acquiring a startup?",
                    "How should the acquirer value the target's technology?",
                    "What integration approach would preserve innovation culture?"
                ]
            ),
            
            "healthcare_merger": ScenarioData(
                scenario_id="healthcare_merger",
                title="Regional Hospital System Merger",
                description="Two regional hospital systems are considering a merger to achieve cost savings and improve patient care coverage",
                companies_involved=["Regional Health East", "Regional Health West"],
                deal_type="merger_of_equals",
                deal_value=2500.0,
                industry="healthcare",
                complexity_level=ConceptDifficulty.ADVANCED,
                learning_objectives=[
                    "Understand regulatory requirements in healthcare M&A",
                    "Analyze cost synergies in hospital mergers",
                    "Evaluate patient care implications"
                ],
                key_concepts=["regulatory_approval", "cost_synergies", "market_concentration"],
                discussion_points=[
                    "What regulatory hurdles must be cleared?",
                    "How can the merger improve patient outcomes?",
                    "What are the antitrust considerations?"
                ]
            ),
            
            "cross_border_deal": ScenarioData(
                scenario_id="cross_border_deal",
                title="US Company Acquires European Competitor",
                description="A US manufacturing company wants to acquire its European competitor to expand globally and achieve economies of scale",
                companies_involved=["AmeriCorp", "EuroManufacturing"],
                deal_type="cross_border_acquisition",
                deal_value=8000.0,
                industry="manufacturing",
                complexity_level=ConceptDifficulty.EXPERT,
                learning_objectives=[
                    "Understand cross-border M&A complexities",
                    "Analyze currency and regulatory risks",
                    "Evaluate cultural integration challenges"
                ],
                key_concepts=["foreign_exchange_risk", "regulatory_differences", "cultural_integration"],
                discussion_points=[
                    "How should currency risk be managed?",
                    "What are the key regulatory differences?",
                    "How can cultural differences be bridged?"
                ]
            ),
            
            "distressed_acquisition": ScenarioData(
                scenario_id="distressed_acquisition",
                title="Private Equity Distressed Buyout",
                description="A private equity firm is considering acquiring a distressed retail company to restructure and turn it around",
                companies_involved=["PE Partners", "Struggling Retail Co"],
                deal_type="distressed_acquisition",
                deal_value=1200.0,
                industry="retail",
                complexity_level=ConceptDifficulty.EXPERT,
                learning_objectives=[
                    "Understand distressed M&A dynamics",
                    "Analyze turnaround strategies",
                    "Evaluate restructuring risks and returns"
                ],
                key_concepts=["distressed_valuation", "turnaround_strategy", "debt_restructuring"],
                discussion_points=[
                    "What makes this a distressed situation?",
                    "What turnaround strategies could work?",
                    "How should the deal be structured?"
                ]
            )
        }
        
        return scenarios
    
    def _load_simulation_templates(self) -> Dict[str, Dict[str, Any]]:
        """Load simulation parameter templates"""
        return {
            "basic_acquisition": {
                "parameters": [
                    {"name": "purchase_price", "type": "currency", "min": 100, "max": 10000, "default": 1000},
                    {"name": "synergy_estimate", "type": "percentage", "min": 0, "max": 50, "default": 15},
                    {"name": "integration_timeline", "type": "months", "min": 6, "max": 36, "default": 18},
                    {"name": "retention_rate", "type": "percentage", "min": 50, "max": 95, "default": 80}
                ],
                "outcomes": ["deal_value", "synergy_realization", "integration_success", "market_reaction"]
            },
            
            "merger_analysis": {
                "parameters": [
                    {"name": "cost_synergies", "type": "currency", "min": 50, "max": 2000, "default": 300},
                    {"name": "revenue_synergies", "type": "currency", "min": 0, "max": 1000, "default": 150},
                    {"name": "integration_costs", "type": "currency", "min": 100, "max": 800, "default": 200},
                    {"name": "market_share_gain", "type": "percentage", "min": 0, "max": 25, "default": 8}
                ],
                "outcomes": ["net_synergies", "market_position", "competitive_response", "regulatory_risk"]
            }
        }
    
    async def present_scenario(self, scenario_id: str, user_profile: UserProfile, 
                             graph_data: Optional[Dict] = None) -> None:
        """Present learning scenario with adaptive complexity"""
        
        if scenario_id not in self.scenarios:
            print(f"❌ Scenario '{scenario_id}' not found.")
            return
        
        scenario = self.scenarios[scenario_id]
        
        print(f"\n🎭 Learning Scenario: {scenario.title}")
        print("=" * 60)
        print(f"🏢 Industry: {scenario.industry.title()}")
        print(f"💰 Deal Value: ${scenario.deal_value:.0f} million")
        print(f"📊 Deal Type: {scenario.deal_type.replace('_', ' ').title()}")
        print(f"⭐ Complexity: {scenario.complexity_level.name}")
        
        print(f"\n📖 Scenario Description:")
        print(f"{scenario.description}")
        
        print(f"\n🏢 Companies Involved:")
        for company in scenario.companies_involved:
            print(f"   • {company}")
        
        # Adaptive presentation based on user level
        if user_profile.current_level == LearningLevel.BEGINNER:
            await self._present_beginner_scenario(scenario, user_profile, graph_data)
        elif user_profile.current_level == LearningLevel.INTERMEDIATE:
            await self._present_intermediate_scenario(scenario, user_profile, graph_data)
        else:
            await self._present_expert_scenario(scenario, user_profile, graph_data)
        
        # Interactive simulation
        await self._run_interactive_simulation(scenario, user_profile)
    
    async def _present_beginner_scenario(self, scenario: ScenarioData, user_profile: UserProfile, 
                                       graph_data: Optional[Dict]):
        """Present scenario for beginners with basic concepts"""
        print(f"\n🎯 What You'll Learn:")
        for objective in scenario.learning_objectives[:2]:  # Limit for beginners
            print(f"   • {objective}")
        
        print(f"\n💡 Key Concepts to Understand:")
        for concept in scenario.key_concepts:
            concept_name = concept.replace('_', ' ').title()
            print(f"   • {concept_name}")
        
        # Get AI explanation for beginners
        request = ExplanationRequest(
            user_id=user_profile.user_id,
            question=f"Explain this M&A scenario in simple terms: {scenario.description}",
            context=f"This is a {scenario.deal_type} in the {scenario.industry} industry",
            user_level=LearningLevel.BEGINNER,
            graph_data=graph_data
        )
        
        try:
            result = await self.claude_service.generate_explanation(request)
            print(f"\n🤖 Simple Explanation:")
            print(result['explanation'])
        except Exception:
            pass
    
    async def _present_intermediate_scenario(self, scenario: ScenarioData, user_profile: UserProfile,
                                           graph_data: Optional[Dict]):
        """Present scenario for intermediate learners"""
        print(f"\n🎯 Learning Objectives:")
        for objective in scenario.learning_objectives:
            print(f"   • {objective}")
        
        print(f"\n🧠 Key M&A Concepts:")
        for concept in scenario.key_concepts:
            concept_name = concept.replace('_', ' ').title()
            print(f"   • {concept_name}")
        
        print(f"\n❓ Think About These Questions:")
        for question in scenario.discussion_points[:2]:
            print(f"   • {question}")
        
        # Get strategic analysis
        request = ExplanationRequest(
            user_id=user_profile.user_id,
            question=f"Provide strategic analysis of this M&A scenario: {scenario.description}",
            context=f"Focus on {', '.join(scenario.key_concepts)}",
            user_level=LearningLevel.INTERMEDIATE,
            graph_data=graph_data
        )
        
        try:
            result = await self.claude_service.generate_explanation(request)
            print(f"\n📊 Strategic Analysis:")
            print(result['explanation'])
        except Exception:
            pass
    
    async def _present_expert_scenario(self, scenario: ScenarioData, user_profile: UserProfile,
                                     graph_data: Optional[Dict]):
        """Present comprehensive scenario for experts"""
        print(f"\n🎯 Advanced Learning Objectives:")
        for objective in scenario.learning_objectives:
            print(f"   • {objective}")
        
        print(f"\n🧠 Complex M&A Concepts:")
        for concept in scenario.key_concepts:
            concept_name = concept.replace('_', ' ').title()
            print(f"   • {concept_name}")
        
        print(f"\n🤔 Strategic Discussion Points:")
        for question in scenario.discussion_points:
            print(f"   • {question}")
        
        # Get expert-level analysis
        request = ExplanationRequest(
            user_id=user_profile.user_id,
            question=f"Provide expert-level analysis of this complex M&A scenario: {scenario.description}",
            context=f"Include analysis of {', '.join(scenario.key_concepts)} and potential risks/opportunities",
            user_level=LearningLevel.EXPERT,
            graph_data=graph_data
        )
        
        try:
            result = await self.claude_service.generate_explanation(request)
            print(f"\n🎓 Expert Analysis:")
            print(result['explanation'])
        except Exception:
            pass
    
    async def _run_interactive_simulation(self, scenario: ScenarioData, user_profile: UserProfile):
        """Run interactive what-if simulation"""
        print(f"\n🎮 Interactive Simulation")
        print("=" * 40)
        print("Now let's explore different scenarios and see their potential outcomes!")
        
        # Determine simulation template based on deal type
        if "acquisition" in scenario.deal_type:
            template_key = "basic_acquisition"
        else:
            template_key = "merger_analysis"
        
        template = self.simulation_templates.get(template_key, self.simulation_templates["basic_acquisition"])
        
        # Collect user inputs
        user_inputs = {}
        print(f"\n📝 Please provide your assumptions:")
        
        for param in template["parameters"]:
            param_name = param["name"].replace('_', ' ').title()
            param_type = param["type"]
            default_val = param["default"]
            
            if param_type == "currency":
                prompt = f"{param_name} (${param['min']}-${param['max']}M, default ${default_val}M): "
            elif param_type == "percentage":
                prompt = f"{param_name} ({param['min']}-{param['max']}%, default {default_val}%): "
            elif param_type == "months":
                prompt = f"{param_name} ({param['min']}-{param['max']} months, default {default_val}): "
            else:
                prompt = f"{param_name} (default {default_val}): "
            
            try:
                user_input = input(prompt).strip()
                if user_input:
                    if param_type in ["currency", "months"]:
                        user_inputs[param["name"]] = float(user_input)
                    elif param_type == "percentage":
                        user_inputs[param["name"]] = float(user_input) / 100
                    else:
                        user_inputs[param["name"]] = user_input
                else:
                    user_inputs[param["name"]] = default_val
            except ValueError:
                user_inputs[param["name"]] = default_val
                print(f"Using default value: {default_val}")
        
        # Run simulation
        simulation_result = await self._simulate_outcomes(scenario, user_inputs, template, user_profile)
        
        # Present results
        await self._present_simulation_results(simulation_result, user_profile)
    
    async def _simulate_outcomes(self, scenario: ScenarioData, user_inputs: Dict[str, Any],
                                template: Dict[str, Any], user_profile: UserProfile) -> SimulationResult:
        """Simulate deal outcomes based on user inputs"""
        
        # Simple simulation logic (could be enhanced with more sophisticated models)
        predicted_outcomes = {}
        market_impact = {}
        learning_insights = []
        
        # Basic calculations based on inputs
        if "purchase_price" in user_inputs:
            purchase_price = user_inputs["purchase_price"]
            synergy_estimate = user_inputs.get("synergy_estimate", 0.15)
            
            # Calculate deal value impact
            synergy_value = purchase_price * synergy_estimate
            predicted_outcomes["total_synergies"] = synergy_value
            predicted_outcomes["deal_premium"] = purchase_price * 0.25  # Assume 25% premium
            
            # Market impact simulation
            market_impact["stock_price_impact"] = synergy_estimate * 0.5  # Simplified
            market_impact["market_share_change"] = user_inputs.get("market_share_gain", 0.08)
            
            # Generate insights
            if synergy_estimate > 0.20:
                learning_insights.append("High synergy expectations may be difficult to achieve")
            if purchase_price > scenario.deal_value * 1.5:
                learning_insights.append("Premium pricing suggests strategic value beyond financials")
        
        # Get AI-powered analysis
        ai_insights = await self._get_ai_simulation_insights(scenario, user_inputs, user_profile)
        learning_insights.extend(ai_insights)
        
        return SimulationResult(
            scenario_id=scenario.scenario_id,
            user_inputs=user_inputs,
            predicted_outcomes=predicted_outcomes,
            market_impact=market_impact,
            learning_insights=learning_insights,
            confidence_score=0.75  # Could be enhanced with actual confidence modeling
        )
    
    async def _get_ai_simulation_insights(self, scenario: ScenarioData, user_inputs: Dict[str, Any],
                                        user_profile: UserProfile) -> List[str]:
        """Get AI-powered insights on simulation results"""
        
        request = ExplanationRequest(
            user_id=user_profile.user_id,
            question=f"Analyze these M&A simulation inputs and provide insights: {json.dumps(user_inputs, indent=2)}",
            context=f"Scenario: {scenario.title} - {scenario.description}",
            user_level=user_profile.current_level
        )
        
        try:
            result = await self.claude_service.generate_explanation(request)
            # Extract key insights from the explanation
            insights = []
            explanation_lines = result['explanation'].split('\n')
            for line in explanation_lines:
                if any(keyword in line.lower() for keyword in ['insight:', 'key point:', 'important:', 'note:']):
                    insights.append(line.strip())
            
            return insights[:3]  # Return top 3 insights
        except Exception:
            return ["Simulation completed with provided parameters"]
    
    async def _present_simulation_results(self, result: SimulationResult, user_profile: UserProfile):
        """Present simulation results with educational insights"""
        print(f"\n📊 Simulation Results")
        print("=" * 40)
        
        print(f"\n💰 Financial Outcomes:")
        for outcome, value in result.predicted_outcomes.items():
            outcome_name = outcome.replace('_', ' ').title()
            if isinstance(value, float):
                if 'synergies' in outcome or 'premium' in outcome:
                    print(f"   • {outcome_name}: ${value:.1f}M")
                else:
                    print(f"   • {outcome_name}: {value:.2f}")
            else:
                print(f"   • {outcome_name}: {value}")
        
        print(f"\n📈 Market Impact:")
        for impact, value in result.market_impact.items():
            impact_name = impact.replace('_', ' ').title()
            if isinstance(value, float):
                if 'percentage' in impact or 'change' in impact:
                    print(f"   • {impact_name}: {value*100:.1f}%")
                else:
                    print(f"   • {impact_name}: {value:.2f}")
            else:
                print(f"   • {impact_name}: {value}")
        
        print(f"\n🎓 Learning Insights:")
        for insight in result.learning_insights:
            print(f"   • {insight}")
        
        print(f"\n🎯 Confidence Score: {result.confidence_score*100:.0f}%")
        
        # Educational follow-up
        await self._simulation_follow_up(result, user_profile)
    
    async def _simulation_follow_up(self, result: SimulationResult, user_profile: UserProfile):
        """Educational follow-up questions and discussion"""
        print(f"\n🤔 Reflection Questions:")
        
        questions = []
        if user_profile.current_level == LearningLevel.BEGINNER:
            questions = [
                "What surprised you about these results?",
                "Would you change any of your assumptions?"
            ]
        elif user_profile.current_level == LearningLevel.INTERMEDIATE:
            questions = [
                "How might these results affect the deal negotiation?",
                "What additional factors should be considered?"
            ]
        else:
            questions = [
                "How would you adjust the deal structure based on these results?",
                "What risk mitigation strategies would you recommend?"
            ]
        
        for i, question in enumerate(questions, 1):
            print(f"\n{i}. {question}")
            response = input("Your thoughts: ").strip()
            
            if response:
                # Get AI feedback
                request = ExplanationRequest(
                    user_id=user_profile.user_id,
                    question=f"Provide educational feedback on this response: '{response}' to the question '{question}'",
                    context=f"Simulation context: {json.dumps(asdict(result), indent=2)}",
                    user_level=user_profile.current_level
                )
                
                try:
                    feedback_result = await self.claude_service.generate_explanation(request)
                    print(f"\n💡 Feedback: {feedback_result['explanation']}")
                except Exception:
                    print(f"\n💡 Excellent thinking! Those are important considerations in M&A analysis.")
        
        # Offer to try different scenarios
        print(f"\n🔄 Would you like to try different assumptions? (y/n): ", end="")
        retry = input().strip().lower()
        
        if retry in ['y', 'yes']:
            scenario = self.scenarios[result.scenario_id]
            await self._run_interactive_simulation(scenario, user_profile)
    
    def list_available_scenarios(self, user_profile: UserProfile) -> List[str]:
        """List scenarios appropriate for user's level"""
        appropriate_scenarios = []
        
        for scenario_id, scenario in self.scenarios.items():
            # Check if complexity is appropriate for user level
            if user_profile.current_level == LearningLevel.BEGINNER:
                if scenario.complexity_level.value <= ConceptDifficulty.INTERMEDIATE.value:
                    appropriate_scenarios.append(scenario_id)
            elif user_profile.current_level == LearningLevel.INTERMEDIATE:
                if scenario.complexity_level.value <= ConceptDifficulty.ADVANCED.value:
                    appropriate_scenarios.append(scenario_id)
            else:  # EXPERT
                appropriate_scenarios.append(scenario_id)
        
        return appropriate_scenarios
    
    def get_scenario_summary(self, scenario_id: str) -> Optional[str]:
        """Get brief summary of a scenario"""
        if scenario_id in self.scenarios:
            scenario = self.scenarios[scenario_id]
            return f"{scenario.title}: {scenario.description[:100]}..."
        return None
