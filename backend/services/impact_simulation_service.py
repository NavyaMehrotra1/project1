#!/usr/bin/env python3
"""
Impact Simulation Service using Cerebras API for fast LLM inference
Generates counterfactual "what if" scenarios and their impacts on companies
"""

import asyncio
import aiohttp
import json
import os
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class ImpactResult:
    """Result of an impact simulation"""
    scenario: str
    primary_companies: List[str]
    affected_companies: List[Dict[str, Any]]
    new_connections: List[Dict[str, Any]]
    market_impact: Dict[str, Any]
    timeline: str
    confidence: float
    reasoning: str
    created_at: datetime

class ImpactSimulationService:
    def __init__(self):
        self.cerebras_api_key = os.getenv('CEREBRAS_API_KEY')
        self.session = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def simulate_impact(self, scenario: str, companies: List[str] = None) -> ImpactResult:
        """
        Simulate the impact of a hypothetical scenario
        
        Args:
            scenario: The "what if" scenario (e.g., "OpenAI partners with Epic Games")
            companies: Optional list of companies to focus analysis on
        
        Returns:
            ImpactResult with detailed analysis and graph updates
        """
        
        logger.info(f"Simulating impact for scenario: {scenario}")
        
        # Get current company data for context
        company_context = await self._get_company_context(companies)
        
        # Generate impact analysis using Cerebras
        impact_analysis = await self._generate_impact_analysis(scenario, company_context)
        
        # Parse and structure the results
        result = await self._parse_impact_results(scenario, impact_analysis, companies)
        
        logger.info(f"Impact simulation completed for: {scenario}")
        return result
    
    async def _get_company_context(self, companies: List[str] = None) -> Dict:
        """Get relevant company data for context"""
        
        # Load graph data for company context
        try:
            import json
            from pathlib import Path
            
            graph_data_path = Path(__file__).parent.parent.parent / "data_agent" / "data_agent" / "output" / "graph_data_for_frontend.json"
            
            with open(graph_data_path, 'r') as f:
                graph_data = json.load(f)
            
            nodes = graph_data.get('nodes', [])
            
            # Create company lookup
            company_data = {}
            for node in nodes:
                data = node.get('data', {})
                name = data.get('name')
                if name:
                    company_data[name] = {
                        'industry': data.get('industry'),
                        'batch': data.get('batch'),
                        'status': data.get('status'),
                        'valuation': data.get('valuation'),
                        'extraordinary_score': data.get('extraordinary_score', 0),
                        'deal_activity_count': data.get('deal_activity_count', 0)
                    }
            
            return {
                'total_companies': len(nodes),
                'company_data': company_data,
                'focus_companies': companies or []
            }
            
        except Exception as e:
            logger.error(f"Error loading company context: {e}")
            return {'total_companies': 0, 'company_data': {}, 'focus_companies': companies or []}
    
    async def _generate_impact_analysis(self, scenario: str, context: Dict) -> Dict:
        """Generate impact analysis using Cerebras API"""
        
        if not self.cerebras_api_key:
            logger.warning("Cerebras API key not found, using mock analysis")
            return await self._generate_mock_analysis(scenario, context)
        
        # Prepare the prompt for impact analysis
        prompt = self._create_impact_prompt(scenario, context)
        
        try:
            headers = {
                "Authorization": f"Bearer {self.cerebras_api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "llama3.1-70b",  # Fast Cerebras model
                "messages": [
                    {
                        "role": "system",
                        "content": "You are an expert business analyst specializing in startup ecosystems, M&A activity, and market impact analysis. Provide detailed, realistic assessments of hypothetical business scenarios."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "max_tokens": 2000,
                "temperature": 0.7,
                "response_format": {"type": "json_object"}
            }
            
            async with self.session.post(
                "https://api.cerebras.ai/v1/chat/completions",
                headers=headers,
                json=payload
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    content = result['choices'][0]['message']['content']
                    return json.loads(content)
                else:
                    logger.error(f"Cerebras API error: {response.status}")
                    return await self._generate_mock_analysis(scenario, context)
                    
        except Exception as e:
            logger.error(f"Error calling Cerebras API: {e}")
            return await self._generate_mock_analysis(scenario, context)
    
    def _create_impact_prompt(self, scenario: str, context: Dict) -> str:
        """Create a detailed prompt for impact analysis"""
        
        company_data = context.get('company_data', {})
        focus_companies = context.get('focus_companies', [])
        
        # Extract relevant companies from scenario
        scenario_companies = []
        for company_name in company_data.keys():
            if company_name.lower() in scenario.lower():
                scenario_companies.append(company_name)
        
        prompt = f"""
Analyze the business impact of this hypothetical scenario: "{scenario}"

CONTEXT:
- Total companies in ecosystem: {context.get('total_companies', 0)}
- Key companies involved: {scenario_companies}
- Focus companies: {focus_companies}

COMPANY DATA:
{json.dumps({k: v for k, v in list(company_data.items())[:10]}, indent=2)}

ANALYSIS REQUIRED:
1. Identify primary companies directly affected
2. Analyze secondary/tertiary impact on other companies
3. Predict new business relationships or partnerships
4. Assess market-wide implications
5. Estimate timeline and confidence level

OUTPUT FORMAT (JSON):
{{
    "primary_companies": ["Company1", "Company2"],
    "affected_companies": [
        {{
            "name": "CompanyName",
            "impact_type": "positive|negative|neutral",
            "impact_score": 0-100,
            "reasoning": "Why this company is affected",
            "new_extraordinary_score": 0-100,
            "valuation_change": "+/-X%"
        }}
    ],
    "new_connections": [
        {{
            "source": "Company1",
            "target": "Company2", 
            "connection_type": "partnership|acquisition|competition|supplier",
            "strength": 0-100,
            "description": "Nature of new relationship"
        }}
    ],
    "market_impact": {{
        "sector": "AI|Fintech|SaaS|etc",
        "overall_sentiment": "positive|negative|mixed",
        "market_cap_change": "+/-X%",
        "innovation_acceleration": true|false
    }},
    "timeline": "immediate|3-6 months|6-12 months|1-2 years",
    "confidence": 0.0-1.0,
    "reasoning": "Detailed explanation of the analysis and predictions"
}}

Provide realistic, data-driven analysis based on actual business dynamics and market trends.
"""
        
        return prompt
    
    async def _generate_mock_analysis(self, scenario: str, context: Dict) -> Dict:
        """Generate mock analysis when API is unavailable"""
        
        # Extract companies from scenario
        company_data = context.get('company_data', {})
        scenario_companies = []
        
        for company_name in company_data.keys():
            if company_name.lower() in scenario.lower():
                scenario_companies.append(company_name)
        
        # Generate realistic mock data
        mock_analysis = {
            "primary_companies": scenario_companies[:2] if scenario_companies else ["OpenAI", "Epic Games"],
            "affected_companies": [
                {
                    "name": "Unity",
                    "impact_type": "negative",
                    "impact_score": 75,
                    "reasoning": "Competitive pressure from OpenAI-Epic partnership in gaming AI",
                    "new_extraordinary_score": 45,
                    "valuation_change": "-15%"
                },
                {
                    "name": "Nvidia",
                    "impact_type": "positive", 
                    "impact_score": 85,
                    "reasoning": "Increased demand for AI infrastructure and gaming GPUs",
                    "new_extraordinary_score": 92,
                    "valuation_change": "+25%"
                },
                {
                    "name": "Microsoft",
                    "impact_type": "positive",
                    "impact_score": 70,
                    "reasoning": "Benefits through existing OpenAI partnership and Azure cloud services",
                    "new_extraordinary_score": 88,
                    "valuation_change": "+12%"
                }
            ],
            "new_connections": [
                {
                    "source": "OpenAI",
                    "target": "Epic Games",
                    "connection_type": "partnership",
                    "strength": 95,
                    "description": "Strategic AI integration partnership for next-gen gaming experiences"
                },
                {
                    "source": "Epic Games", 
                    "target": "Nvidia",
                    "connection_type": "supplier",
                    "strength": 80,
                    "description": "Enhanced GPU requirements for AI-powered gaming"
                }
            ],
            "market_impact": {
                "sector": "Gaming AI",
                "overall_sentiment": "positive",
                "market_cap_change": "+8%",
                "innovation_acceleration": True
            },
            "timeline": "6-12 months",
            "confidence": 0.75,
            "reasoning": "This partnership would combine OpenAI's advanced AI capabilities with Epic's gaming platform expertise, creating new opportunities in AI-powered gaming while disrupting traditional gaming companies."
        }
        
        return mock_analysis
    
    async def _parse_impact_results(self, scenario: str, analysis: Dict, companies: List[str] = None) -> ImpactResult:
        """Parse and structure the impact analysis results"""
        
        return ImpactResult(
            scenario=scenario,
            primary_companies=analysis.get('primary_companies', []),
            affected_companies=analysis.get('affected_companies', []),
            new_connections=analysis.get('new_connections', []),
            market_impact=analysis.get('market_impact', {}),
            timeline=analysis.get('timeline', 'unknown'),
            confidence=analysis.get('confidence', 0.5),
            reasoning=analysis.get('reasoning', ''),
            created_at=datetime.now()
        )
    
    async def apply_simulation_to_graph(self, result: ImpactResult) -> Dict:
        """
        Apply simulation results to graph data and return updated graph
        
        Returns:
            Updated graph data with simulation effects applied
        """
        
        try:
            import json
            from pathlib import Path
            
            # Load current graph data
            graph_data_path = Path(__file__).parent.parent.parent / "data_agent" / "data_agent" / "output" / "graph_data_for_frontend.json"
            
            with open(graph_data_path, 'r') as f:
                graph_data = json.load(f)
            
            # Create a copy for simulation (don't modify original)
            simulated_graph = json.loads(json.dumps(graph_data))
            
            # Apply company impacts
            nodes = simulated_graph.get('nodes', [])
            for affected in result.affected_companies:
                company_name = affected.get('name')
                
                for node in nodes:
                    if node.get('data', {}).get('name') == company_name:
                        # Update extraordinary score
                        new_score = affected.get('new_extraordinary_score')
                        if new_score:
                            node['data']['extraordinary_score'] = new_score
                            
                            # Update visual properties based on new score
                            if new_score >= 80:
                                node['color'] = '#ffd700'  # Gold
                                node['size'] = max(node.get('size', 50), 80)
                            elif new_score >= 60:
                                node['color'] = '#ff6b6b'  # Red  
                                node['size'] = max(node.get('size', 50), 70)
                            elif new_score >= 40:
                                node['color'] = '#4ecdc4'  # Teal
                                node['size'] = max(node.get('size', 50), 60)
                            else:
                                node['color'] = '#95a5a6'  # Gray
                        
                        # Add simulation metadata
                        node['data']['simulation_impact'] = {
                            'scenario': result.scenario,
                            'impact_type': affected.get('impact_type'),
                            'impact_score': affected.get('impact_score'),
                            'reasoning': affected.get('reasoning'),
                            'valuation_change': affected.get('valuation_change'),
                            'applied_at': datetime.now().isoformat()
                        }
                        break
            
            # Add new connections
            edges = simulated_graph.get('edges', [])
            for connection in result.new_connections:
                new_edge = {
                    'id': f"sim_{connection['source']}_{connection['target']}",
                    'source': connection['source'].lower().replace(' ', ''),
                    'target': connection['target'].lower().replace(' ', ''),
                    'type': connection.get('connection_type', 'partnership'),
                    'weight': connection.get('strength', 50),
                    'simulation': {
                        'scenario': result.scenario,
                        'description': connection.get('description'),
                        'created_at': datetime.now().isoformat()
                    },
                    'style': {
                        'color': '#ff6b6b',  # Highlight simulated connections
                        'width': 3,
                        'dash': [5, 5]  # Dashed line for simulated connections
                    }
                }
                edges.append(new_edge)
            
            # Add simulation metadata to graph
            simulated_graph['simulation'] = {
                'scenario': result.scenario,
                'applied_at': datetime.now().isoformat(),
                'confidence': result.confidence,
                'timeline': result.timeline,
                'market_impact': result.market_impact,
                'reasoning': result.reasoning
            }
            
            return simulated_graph
            
        except Exception as e:
            logger.error(f"Error applying simulation to graph: {e}")
            return {}

# Predefined scenario templates for quick access
SCENARIO_TEMPLATES = [
    "What if {company1} acquires {company2}?",
    "What if {company1} partners with {company2}?", 
    "What if {company1} competes directly with {company2}?",
    "What if {company1} goes public?",
    "What if {company1} raises a $1B funding round?",
    "What if {company1} expands into {industry}?",
    "What if {company1} and {company2} merge?",
    "What if {company1} launches a competing product to {company2}?",
    "What if {company1} gets acquired by a tech giant?",
    "What if {company1} faces a major security breach?"
]
