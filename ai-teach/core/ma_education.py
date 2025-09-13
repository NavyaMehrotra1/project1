"""
Interactive M&A Education Module
Provides contextual explanations and real-world examples for M&A concepts.
"""

import json
import asyncio
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import asdict
from datetime import datetime
from models.learning_models import (
    LearningLevel, UserProfile, Concept, ExplanationRequest
)
from services.claude_service import ClaudeService


class MAEducationModule:
    """Interactive M&A education with contextual explanations and real examples"""
    
    def __init__(self, claude_service: ClaudeService):
        self.claude_service = claude_service
        self.ma_terminology = self._load_ma_terminology()
        self.case_studies = self._load_case_studies()
        self.industry_contexts = self._load_industry_contexts()
    
    def _load_ma_terminology(self) -> Dict[str, Dict[str, Any]]:
        """Load comprehensive M&A terminology with explanations"""
        return {
            "merger": {
                "definition": "A combination of two companies where they agree to go forward as a single new company",
                "beginner_explanation": "When two companies decide to join together and become one bigger company",
                "intermediate_explanation": "A strategic combination where two companies of similar size combine to form a new entity",
                "expert_explanation": "A transaction where two companies combine through share exchange, creating synergies and market consolidation",
                "examples": ["Exxon + Mobil", "Disney + ABC", "AT&T + Time Warner"],
                "related_terms": ["acquisition", "consolidation", "horizontal merger"]
            },
            
            "acquisition": {
                "definition": "When one company purchases most or all of another company's shares to gain control",
                "beginner_explanation": "When a bigger company buys a smaller company to own it completely",
                "intermediate_explanation": "A transaction where one company (acquirer) purchases another company (target) to gain control",
                "expert_explanation": "Strategic purchase of target company assets or equity to achieve operational control and integration",
                "examples": ["Facebook + Instagram", "Amazon + Whole Foods", "Microsoft + LinkedIn"],
                "related_terms": ["takeover", "buyout", "strategic acquisition"]
            },
            
            "due_diligence": {
                "definition": "Investigation or audit of a potential investment or product to confirm facts",
                "beginner_explanation": "Checking everything about a company before buying it, like inspecting a house before purchase",
                "intermediate_explanation": "Comprehensive review of target company's financials, operations, and legal status",
                "expert_explanation": "Systematic risk assessment covering financial, legal, commercial, and operational aspects of target",
                "examples": ["Financial DD", "Legal DD", "Commercial DD", "IT DD"],
                "related_terms": ["investigation", "audit", "risk assessment"]
            },
            
            "synergy": {
                "definition": "The concept that the value of combined companies will be greater than the sum of separate parts",
                "beginner_explanation": "When two companies work better together than apart, like 1+1=3",
                "intermediate_explanation": "Cost savings and revenue enhancements achieved through combining operations",
                "expert_explanation": "Quantifiable value creation through operational efficiencies, market expansion, and strategic advantages",
                "examples": ["Cost synergies", "Revenue synergies", "Tax synergies"],
                "related_terms": ["value creation", "economies of scale", "cross-selling"]
            },
            
            "valuation": {
                "definition": "The analytical process of determining the current worth of an asset or company",
                "beginner_explanation": "Figuring out how much a company is worth, like appraising a house",
                "intermediate_explanation": "Using financial models to determine fair value for M&A transactions",
                "expert_explanation": "Application of DCF, comparable company, and precedent transaction methodologies",
                "examples": ["DCF analysis", "Trading multiples", "Transaction multiples"],
                "related_terms": ["enterprise value", "equity value", "fair value"]
            },
            
            "ebitda": {
                "definition": "Earnings Before Interest, Taxes, Depreciation, and Amortization",
                "beginner_explanation": "A way to measure how much money a company makes from its main business",
                "intermediate_explanation": "Key profitability metric that excludes financing and accounting decisions",
                "expert_explanation": "Normalized earnings metric used for valuation multiples and debt capacity analysis",
                "examples": ["EBITDA margin", "EV/EBITDA multiple", "EBITDA growth"],
                "related_terms": ["operating income", "cash flow", "normalized earnings"]
            }
        }
    
    def _load_case_studies(self) -> Dict[str, Dict[str, Any]]:
        """Load real M&A case studies for different learning levels"""
        return {
            "disney_pixar": {
                "title": "Disney Acquires Pixar (2006)",
                "deal_value": 7.4,  # billion USD
                "deal_type": "acquisition",
                "industry": "entertainment",
                "difficulty": "beginner",
                "summary": "Disney acquired Pixar to revitalize its animation division and gain access to cutting-edge technology",
                "key_concepts": ["strategic acquisition", "creative synergies", "cultural integration"],
                "learning_points": [
                    "Strategic rationale: Disney needed to modernize its animation capabilities",
                    "Cultural challenges: Integrating creative teams with different work styles",
                    "Success factors: Maintaining Pixar's creative independence while leveraging Disney's distribution"
                ],
                "financial_details": {
                    "purchase_price": "$7.4 billion",
                    "payment_method": "All stock",
                    "premium": "~4% premium to market price"
                },
                "outcomes": [
                    "Successful integration of creative teams",
                    "Multiple successful film releases",
                    "Technology transfer to Disney animation"
                ]
            },
            
            "microsoft_linkedin": {
                "title": "Microsoft Acquires LinkedIn (2016)",
                "deal_value": 26.2,
                "deal_type": "acquisition", 
                "industry": "technology",
                "difficulty": "intermediate",
                "summary": "Microsoft's largest acquisition to expand into professional networking and enterprise services",
                "key_concepts": ["strategic fit", "platform integration", "enterprise value"],
                "learning_points": [
                    "Strategic rationale: Expanding Microsoft's cloud and productivity ecosystem",
                    "Integration approach: Maintaining LinkedIn as independent platform",
                    "Synergy realization: Cross-selling opportunities and data integration"
                ],
                "financial_details": {
                    "purchase_price": "$26.2 billion",
                    "payment_method": "All cash",
                    "premium": "49.5% premium to closing price"
                },
                "outcomes": [
                    "Successful revenue growth acceleration",
                    "Integration with Microsoft Office suite",
                    "Expansion of enterprise customer base"
                ]
            },
            
            "broadcom_qualcomm": {
                "title": "Broadcom's Failed Bid for Qualcomm (2018)",
                "deal_value": 117,
                "deal_type": "hostile_takeover",
                "industry": "semiconductors",
                "difficulty": "expert",
                "summary": "Hostile takeover attempt blocked by US government on national security grounds",
                "key_concepts": ["hostile takeover", "regulatory risk", "national security"],
                "learning_points": [
                    "Regulatory complexity: CFIUS review and national security concerns",
                    "Hostile tactics: Proxy fight and board replacement strategy",
                    "Market dynamics: Consolidation pressures in semiconductor industry"
                ],
                "financial_details": {
                    "proposed_price": "$117 billion",
                    "payment_method": "$60 cash + $57 stock",
                    "premium": "28% premium to unaffected price"
                },
                "outcomes": [
                    "Deal blocked by US Treasury/CFIUS",
                    "Broadcom relocated headquarters to US",
                    "Increased focus on regulatory approval processes"
                ]
            }
        }
    
    def _load_industry_contexts(self) -> Dict[str, Dict[str, Any]]:
        """Load industry-specific M&A contexts and trends"""
        return {
            "technology": {
                "key_drivers": ["Digital transformation", "Platform consolidation", "Talent acquisition"],
                "common_deal_types": ["Strategic acquisitions", "Acqui-hires", "Platform integrations"],
                "valuation_metrics": ["Revenue multiples", "User metrics", "Technology value"],
                "integration_challenges": ["Cultural fit", "Technology integration", "Talent retention"],
                "examples": ["Microsoft + GitHub", "Salesforce + Slack", "Adobe + Figma"]
            },
            
            "healthcare": {
                "key_drivers": ["Cost reduction", "Scale economies", "Regulatory compliance"],
                "common_deal_types": ["Horizontal mergers", "Vertical integration", "Portfolio optimization"],
                "valuation_metrics": ["EBITDA multiples", "Revenue per bed", "Patient volume"],
                "integration_challenges": ["Regulatory approval", "System integration", "Care quality"],
                "examples": ["CVS + Aetna", "UnitedHealth + Optum", "Anthem + Cigna (failed)"]
            },
            
            "financial_services": {
                "key_drivers": ["Digital disruption", "Regulatory efficiency", "Market expansion"],
                "common_deal_types": ["Bank mergers", "Fintech acquisitions", "Cross-border deals"],
                "valuation_metrics": ["Price-to-book", "Price-to-tangible book", "Deposit premiums"],
                "integration_challenges": ["Regulatory approval", "System conversion", "Customer retention"],
                "examples": ["JPMorgan + Bear Stearns", "Wells Fargo + Wachovia", "PayPal + Venmo"]
            }
        }
    
    async def explain_concept(self, term: str, user_profile: UserProfile, 
                            context: str = "", graph_data: Optional[Dict] = None) -> str:
        """Provide adaptive explanation of M&A concept"""
        
        term_lower = term.lower()
        
        # Check if term exists in our terminology
        if term_lower in self.ma_terminology:
            term_data = self.ma_terminology[term_lower]
            
            # Get level-appropriate explanation
            level_key = f"{user_profile.current_level.value}_explanation"
            explanation = term_data.get(level_key, term_data["definition"])
            
            print(f"\n📖 {term.title()}")
            print("=" * 40)
            print(f"\n{explanation}")
            
            # Add examples for beginners and intermediates
            if user_profile.current_level in [LearningLevel.BEGINNER, LearningLevel.INTERMEDIATE]:
                if term_data.get("examples"):
                    print(f"\n💡 Examples:")
                    for example in term_data["examples"][:3]:
                        print(f"   • {example}")
            
            # Add related terms for all levels
            if term_data.get("related_terms"):
                print(f"\n🔗 Related Terms: {', '.join(term_data['related_terms'])}")
            
            # Get AI-enhanced explanation with context
            enhanced_explanation = await self._get_enhanced_explanation(
                term, explanation, user_profile, context, graph_data
            )
            
            if enhanced_explanation:
                print(f"\n🤖 AI Insight:")
                print(enhanced_explanation)
            
            return explanation
        
        else:
            # Use AI to explain unknown terms
            request = ExplanationRequest(
                user_id=user_profile.user_id,
                question=f"What is '{term}' in M&A context?",
                context=context,
                user_level=user_profile.current_level,
                graph_data=graph_data
            )
            
            result = await self.claude_service.generate_explanation(request)
            
            print(f"\n📖 {term.title()}")
            print("=" * 40)
            print(f"\n{result['explanation']}")
            
            return result['explanation']
    
    async def _get_enhanced_explanation(self, term: str, base_explanation: str, 
                                      user_profile: UserProfile, context: str,
                                      graph_data: Optional[Dict]) -> str:
        """Get AI-enhanced explanation with real-world context"""
        
        request = ExplanationRequest(
            user_id=user_profile.user_id,
            question=f"Provide additional context and real-world examples for '{term}' in M&A",
            context=f"Base explanation: {base_explanation}. Additional context: {context}",
            user_level=user_profile.current_level,
            preferred_style="example_heavy",
            graph_data=graph_data
        )
        
        try:
            result = await self.claude_service.generate_explanation(request)
            return result['explanation']
        except Exception:
            return ""
    
    async def explore_case_study(self, case_id: str, user_profile: UserProfile) -> None:
        """Explore M&A case study with adaptive depth"""
        
        if case_id not in self.case_studies:
            print(f"❌ Case study '{case_id}' not found.")
            return
        
        case = self.case_studies[case_id]
        
        print(f"\n📊 Case Study: {case['title']}")
        print("=" * 50)
        print(f"💰 Deal Value: ${case['deal_value']:.1f} billion")
        print(f"🏢 Industry: {case['industry'].title()}")
        print(f"📈 Deal Type: {case['deal_type'].replace('_', ' ').title()}")
        
        print(f"\n📝 Summary:")
        print(f"{case['summary']}")
        
        # Adaptive detail level
        if user_profile.current_level == LearningLevel.BEGINNER:
            await self._present_beginner_case_analysis(case, user_profile)
        elif user_profile.current_level == LearningLevel.INTERMEDIATE:
            await self._present_intermediate_case_analysis(case, user_profile)
        else:
            await self._present_expert_case_analysis(case, user_profile)
        
        # Interactive Q&A
        await self._case_study_qa(case, user_profile)
    
    async def _present_beginner_case_analysis(self, case: Dict, user_profile: UserProfile):
        """Present case study for beginners with simple concepts"""
        print(f"\n🎯 Key Learning Points:")
        for point in case['learning_points'][:2]:  # Limit for beginners
            print(f"   • {point}")
        
        print(f"\n💡 Why This Deal Happened:")
        print(f"   The companies wanted to work together to become stronger and more successful.")
        
        if case.get('outcomes'):
            print(f"\n✅ What Happened After:")
            for outcome in case['outcomes'][:2]:
                print(f"   • {outcome}")
    
    async def _present_intermediate_case_analysis(self, case: Dict, user_profile: UserProfile):
        """Present case study for intermediate learners"""
        print(f"\n🎯 Key Learning Points:")
        for point in case['learning_points']:
            print(f"   • {point}")
        
        if case.get('financial_details'):
            print(f"\n💰 Financial Details:")
            for key, value in case['financial_details'].items():
                print(f"   • {key.replace('_', ' ').title()}: {value}")
        
        print(f"\n📈 M&A Concepts Demonstrated:")
        for concept in case['key_concepts']:
            print(f"   • {concept.replace('_', ' ').title()}")
        
        if case.get('outcomes'):
            print(f"\n📊 Results:")
            for outcome in case['outcomes']:
                print(f"   • {outcome}")
    
    async def _present_expert_case_analysis(self, case: Dict, user_profile: UserProfile):
        """Present comprehensive case study for experts"""
        print(f"\n🎯 Strategic Analysis:")
        for point in case['learning_points']:
            print(f"   • {point}")
        
        if case.get('financial_details'):
            print(f"\n💰 Deal Structure:")
            for key, value in case['financial_details'].items():
                print(f"   • {key.replace('_', ' ').title()}: {value}")
        
        print(f"\n🧠 Advanced Concepts:")
        for concept in case['key_concepts']:
            print(f"   • {concept.replace('_', ' ').title()}")
        
        # Get AI analysis for expert insights
        request = ExplanationRequest(
            user_id=user_profile.user_id,
            question=f"Provide expert-level strategic analysis of the {case['title']} case study",
            context=f"Case details: {json.dumps(case, indent=2)}",
            user_level=LearningLevel.EXPERT
        )
        
        try:
            result = await self.claude_service.generate_explanation(request)
            print(f"\n🎓 Expert Analysis:")
            print(result['explanation'])
        except Exception:
            pass
        
        if case.get('outcomes'):
            print(f"\n📊 Post-Deal Performance:")
            for outcome in case['outcomes']:
                print(f"   • {outcome}")
    
    async def _case_study_qa(self, case: Dict, user_profile: UserProfile):
        """Interactive Q&A for case study"""
        print(f"\n❓ Discussion Questions:")
        
        # Generate level-appropriate questions
        if user_profile.current_level == LearningLevel.BEGINNER:
            questions = [
                f"What do you think was the main reason for this deal?",
                f"Do you think this was a good decision? Why?"
            ]
        elif user_profile.current_level == LearningLevel.INTERMEDIATE:
            questions = [
                f"What were the key success factors for this transaction?",
                f"What risks do you think the companies faced?"
            ]
        else:
            questions = [
                f"How would you have structured this deal differently?",
                f"What alternative strategies could have achieved similar objectives?"
            ]
        
        for i, question in enumerate(questions, 1):
            print(f"\n{i}. {question}")
            response = input("Your thoughts: ").strip()
            
            if response:
                # Get AI feedback
                feedback_request = ExplanationRequest(
                    user_id=user_profile.user_id,
                    question=f"Provide feedback on this response to '{question}': {response}",
                    context=f"Case study context: {case['title']}",
                    user_level=user_profile.current_level
                )
                
                try:
                    feedback_result = await self.claude_service.generate_explanation(feedback_request)
                    print(f"\n💭 Feedback: {feedback_result['explanation']}")
                except Exception:
                    print(f"\n💭 Great insights! That's an important perspective to consider.")
    
    async def get_industry_context(self, industry: str, user_profile: UserProfile) -> str:
        """Provide industry-specific M&A context"""
        
        industry_lower = industry.lower()
        
        if industry_lower in self.industry_contexts:
            context = self.industry_contexts[industry_lower]
            
            print(f"\n🏭 M&A in {industry.title()} Industry")
            print("=" * 40)
            
            print(f"\n🎯 Key Drivers:")
            for driver in context['key_drivers']:
                print(f"   • {driver}")
            
            print(f"\n📋 Common Deal Types:")
            for deal_type in context['common_deal_types']:
                print(f"   • {deal_type}")
            
            if user_profile.current_level != LearningLevel.BEGINNER:
                print(f"\n📊 Valuation Metrics:")
                for metric in context['valuation_metrics']:
                    print(f"   • {metric}")
                
                print(f"\n⚠️  Integration Challenges:")
                for challenge in context['integration_challenges']:
                    print(f"   • {challenge}")
            
            print(f"\n🌟 Notable Examples:")
            for example in context['examples']:
                print(f"   • {example}")
            
            return f"Industry context for {industry} provided"
        
        else:
            # Use AI for unknown industries
            request = ExplanationRequest(
                user_id=user_profile.user_id,
                question=f"Explain M&A trends and characteristics in the {industry} industry",
                context="Focus on key drivers, common deal types, and notable examples",
                user_level=user_profile.current_level
            )
            
            result = await self.claude_service.generate_explanation(request)
            
            print(f"\n🏭 M&A in {industry.title()} Industry")
            print("=" * 40)
            print(f"\n{result['explanation']}")
            
            return result['explanation']
    
    def list_available_case_studies(self, user_profile: UserProfile) -> List[str]:
        """List case studies appropriate for user's level"""
        appropriate_cases = []
        
        for case_id, case in self.case_studies.items():
            case_difficulty = case.get('difficulty', 'intermediate')
            
            if user_profile.current_level == LearningLevel.BEGINNER and case_difficulty == 'beginner':
                appropriate_cases.append(case_id)
            elif user_profile.current_level == LearningLevel.INTERMEDIATE and case_difficulty in ['beginner', 'intermediate']:
                appropriate_cases.append(case_id)
            elif user_profile.current_level == LearningLevel.EXPERT:
                appropriate_cases.append(case_id)
        
        return appropriate_cases
    
    def list_available_industries(self) -> List[str]:
        """List available industry contexts"""
        return list(self.industry_contexts.keys())
