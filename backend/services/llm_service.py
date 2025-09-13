import os
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import json
from anthropic import Anthropic
from models.schemas import Company, Deal, DealType, SimulationResult, ExpertiseLevel

class LLMService:
    def __init__(self):
        self.anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        self.client = Anthropic(api_key=self.anthropic_key) if self.anthropic_key else None
        
    async def predict_future_deals(self, companies: List[str], context: Optional[str] = None, time_horizon: int = 12) -> List[Deal]:
        """Generate LLM predictions for future deals"""
        if not self.client:
            return self._mock_predictions(companies, time_horizon)
        
        prompt = f"""
        Based on the following companies and market context, predict likely M&A deals, partnerships, or investments that could happen in the next {time_horizon} months:
        
        Companies: {', '.join(companies)}
        Context: {context or 'General market analysis'}
        
        Consider:
        - Industry trends and synergies
        - Company financial positions
        - Strategic needs and gaps
        - Recent market movements
        - Competitive landscape
        
        Return predictions in JSON format with the following structure:
        {{
            "predictions": [
                {{
                    "source_company": "Company A",
                    "target_company": "Company B",
                    "deal_type": "acquisition|merger|partnership|investment",
                    "probability": 0.75,
                    "reasoning": "Strategic rationale",
                    "estimated_value": 1000000000,
                    "timeline": "Q2 2024"
                }}
            ]
        }}
        """
        
        try:
            response = await self._call_anthropic(prompt)
            predictions_data = json.loads(response)
            
            deals = []
            for i, pred in enumerate(predictions_data.get("predictions", [])):
                deal = Deal(
                    id=f"prediction_{i}",
                    source_company_id=pred["source_company"].lower().replace(" ", "_"),
                    target_company_id=pred["target_company"].lower().replace(" ", "_"),
                    deal_type=DealType(pred["deal_type"]),
                    deal_value=pred.get("estimated_value"),
                    deal_date=datetime.now() + timedelta(days=90),  # Approximate
                    description=pred["reasoning"],
                    status="predicted",
                    confidence_score=pred["probability"],
                    is_predicted=True
                )
                deals.append(deal)
            
            return deals
        except Exception as e:
            print(f"LLM prediction error: {e}")
            return self._mock_predictions(companies, time_horizon)

    async def simulate_scenario(self, scenario: str, companies_involved: List[str], deal_type: Optional[DealType] = None) -> SimulationResult:
        """Simulate 'what if' scenarios"""
        if not self.client:
            return self._mock_simulation(scenario, companies_involved)
        
        prompt = f"""
        Analyze the following hypothetical business scenario and provide a comprehensive impact analysis:
        
        Scenario: {scenario}
        Companies Involved: {', '.join(companies_involved)}
        Deal Type: {deal_type.value if deal_type else 'Not specified'}
        
        Provide analysis covering:
        1. Direct impact on involved companies
        2. Market implications and competitive effects
        3. Industry-wide consequences
        4. Timeline for impact realization
        5. Confidence level in the analysis
        
        Format as JSON:
        {{
            "impact_analysis": "Detailed analysis of direct impacts",
            "market_implications": "Broader market effects",
            "affected_companies": ["Company1", "Company2"],
            "timeline": "Expected timeline for impact",
            "confidence_score": 0.85
        }}
        """
        
        try:
            response = await self._call_anthropic(prompt)
            result_data = json.loads(response)
            
            return SimulationResult(
                scenario=scenario,
                impact_analysis=result_data["impact_analysis"],
                affected_companies=result_data["affected_companies"],
                market_implications=result_data["market_implications"],
                confidence_score=result_data["confidence_score"],
                timeline=result_data["timeline"]
            )
        except Exception as e:
            print(f"Simulation error: {e}")
            return self._mock_simulation(scenario, companies_involved)

    async def explain_concept(self, query: str, expertise_level: ExpertiseLevel, context: Optional[str] = None) -> str:
        """Provide educational explanations"""
        if not self.client:
            return self._mock_explanation(query, expertise_level)
        
        level_instructions = {
            ExpertiseLevel.BEGINNER: "Explain in simple terms, avoid jargon, use analogies",
            ExpertiseLevel.INTERMEDIATE: "Use some technical terms but explain them, provide examples",
            ExpertiseLevel.EXPERT: "Use technical language, focus on nuances and implications"
        }
        
        prompt = f"""
        Explain the following business/finance concept or deal:
        
        Query: {query}
        Expertise Level: {expertise_level.value}
        Context: {context or 'General business education'}
        
        Instructions: {level_instructions[expertise_level]}
        
        Provide a clear, engaging explanation that matches the user's expertise level.
        Include relevant examples and implications where appropriate.
        """
        
        try:
            response = await self._call_anthropic(prompt)
            return response
        except Exception as e:
            print(f"Education error: {e}")
            return self._mock_explanation(query, expertise_level)

    async def _call_anthropic(self, prompt: str) -> str:
        """Call Anthropic API"""
        try:
            message = self.client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}]
            )
            return message.content[0].text
        except Exception as e:
            raise Exception(f"Anthropic API error: {e}")

    def _mock_predictions(self, companies: List[str], time_horizon: int) -> List[Deal]:
        """Mock predictions for demo when API is not available"""
        mock_deals = [
            Deal(
                id="prediction_mock_1",
                source_company_id="microsoft",
                target_company_id="openai",
                deal_type=DealType.ACQUISITION,
                deal_value=50000000000,
                deal_date=datetime.now() + timedelta(days=180),
                description="Microsoft could acquire OpenAI to fully integrate AI capabilities",
                status="predicted",
                confidence_score=0.75,
                is_predicted=True
            ),
            Deal(
                id="prediction_mock_2",
                source_company_id="google",
                target_company_id="anthropic",
                deal_type=DealType.PARTNERSHIP,
                deal_value=5000000000,
                deal_date=datetime.now() + timedelta(days=120),
                description="Google and Anthropic strategic partnership for AI safety research",
                status="predicted",
                confidence_score=0.68,
                is_predicted=True
            )
        ]
        return mock_deals[:2]  # Return first 2 for demo

    def _mock_simulation(self, scenario: str, companies_involved: List[str]) -> SimulationResult:
        """Mock simulation for demo"""
        return SimulationResult(
            scenario=scenario,
            impact_analysis=f"The scenario '{scenario}' would significantly impact the competitive landscape. The involved companies would need to restructure their strategic priorities and market positioning.",
            affected_companies=companies_involved + ["Apple", "Amazon", "Tesla"],
            market_implications="This would accelerate industry consolidation and create new competitive dynamics in the technology sector.",
            confidence_score=0.82,
            timeline="Impact would be realized over 12-18 months, with immediate market reactions followed by longer-term strategic adjustments."
        )

    def _mock_explanation(self, query: str, expertise_level: ExpertiseLevel) -> str:
        """Mock explanation for demo"""
        explanations = {
            ExpertiseLevel.BEGINNER: f"Let me explain '{query}' in simple terms: This is a business concept that involves companies working together or one company buying another. Think of it like when two friends decide to combine their lemonade stands to make more money together.",
            ExpertiseLevel.INTERMEDIATE: f"'{query}' refers to strategic business transactions where companies combine resources, capabilities, or ownership structures to achieve competitive advantages, market expansion, or operational synergies.",
            ExpertiseLevel.EXPERT: f"'{query}' represents complex corporate restructuring mechanisms involving due diligence, valuation methodologies, regulatory compliance, and post-transaction integration strategies that optimize shareholder value and market positioning."
        }
        return explanations.get(expertise_level, explanations[ExpertiseLevel.INTERMEDIATE])
