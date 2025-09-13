"""
Claude API Service for AI-Powered Explanations
Handles communication with Anthropic's Claude API for educational content generation.
"""

import os
import json
import asyncio
from typing import Dict, List, Optional, Any
from dataclasses import asdict
import anthropic
from models.learning_models import (
    LearningLevel, ExplanationRequest, UserProfile, Concept
)


class ClaudeService:
    """Service for generating AI-powered educational explanations using Claude"""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize Claude service with API key"""
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable is required")
        
        self.client = anthropic.Anthropic(api_key=self.api_key)
        
        # Learning level prompts
        self.level_prompts = {
            LearningLevel.BEGINNER: {
                "style": "Use simple language, avoid jargon, provide step-by-step explanations with analogies",
                "depth": "Basic concepts with real-world examples",
                "tone": "Encouraging and patient"
            },
            LearningLevel.INTERMEDIATE: {
                "style": "Use moderate technical language, explain key terms, provide context",
                "depth": "Detailed explanations with industry examples",
                "tone": "Professional but accessible"
            },
            LearningLevel.EXPERT: {
                "style": "Use technical language, assume knowledge of fundamentals, focus on nuances",
                "depth": "Advanced analysis with strategic implications",
                "tone": "Direct and comprehensive"
            }
        }
    
    async def generate_explanation(self, request: ExplanationRequest) -> Dict[str, Any]:
        """Generate an adaptive explanation based on user level and context"""
        
        # Build the prompt based on user level
        level_config = self.level_prompts[request.user_level]
        
        system_prompt = f"""You are an expert M&A (Mergers & Acquisitions) teacher. Your role is to provide educational explanations that are:

LEARNING LEVEL: {request.user_level.value.upper()}
- Style: {level_config['style']}
- Depth: {level_config['depth']}
- Tone: {level_config['tone']}

TEACHING PRINCIPLES:
1. Always assess if the user understands prerequisite concepts
2. Build knowledge incrementally from basics if needed
3. Use real M&A examples and case studies
4. Connect concepts to practical applications
5. Encourage questions and deeper exploration

RESPONSE FORMAT:
- Start with a brief concept check if needed
- Provide the main explanation
- Include relevant examples
- Suggest follow-up learning topics
- Ask a question to check understanding"""

        user_prompt = f"""
Question: {request.question}

Context: {request.context}

User Learning Level: {request.user_level.value}
Preferred Style: {request.preferred_style}

{self._format_graph_context(request.graph_data) if request.graph_data else ""}

Please provide an educational explanation tailored to this user's level.
"""

        try:
            response = await asyncio.to_thread(
                self.client.messages.create,
                model="claude-3-sonnet-20240229",
                max_tokens=1500,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_prompt}
                ]
            )
            
            explanation = response.content[0].text
            
            return {
                "explanation": explanation,
                "user_level": request.user_level.value,
                "confidence": 0.9,  # Could be enhanced with actual confidence scoring
                "follow_up_topics": self._extract_follow_up_topics(explanation),
                "prerequisite_check": self._needs_prerequisite_check(request.question, request.user_level)
            }
            
        except Exception as e:
            return {
                "explanation": f"I apologize, but I encountered an error generating the explanation: {str(e)}",
                "user_level": request.user_level.value,
                "confidence": 0.0,
                "follow_up_topics": [],
                "prerequisite_check": False,
                "error": str(e)
            }
    
    async def assess_background_knowledge(self, user_responses: List[str], questions: List[str]) -> Dict[str, Any]:
        """Assess user's background knowledge based on their responses"""
        
        system_prompt = """You are an expert M&A educator assessing a student's background knowledge. 
        
        Analyze the user's responses to determine:
        1. Their current knowledge level (beginner/intermediate/expert)
        2. Specific knowledge gaps
        3. Strengths they can build upon
        4. Recommended starting concepts
        
        Provide a detailed assessment with specific recommendations."""
        
        user_prompt = f"""
        Assessment Questions and User Responses:
        
        {self._format_qa_pairs(questions, user_responses)}
        
        Please provide a comprehensive background assessment.
        """
        
        try:
            response = await asyncio.to_thread(
                self.client.messages.create,
                model="claude-3-sonnet-20240229",
                max_tokens=1000,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_prompt}
                ]
            )
            
            assessment = response.content[0].text
            
            # Extract structured data from assessment
            level = self._extract_learning_level(assessment)
            gaps = self._extract_knowledge_gaps(assessment)
            strengths = self._extract_strengths(assessment)
            
            return {
                "assessment": assessment,
                "recommended_level": level,
                "knowledge_gaps": gaps,
                "strengths": strengths,
                "confidence": 0.85
            }
            
        except Exception as e:
            return {
                "assessment": f"Error in assessment: {str(e)}",
                "recommended_level": LearningLevel.BEGINNER,
                "knowledge_gaps": [],
                "strengths": [],
                "confidence": 0.0,
                "error": str(e)
            }
    
    async def generate_scenario_explanation(self, scenario_data: Dict[str, Any], user_level: LearningLevel) -> str:
        """Generate educational explanation for M&A scenarios"""
        
        level_config = self.level_prompts[user_level]
        
        system_prompt = f"""You are an M&A educator explaining real-world scenarios. 
        
        Teaching Level: {user_level.value}
        Style: {level_config['style']}
        
        Explain the scenario focusing on:
        1. Key M&A concepts demonstrated
        2. Strategic rationale
        3. Financial implications
        4. Potential challenges
        5. Learning takeaways
        """
        
        user_prompt = f"""
        M&A Scenario: {json.dumps(scenario_data, indent=2)}
        
        Please provide an educational explanation of this scenario.
        """
        
        try:
            response = await asyncio.to_thread(
                self.client.messages.create,
                model="claude-3-sonnet-20240229",
                max_tokens=1200,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_prompt}
                ]
            )
            
            return response.content[0].text
            
        except Exception as e:
            return f"Error generating scenario explanation: {str(e)}"
    
    def _format_graph_context(self, graph_data: Dict[str, Any]) -> str:
        """Format graph data for context in explanations"""
        if not graph_data:
            return ""
        
        context = "\nRELEVANT GRAPH DATA:\n"
        if 'nodes' in graph_data:
            context += f"Companies: {', '.join([node.get('name', 'Unknown') for node in graph_data['nodes'][:5]])}\n"
        if 'edges' in graph_data:
            context += f"Relationships: {len(graph_data['edges'])} connections\n"
        
        return context
    
    def _format_qa_pairs(self, questions: List[str], responses: List[str]) -> str:
        """Format question-answer pairs for assessment"""
        pairs = []
        for i, (q, r) in enumerate(zip(questions, responses)):
            pairs.append(f"Q{i+1}: {q}\nA{i+1}: {r}\n")
        return "\n".join(pairs)
    
    def _extract_follow_up_topics(self, explanation: str) -> List[str]:
        """Extract potential follow-up topics from explanation"""
        # Simple keyword extraction - could be enhanced with NLP
        topics = []
        keywords = ["merger", "acquisition", "valuation", "due diligence", "synergy", "integration"]
        
        for keyword in keywords:
            if keyword.lower() in explanation.lower():
                topics.append(keyword.title())
        
        return topics[:3]  # Return top 3
    
    def _needs_prerequisite_check(self, question: str, level: LearningLevel) -> bool:
        """Determine if prerequisite concepts should be checked"""
        advanced_terms = ["dcf", "wacc", "ebitda", "synergy", "accretion", "dilution"]
        
        if level == LearningLevel.BEGINNER:
            return any(term in question.lower() for term in advanced_terms)
        
        return False
    
    def _extract_learning_level(self, assessment: str) -> LearningLevel:
        """Extract recommended learning level from assessment text"""
        assessment_lower = assessment.lower()
        
        if "expert" in assessment_lower or "advanced" in assessment_lower:
            return LearningLevel.EXPERT
        elif "intermediate" in assessment_lower or "moderate" in assessment_lower:
            return LearningLevel.INTERMEDIATE
        else:
            return LearningLevel.BEGINNER
    
    def _extract_knowledge_gaps(self, assessment: str) -> List[str]:
        """Extract knowledge gaps from assessment"""
        # Simple extraction - could be enhanced
        gaps = []
        if "financial" in assessment.lower():
            gaps.append("Financial Analysis")
        if "valuation" in assessment.lower():
            gaps.append("Valuation Methods")
        if "legal" in assessment.lower():
            gaps.append("Legal Frameworks")
        
        return gaps
    
    def _extract_strengths(self, assessment: str) -> List[str]:
        """Extract strengths from assessment"""
        # Simple extraction - could be enhanced
        strengths = []
        if "business" in assessment.lower():
            strengths.append("Business Acumen")
        if "analytical" in assessment.lower():
            strengths.append("Analytical Skills")
        
        return strengths
