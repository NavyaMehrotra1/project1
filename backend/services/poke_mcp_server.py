"""
Poke MCP Server for M&A Intelligence Automations
Model Context Protocol server that enables intelligent M&A deal monitoring and alerts
"""

import asyncio
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import aiohttp
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os

from .tandemn_integration_service import TandemnDistributedService, enhance_ma_events_with_tandemn
from .ma_intelligence_service import MAIntelligenceService
from .dynamic_confidence_service import DynamicConfidenceService

logger = logging.getLogger(__name__)

class PokeMessage(BaseModel):
    message: str
    priority: str = "normal"  # "low", "normal", "high", "urgent"
    automation_type: str = "deal_alert"

class MAAutomationTrigger(BaseModel):
    trigger_type: str  # "new_deal", "confidence_change", "market_sentiment", "competitor_activity"
    companies: List[str] = []
    deal_value_threshold: Optional[float] = None
    confidence_threshold: Optional[float] = None
    sentiment_threshold: Optional[float] = None

class PokeMCPServer:
    """
    MCP Server for Poke that provides intelligent M&A automation capabilities
    Combines Tandemn distributed inference with real-time deal monitoring
    """
    
    def __init__(self, poke_api_key: str, tandemn_api_key: str, exa_api_key: str):
        self.poke_api_key = poke_api_key
        self.tandemn_api_key = tandemn_api_key
        self.exa_api_key = exa_api_key
        
        # Initialize services
        self.ma_service = MAIntelligenceService(exa_api_key)
        self.confidence_service = DynamicConfidenceService()
        
        # Active automations storage
        self.active_automations: Dict[str, MAAutomationTrigger] = {}
        self.last_check_time = datetime.now()
        
    async def send_poke_message(self, message: str, priority: str = "normal") -> bool:
        """Send message to Poke using their API"""
        try:
            headers = {
                "Authorization": f"Bearer {self.poke_api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "message": message
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    "https://poke.com/api/v1/inbound-sms/webhook",
                    headers=headers,
                    json=payload
                ) as response:
                    if response.status == 200:
                        logger.info(f"Successfully sent Poke message: {message[:50]}...")
                        return True
                    else:
                        logger.error(f"Failed to send Poke message: {response.status}")
                        return False
                        
        except Exception as e:
            logger.error(f"Error sending Poke message: {str(e)}")
            return False

    async def create_deal_monitoring_automation(
        self, 
        automation_id: str, 
        trigger: MAAutomationTrigger
    ) -> Dict[str, Any]:
        """
        Create intelligent deal monitoring automation
        Uses Tandemn for distributed processing and Poke for notifications
        """
        
        # Store automation
        self.active_automations[automation_id] = trigger
        
        # Send confirmation message
        companies_str = ", ".join(trigger.companies) if trigger.companies else "all companies"
        await self.send_poke_message(
            f"🤖 M&A Automation Active: Monitoring {companies_str} for {trigger.trigger_type}. "
            f"Thresholds: Deal>${trigger.deal_value_threshold or 0}M, "
            f"Confidence>{trigger.confidence_threshold or 0.5}"
        )
        
        return {
            "automation_id": automation_id,
            "status": "active",
            "trigger": trigger.dict(),
            "created_at": datetime.now().isoformat()
        }

    async def intelligent_deal_discovery(self) -> List[Dict[str, Any]]:
        """
        Use Tandemn + Exa to discover and analyze new M&A deals
        Returns enhanced deals with multi-model confidence scoring
        """
        
        # Step 1: Discover new deals using Exa
        search_queries = [
            "merger acquisition announced today",
            "strategic partnership investment funding",
            "corporate deal transaction completed",
            "company acquired startup funding round"
        ]
        
        all_events = []
        for query in search_queries:
            try:
                events = await self.ma_service.search_ma_events(query, num_results=10)
                all_events.extend(events)
            except Exception as e:
                logger.error(f"Error searching for events with query '{query}': {str(e)}")
        
        # Step 2: Enhance with Tandemn distributed confidence scoring
        if all_events and self.tandemn_api_key:
            try:
                enhanced_events = await enhance_ma_events_with_tandemn(
                    events=all_events,
                    api_key=self.tandemn_api_key
                )
                return enhanced_events
            except Exception as e:
                logger.error(f"Error enhancing events with Tandemn: {str(e)}")
                return all_events
        
        return all_events

    async def check_automation_triggers(self) -> List[Dict[str, Any]]:
        """
        Check all active automations for trigger conditions
        Uses intelligent deal discovery and sends Poke notifications
        """
        
        triggered_automations = []
        
        # Get latest deals using intelligent discovery
        latest_deals = await self.intelligent_deal_discovery()
        
        for automation_id, trigger in self.active_automations.items():
            
            for deal in latest_deals:
                should_trigger = False
                trigger_reason = ""
                
                # Check company filter
                if trigger.companies:
                    deal_companies = deal.get('companies_mentioned', [])
                    if not any(company.lower() in [c.lower() for c in deal_companies] 
                             for company in trigger.companies):
                        continue
                
                # Check trigger conditions
                if trigger.trigger_type == "new_deal":
                    should_trigger = True
                    trigger_reason = "New deal discovered"
                    
                elif trigger.trigger_type == "confidence_change":
                    confidence = deal.get('tandemn_multi_model_confidence', deal.get('confidence_score', 0))
                    if confidence >= (trigger.confidence_threshold or 0.8):
                        should_trigger = True
                        trigger_reason = f"High confidence deal ({confidence:.2f})"
                        
                elif trigger.trigger_type == "market_sentiment":
                    # Check if deal has sentiment analysis
                    sentiment_data = deal.get('sentiment_analysis', {})
                    if sentiment_data:
                        sentiment = sentiment_data.get('overall_sentiment', 0)
                        if abs(sentiment) >= (trigger.sentiment_threshold or 0.7):
                            should_trigger = True
                            trigger_reason = f"Strong market sentiment ({sentiment:.2f})"
                
                elif trigger.trigger_type == "competitor_activity":
                    # Check if deal involves competitors
                    deal_value = deal.get('deal_value')
                    if deal_value and deal_value >= (trigger.deal_value_threshold or 1000000000):  # $1B default
                        should_trigger = True
                        trigger_reason = f"Large competitor deal (${deal_value/1e9:.1f}B)"
                
                if should_trigger:
                    # Create rich notification message
                    message = await self.create_deal_notification_message(deal, trigger_reason)
                    
                    # Send Poke notification
                    await self.send_poke_message(message, priority="high")
                    
                    triggered_automations.append({
                        "automation_id": automation_id,
                        "deal": deal,
                        "trigger_reason": trigger_reason,
                        "timestamp": datetime.now().isoformat()
                    })
        
        return triggered_automations

    async def create_deal_notification_message(self, deal: Dict[str, Any], reason: str) -> str:
        """Create rich, actionable notification message for Poke"""
        
        source_company = deal.get('source_company', 'Unknown')
        target_company = deal.get('target_company', 'Unknown')
        deal_type = deal.get('deal_type', 'transaction')
        deal_value = deal.get('deal_value')
        confidence = deal.get('tandemn_multi_model_confidence', deal.get('confidence_score', 0))
        
        # Format deal value
        value_str = ""
        if deal_value:
            if deal_value >= 1e9:
                value_str = f" (${deal_value/1e9:.1f}B)"
            elif deal_value >= 1e6:
                value_str = f" (${deal_value/1e6:.0f}M)"
        
        # Create emoji based on deal type
        emoji_map = {
            'acquisition': '🏢',
            'merger': '🤝',
            'partnership': '🤝',
            'funding': '💰',
            'investment': '📈'
        }
        emoji = emoji_map.get(deal_type, '📊')
        
        # Build message
        message = f"{emoji} M&A Alert: {source_company} {deal_type} {target_company}{value_str}\n"
        message += f"🎯 Reason: {reason}\n"
        message += f"🔍 Confidence: {confidence:.1%}\n"
        
        # Add Tandemn insights if available
        if 'confidence_breakdown' in deal:
            breakdown = deal['confidence_breakdown']
            message += f"📊 Analysis: "
            if 'financial_confidence' in breakdown:
                message += f"Financial {breakdown['financial_confidence'].get('confidence', 0):.1%} | "
            if 'legal_confidence' in breakdown:
                message += f"Legal {breakdown['legal_confidence'].get('confidence', 0):.1%} | "
            if 'market_confidence' in breakdown:
                message += f"Market {breakdown['market_confidence'].get('confidence', 0):.1%}"
            message += "\n"
        
        # Add source and timestamp
        source = deal.get('source', 'Multiple sources')
        message += f"📰 Source: {source}\n"
        message += f"⏰ {datetime.now().strftime('%H:%M %Z')}"
        
        return message

    async def create_sentiment_monitoring_automation(self) -> Dict[str, Any]:
        """
        Create automation that monitors market sentiment using Tandemn distributed analysis
        """
        
        automation_id = f"sentiment_monitor_{datetime.now().timestamp()}"
        
        # Monitor social media and news for M&A sentiment
        async def sentiment_check():
            try:
                # Use Tandemn for distributed sentiment analysis
                async with TandemnDistributedService(self.tandemn_api_key) as tandemn:
                    # Sample news texts (in production, would fetch from live sources)
                    news_texts = [
                        "Microsoft acquisition rumors spreading on social media",
                        "Tech merger activity heating up according to analysts",
                        "Investment firms bullish on M&A opportunities"
                    ]
                    
                    sentiment_results = await tandemn.real_time_sentiment_analysis(news_texts)
                    
                    # Check for significant sentiment changes
                    overall_sentiment = sentiment_results.get('overall_sentiment', 0)
                    if abs(overall_sentiment) > 0.6:  # Strong sentiment threshold
                        
                        sentiment_type = "Bullish" if overall_sentiment > 0 else "Bearish"
                        message = f"📈 Market Sentiment Alert: {sentiment_type} M&A sentiment detected!\n"
                        message += f"🎯 Sentiment Score: {overall_sentiment:+.2f}\n"
                        message += f"📊 Sample Size: {sentiment_results.get('sample_size', 0)} sources\n"
                        message += f"🏢 Top Companies: {', '.join(sentiment_results.get('top_mentioned_companies', [])[:3])}"
                        
                        await self.send_poke_message(message, priority="normal")
                        
            except Exception as e:
                logger.error(f"Sentiment monitoring error: {str(e)}")
        
        # Schedule sentiment check (in production, would use proper scheduler)
        asyncio.create_task(sentiment_check())
        
        await self.send_poke_message(
            "🎭 Sentiment Monitor Active: Tracking market sentiment for M&A activity using distributed AI analysis"
        )
        
        return {
            "automation_id": automation_id,
            "type": "sentiment_monitoring",
            "status": "active"
        }

    async def create_competitor_intelligence_automation(self, competitors: List[str]) -> Dict[str, Any]:
        """
        Create automation that monitors competitor M&A activity
        """
        
        automation_id = f"competitor_intel_{datetime.now().timestamp()}"
        
        # Set up competitor monitoring
        trigger = MAAutomationTrigger(
            trigger_type="competitor_activity",
            companies=competitors,
            deal_value_threshold=100000000  # $100M threshold
        )
        
        await self.create_deal_monitoring_automation(automation_id, trigger)
        
        competitors_str = ", ".join(competitors)
        await self.send_poke_message(
            f"🕵️ Competitor Intelligence Active: Monitoring {competitors_str} for M&A activity >$100M"
        )
        
        return {
            "automation_id": automation_id,
            "type": "competitor_intelligence",
            "competitors": competitors,
            "status": "active"
        }

    async def create_portfolio_monitoring_automation(self, portfolio_companies: List[str]) -> Dict[str, Any]:
        """
        Create automation for portfolio company exit monitoring
        """
        
        automation_id = f"portfolio_monitor_{datetime.now().timestamp()}"
        
        # Monitor for high-confidence deals involving portfolio companies
        trigger = MAAutomationTrigger(
            trigger_type="confidence_change",
            companies=portfolio_companies,
            confidence_threshold=0.85
        )
        
        await self.create_deal_monitoring_automation(automation_id, trigger)
        
        portfolio_str = ", ".join(portfolio_companies)
        await self.send_poke_message(
            f"💼 Portfolio Monitor Active: Tracking exit opportunities for {portfolio_str}"
        )
        
        return {
            "automation_id": automation_id,
            "type": "portfolio_monitoring",
            "portfolio_companies": portfolio_companies,
            "status": "active"
        }

    async def get_automation_status(self) -> Dict[str, Any]:
        """Get status of all active automations"""
        
        return {
            "active_automations": len(self.active_automations),
            "automations": [
                {
                    "id": aid,
                    "trigger": trigger.dict(),
                    "status": "active"
                }
                for aid, trigger in self.active_automations.items()
            ],
            "last_check": self.last_check_time.isoformat(),
            "system_status": "operational"
        }

# MCP Server Integration Functions
async def setup_ma_intelligence_automations(
    poke_api_key: str,
    tandemn_api_key: str, 
    exa_api_key: str
) -> PokeMCPServer:
    """
    Set up M&A intelligence automations for Poke MCP integration
    """
    
    server = PokeMCPServer(poke_api_key, tandemn_api_key, exa_api_key)
    
    # Create default automations
    await server.create_sentiment_monitoring_automation()
    
    # Example competitor monitoring
    tech_giants = ["Microsoft", "Google", "Apple", "Meta", "Amazon"]
    await server.create_competitor_intelligence_automation(tech_giants)
    
    # Example portfolio monitoring (for VCs)
    portfolio_example = ["OpenAI", "Anthropic", "Stripe", "Figma"]
    await server.create_portfolio_monitoring_automation(portfolio_example)
    
    return server

# Background task for continuous monitoring
async def run_continuous_monitoring(server: PokeMCPServer, check_interval: int = 300):
    """
    Run continuous monitoring of automations (every 5 minutes by default)
    """
    
    while True:
        try:
            triggered = await server.check_automation_triggers()
            if triggered:
                logger.info(f"Triggered {len(triggered)} automations")
            
            server.last_check_time = datetime.now()
            
        except Exception as e:
            logger.error(f"Monitoring error: {str(e)}")
        
        await asyncio.sleep(check_interval)
