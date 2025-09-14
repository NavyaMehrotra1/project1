"""
Graph Extraordinary Integration Service
Automatically generates extraordinary profiles for companies in graph_data_for_frontend.json
Uses AI-powered deep research to enhance company data with comprehensive profiles
"""

import asyncio
import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
import os

from services.extraordinary_profile_service import ExtraordinaryProfileService
from models.extraordinary_profile import ProfileGenerationRequest

logger = logging.getLogger(__name__)

class GraphExtraordinaryIntegrationService:
    def __init__(self, exa_api_key: str = None):
        # Load environment variables from .env file
        env_path = Path(__file__).parent.parent / ".env"
        if env_path.exists():
            load_dotenv(env_path)
            logger.info(f"Loaded environment variables from {env_path}")
        
        # Use provided key or load from environment
        actual_exa_key = exa_api_key or os.getenv("EXA_API_KEY")
        self.profile_service = ExtraordinaryProfileService(exa_api_key=actual_exa_key)
        self.graph_data_path = Path(__file__).parent.parent.parent / "data_agent" / "data_agent" / "output" / "graph_data_for_frontend.json"
        
    async def enhance_graph_with_extraordinary_profiles(self, 
                                                       max_companies: int = 10, 
                                                       force_regenerate: bool = False,
                                                       target_companies: List[str] = None) -> Dict[str, Any]:
        """
        Enhance graph data with comprehensive extraordinary profiles using AI research
        
        This is the core deep research functionality that:
        1. Uses Exa API to search across the entire web for company information
        2. Employs Claude AI to analyze and extract extraordinary achievements
        3. Identifies awards, recognitions, and industry rankings
        4. Discovers breakthrough innovations and technical feats
        5. Aggregates comprehensive statistics and metrics
        6. Integrates everything back into the graph data structure
        """
        logger.info(f"🔍 Starting deep research enhancement for graph companies")
        
        # Load current graph data
        graph_data = await self._load_graph_data()
        if not graph_data:
            return {"error": "Failed to load graph data"}
        
        # Select companies for research
        companies_to_research = self._select_companies_for_research(
            graph_data, max_companies, target_companies, force_regenerate
        )
        
        logger.info(f"📊 Selected {len(companies_to_research)} companies for deep research")
        
        research_results = {
            "companies_processed": 0,
            "profiles_generated": 0,
            "research_summary": {},
            "errors": []
        }
        
        # Process companies with deep research
        for company_node in companies_to_research:
            try:
                company_id = company_node["id"]
                company_data = company_node["data"]
                
                logger.info(f"🔬 Conducting deep research for {company_data['name']}")
                
                # Generate comprehensive profile using AI research
                profile_request = ProfileGenerationRequest(
                    company_id=company_id,
                    company_name=company_data["name"],
                    industry=company_data.get("industry", "Unknown"),
                    research_depth="comprehensive",  # Maximum depth research
                    force_regenerate=force_regenerate
                )
                
                # This is where the magic happens - AI-powered deep research
                profile = await self.profile_service.generate_extraordinary_profile(profile_request)
                
                # Integrate profile data into graph node
                enhanced_data = await self._integrate_profile_into_graph_node(company_data, profile)
                
                # Update the node in graph data
                for node in graph_data["nodes"]:
                    if node["id"] == company_id:
                        node["data"] = enhanced_data
                        break
                
                research_results["companies_processed"] += 1
                research_results["profiles_generated"] += 1
                
                # Track research quality metrics
                research_results["research_summary"][company_id] = {
                    "company_name": company_data["name"],
                    "articles_found": len(profile.notable_articles),
                    "recognitions_found": len(profile.recognitions),
                    "extraordinary_feats": len(profile.extraordinary_feats),
                    "overall_score": profile.overall_profile_score,
                    "research_depth_score": profile.research_depth_score,
                    "sources_analyzed": profile.total_sources_analyzed,
                    "ai_enhanced": bool(self.profile_service.claude_client)
                }
                
                logger.info(f"✅ Enhanced {company_data['name']} with extraordinary profile")
                logger.info(f"   📰 Articles: {len(profile.notable_articles)}")
                logger.info(f"   🏆 Recognitions: {len(profile.recognitions)}")
                logger.info(f"   🚀 Feats: {len(profile.extraordinary_feats)}")
                logger.info(f"   📊 Overall Score: {profile.overall_profile_score:.2f}")
                
            except Exception as e:
                error_msg = f"Error processing {company_data.get('name', company_id)}: {str(e)}"
                logger.error(error_msg)
                research_results["errors"].append(error_msg)
                continue
        
        # Save enhanced graph data
        await self._save_graph_data(graph_data)
        
        logger.info(f"🎉 Deep research enhancement completed!")
        logger.info(f"   Companies processed: {research_results['companies_processed']}")
        logger.info(f"   Profiles generated: {research_results['profiles_generated']}")
        logger.info(f"   Errors: {len(research_results['errors'])}")
        
        return research_results
    
    async def _load_graph_data(self) -> Optional[Dict[str, Any]]:
        """Load graph data from JSON file"""
        try:
            if self.graph_data_path.exists():
                with open(self.graph_data_path, 'r') as f:
                    return json.load(f)
            else:
                logger.error(f"Graph data file not found: {self.graph_data_path}")
                return None
        except Exception as e:
            logger.error(f"Error loading graph data: {e}")
            return None
    
    async def _save_graph_data(self, graph_data: Dict[str, Any]):
        """Save enhanced graph data back to JSON file"""
        try:
            # Create backup
            backup_path = self.graph_data_path.with_suffix('.backup.json')
            if self.graph_data_path.exists():
                import shutil
                shutil.copy2(self.graph_data_path, backup_path)
            
            # Save enhanced data
            with open(self.graph_data_path, 'w') as f:
                json.dump(graph_data, f, indent=2, default=str)
            
            logger.info(f"Enhanced graph data saved to {self.graph_data_path}")
            
        except Exception as e:
            logger.error(f"Error saving graph data: {e}")
            raise
    
    def _select_companies_for_research(self, 
                                     graph_data: Dict[str, Any], 
                                     max_companies: int,
                                     target_companies: List[str] = None,
                                     force_regenerate: bool = False) -> List[Dict[str, Any]]:
        """Select companies for deep research based on criteria"""
        nodes = graph_data.get("nodes", [])
        
        # Filter to company nodes only
        company_nodes = [node for node in nodes if node.get("data", {}).get("name")]
        
        # If specific companies are targeted
        if target_companies:
            selected = [node for node in company_nodes 
                       if node["id"] in target_companies or 
                          node.get("data", {}).get("name") in target_companies]
            return selected[:max_companies]
        
        # Select companies that need research
        candidates = []
        for node in company_nodes:
            data = node.get("data", {})
            
            # Skip if already has recent extraordinary profile (unless forcing)
            if not force_regenerate and data.get("extraordinary_profile_generated"):
                last_update = data.get("last_extraordinary_update")
                if last_update:
                    try:
                        update_time = datetime.fromisoformat(last_update.replace('Z', '+00:00'))
                        if (datetime.now() - update_time).days < 30:  # Skip if updated within 30 days
                            continue
                    except:
                        pass
            
            # Prioritize high-value companies
            priority_score = 0
            
            # Higher valuation = higher priority
            valuation = data.get("valuation", 0)
            if valuation > 10000000000:  # $10B+
                priority_score += 10
            elif valuation > 1000000000:  # $1B+
                priority_score += 5
            
            # More deal activity = higher priority
            deal_activity = data.get("deal_activity_count", 0)
            priority_score += min(deal_activity, 10)
            
            # Well-known companies get priority
            well_known = ["stripe", "openai", "airbnb", "uber", "spotify", "dropbox", "reddit"]
            if node["id"] in well_known:
                priority_score += 15
            
            candidates.append((node, priority_score))
        
        # Sort by priority and take top candidates
        candidates.sort(key=lambda x: x[1], reverse=True)
        return [node for node, _ in candidates[:max_companies]]
    
    async def _integrate_profile_into_graph_node(self, 
                                               company_data: Dict[str, Any], 
                                               profile) -> Dict[str, Any]:
        """
        Integrate extraordinary profile data into graph node data
        This transforms the deep research results into graph-compatible format
        """
        enhanced_data = company_data.copy()
        
        # Core extraordinary profile data
        enhanced_data.update({
            "extraordinary_profile_generated": True,
            "last_extraordinary_update": datetime.now().isoformat(),
            "extraordinary_profile_score": profile.overall_profile_score,
            "research_depth_score": profile.research_depth_score,
            "data_completeness_score": profile.data_completeness_score,
        })
        
        # Update extraordinary score with AI-calculated score
        enhanced_data["extraordinary_score"] = min(100, max(0, int(profile.overall_profile_score * 100)))
        
        # Notable articles summary
        if profile.notable_articles:
            enhanced_data["notable_articles"] = [
                {
                    "title": article.title,
                    "source": article.source,
                    "url": article.url,
                    "summary": article.summary[:200] + "..." if len(article.summary) > 200 else article.summary,
                    "relevance_score": article.relevance_score,
                    "sentiment": article.sentiment,
                    "key_quotes": article.key_quotes[:2]  # Top 2 quotes
                }
                for article in profile.notable_articles[:10]  # Top 10 articles
            ]
            enhanced_data["article_quality_score"] = profile.article_quality_score
        
        # Recognitions and awards
        if profile.recognitions:
            enhanced_data["recognitions"] = [
                {
                    "title": recognition.title,
                    "organization": recognition.organization,
                    "year": recognition.year,
                    "type": recognition.recognition_type.value,
                    "description": recognition.description[:150] + "..." if len(recognition.description) > 150 else recognition.description,
                    "significance_score": recognition.significance_score,
                    "rank_position": recognition.rank_position
                }
                for recognition in profile.recognitions[:8]  # Top 8 recognitions
            ]
            enhanced_data["recognition_prestige_score"] = profile.recognition_prestige_score
        
        # Extraordinary feats
        if profile.extraordinary_feats:
            enhanced_data["extraordinary_feats"] = [
                {
                    "title": feat.title,
                    "description": feat.description[:200] + "..." if len(feat.description) > 200 else feat.description,
                    "type": feat.feat_type.value,
                    "impact": feat.impact_description[:150] + "..." if len(feat.impact_description) > 150 else feat.impact_description,
                    "impressiveness_score": feat.impressiveness_score,
                    "metrics": feat.metrics
                }
                for feat in profile.extraordinary_feats[:6]  # Top 6 feats
            ]
            enhanced_data["feat_impressiveness_score"] = profile.feat_impressiveness_score
        
        # Enhanced company statistics
        stats = profile.company_stats
        if stats:
            enhanced_stats = {}
            
            # Financial metrics
            if stats.valuation:
                enhanced_stats["ai_researched_valuation"] = stats.valuation
            if stats.revenue:
                enhanced_stats["ai_researched_revenue"] = stats.revenue
            if stats.funding_raised:
                enhanced_stats["ai_researched_funding"] = stats.funding_raised
            
            # Growth metrics
            if stats.employee_count:
                enhanced_stats["ai_researched_employees"] = stats.employee_count
            if stats.user_count:
                enhanced_stats["ai_researched_users"] = stats.user_count
            
            # Performance metrics
            if stats.customer_satisfaction:
                enhanced_stats["customer_satisfaction"] = stats.customer_satisfaction
            
            if enhanced_stats:
                enhanced_data["ai_researched_stats"] = enhanced_stats
        
        # Research metadata
        enhanced_data["research_metadata"] = {
            "sources_analyzed": profile.total_sources_analyzed,
            "queries_performed": len(profile.research_queries_performed),
            "ai_enhanced": bool(self.profile_service.claude_client),
            "exa_api_used": bool(self.profile_service.exa_client),
            "research_timestamp": datetime.now().isoformat()
        }
        
        # Summary for quick display
        enhanced_data["extraordinary_summary"] = self._generate_extraordinary_summary(profile)
        
        return enhanced_data
    
    def _generate_extraordinary_summary(self, profile) -> str:
        """Generate a concise summary of what makes this company extraordinary"""
        summary_parts = []
        
        # Top achievement
        if profile.extraordinary_feats:
            top_feat = max(profile.extraordinary_feats, key=lambda x: x.impressiveness_score)
            summary_parts.append(f"🚀 {top_feat.title}")
        
        # Top recognition
        if profile.recognitions:
            top_recognition = max(profile.recognitions, key=lambda x: x.significance_score)
            summary_parts.append(f"🏆 {top_recognition.title} ({top_recognition.organization})")
        
        # Key stats
        stats = profile.company_stats
        if stats.valuation and stats.valuation > 1000000000:
            summary_parts.append(f"💰 ${stats.valuation/1000000000:.1f}B valuation")
        
        if stats.employee_count and stats.employee_count > 1000:
            summary_parts.append(f"👥 {stats.employee_count:,} employees")
        
        # Article highlights
        if profile.notable_articles:
            high_quality_articles = [a for a in profile.notable_articles if a.relevance_score > 0.7]
            if high_quality_articles:
                summary_parts.append(f"📰 {len(high_quality_articles)} high-impact articles")
        
        return " | ".join(summary_parts[:4])  # Keep it concise

# Convenience functions for easy usage
async def enhance_all_companies(max_companies: int = 10, exa_api_key: str = None) -> Dict[str, Any]:
    """Enhance all companies in graph with extraordinary profiles"""
    service = GraphExtraordinaryIntegrationService(exa_api_key=exa_api_key)
    return await service.enhance_graph_with_extraordinary_profiles(max_companies=max_companies)

async def enhance_specific_companies(company_names: List[str], exa_api_key: str = None) -> Dict[str, Any]:
    """Enhance specific companies with extraordinary profiles"""
    service = GraphExtraordinaryIntegrationService(exa_api_key=exa_api_key)
    return await service.enhance_graph_with_extraordinary_profiles(
        target_companies=company_names,
        max_companies=len(company_names)
    )
