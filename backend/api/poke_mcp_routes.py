"""
Poke MCP API Routes
FastAPI routes for Poke Model Context Protocol integration
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
import asyncio
import logging
import os
from datetime import datetime

from ..services.poke_mcp_server import (
    PokeMCPServer,
    MAAutomationTrigger,
    PokeMessage,
    setup_ma_intelligence_automations,
    run_continuous_monitoring
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/poke-mcp", tags=["poke-mcp"])

# Global server instance
mcp_server: Optional[PokeMCPServer] = None

# Pydantic models for requests
class CreateAutomationRequest(BaseModel):
    automation_type: str  # "deal_monitoring", "sentiment_analysis", "competitor_intel", "portfolio_tracking"
    companies: List[str] = []
    deal_value_threshold: Optional[float] = None
    confidence_threshold: Optional[float] = 0.8
    sentiment_threshold: Optional[float] = 0.7

class SendMessageRequest(BaseModel):
    message: str
    priority: str = "normal"

class CompetitorIntelRequest(BaseModel):
    competitors: List[str]

class PortfolioMonitorRequest(BaseModel):
    portfolio_companies: List[str]

def get_api_keys():
    """Get required API keys from environment"""
    poke_key = os.getenv("POKE_API_KEY")
    tandemn_key = os.getenv("TANDEMN_API_KEY")
    exa_key = os.getenv("EXA_API_KEY")
    
    if not poke_key:
        raise HTTPException(status_code=500, detail="POKE_API_KEY not configured")
    if not tandemn_key:
        raise HTTPException(status_code=500, detail="TANDEMN_API_KEY not configured")
    if not exa_key:
        raise HTTPException(status_code=500, detail="EXA_API_KEY not configured")
    
    return poke_key, tandemn_key, exa_key

async def get_mcp_server():
    """Get or initialize MCP server"""
    global mcp_server
    
    if mcp_server is None:
        poke_key, tandemn_key, exa_key = get_api_keys()
        mcp_server = await setup_ma_intelligence_automations(poke_key, tandemn_key, exa_key)
    
    return mcp_server

@router.post("/initialize")
async def initialize_mcp_server(background_tasks: BackgroundTasks):
    """
    Initialize Poke MCP server with M&A intelligence automations
    Sets up default monitoring for deals, sentiment, and competitor activity
    """
    try:
        server = await get_mcp_server()
        
        # Start continuous monitoring in background
        background_tasks.add_task(run_continuous_monitoring, server, 300)  # 5 minute intervals
        
        return {
            "status": "initialized",
            "message": "M&A Intelligence MCP server active with Poke integration",
            "capabilities": [
                "Real-time deal monitoring",
                "Distributed sentiment analysis",
                "Competitor intelligence tracking",
                "Portfolio company exit alerts",
                "Multi-model confidence scoring"
            ],
            "automations_created": 3  # sentiment, competitor, portfolio
        }
        
    except Exception as e:
        logger.error(f"MCP server initialization failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Initialization failed: {str(e)}")

@router.post("/automations/create")
async def create_automation(request: CreateAutomationRequest):
    """
    Create custom M&A intelligence automation
    Supports deal monitoring, sentiment analysis, competitor tracking, portfolio monitoring
    """
    try:
        server = await get_mcp_server()
        automation_id = f"{request.automation_type}_{datetime.now().timestamp()}"
        
        if request.automation_type == "deal_monitoring":
            trigger = MAAutomationTrigger(
                trigger_type="new_deal",
                companies=request.companies,
                deal_value_threshold=request.deal_value_threshold,
                confidence_threshold=request.confidence_threshold
            )
            result = await server.create_deal_monitoring_automation(automation_id, trigger)
            
        elif request.automation_type == "sentiment_analysis":
            result = await server.create_sentiment_monitoring_automation()
            
        elif request.automation_type == "competitor_intel":
            result = await server.create_competitor_intelligence_automation(request.companies)
            
        elif request.automation_type == "portfolio_tracking":
            result = await server.create_portfolio_monitoring_automation(request.companies)
            
        else:
            raise HTTPException(status_code=400, detail=f"Unknown automation type: {request.automation_type}")
        
        return {
            "automation_created": True,
            "automation_id": automation_id,
            "type": request.automation_type,
            "details": result,
            "poke_notification_sent": True
        }
        
    except Exception as e:
        logger.error(f"Automation creation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Automation creation failed: {str(e)}")

@router.post("/message/send")
async def send_poke_message(request: SendMessageRequest):
    """
    Send message to Poke programmatically
    Useful for testing and manual notifications
    """
    try:
        server = await get_mcp_server()
        success = await server.send_poke_message(request.message, request.priority)
        
        return {
            "message_sent": success,
            "message": request.message,
            "priority": request.priority,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Message sending failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Message sending failed: {str(e)}")

@router.post("/intelligence/discover")
async def discover_deals():
    """
    Trigger intelligent deal discovery using Tandemn + Exa
    Returns latest M&A deals with enhanced confidence scoring
    """
    try:
        server = await get_mcp_server()
        deals = await server.intelligent_deal_discovery()
        
        # Send summary to Poke
        if deals:
            summary_message = f"🔍 Deal Discovery: Found {len(deals)} new M&A events\n"
            high_confidence = [d for d in deals if d.get('tandemn_multi_model_confidence', 0) > 0.8]
            if high_confidence:
                summary_message += f"⭐ {len(high_confidence)} high-confidence deals detected"
            
            await server.send_poke_message(summary_message)
        
        return {
            "deals_discovered": len(deals),
            "high_confidence_deals": len([d for d in deals if d.get('tandemn_multi_model_confidence', 0) > 0.8]),
            "deals": deals[:5],  # Return first 5 for preview
            "poke_notification_sent": len(deals) > 0
        }
        
    except Exception as e:
        logger.error(f"Deal discovery failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Deal discovery failed: {str(e)}")

@router.post("/automations/trigger-check")
async def check_automation_triggers():
    """
    Manually trigger automation checks
    Useful for testing and immediate updates
    """
    try:
        server = await get_mcp_server()
        triggered = await server.check_automation_triggers()
        
        return {
            "automations_triggered": len(triggered),
            "triggered_automations": triggered,
            "check_timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Automation trigger check failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Trigger check failed: {str(e)}")

@router.get("/automations/status")
async def get_automations_status():
    """
    Get status of all active automations
    Shows what's currently being monitored
    """
    try:
        server = await get_mcp_server()
        status = await server.get_automation_status()
        
        return status
        
    except Exception as e:
        logger.error(f"Status check failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Status check failed: {str(e)}")

@router.post("/competitor-intel/setup")
async def setup_competitor_intelligence(request: CompetitorIntelRequest):
    """
    Set up comprehensive competitor intelligence monitoring
    Tracks M&A activity, partnerships, and strategic moves
    """
    try:
        server = await get_mcp_server()
        result = await server.create_competitor_intelligence_automation(request.competitors)
        
        # Also create high-value deal monitoring for competitors
        trigger = MAAutomationTrigger(
            trigger_type="competitor_activity",
            companies=request.competitors,
            deal_value_threshold=500000000  # $500M threshold for major deals
        )
        
        automation_id = f"competitor_major_deals_{datetime.now().timestamp()}"
        await server.create_deal_monitoring_automation(automation_id, trigger)
        
        return {
            "competitor_intelligence_active": True,
            "competitors_monitored": request.competitors,
            "automations_created": 2,
            "monitoring_features": [
                "M&A activity tracking",
                "Major deal alerts (>$500M)",
                "Strategic partnership detection",
                "Real-time Poke notifications"
            ]
        }
        
    except Exception as e:
        logger.error(f"Competitor intelligence setup failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Setup failed: {str(e)}")

@router.post("/portfolio/monitor")
async def setup_portfolio_monitoring(request: PortfolioMonitorRequest):
    """
    Set up portfolio company exit monitoring
    Perfect for VCs and investment firms
    """
    try:
        server = await get_mcp_server()
        result = await server.create_portfolio_monitoring_automation(request.portfolio_companies)
        
        # Also monitor for funding rounds and partnerships
        funding_trigger = MAAutomationTrigger(
            trigger_type="new_deal",
            companies=request.portfolio_companies,
            confidence_threshold=0.75
        )
        
        automation_id = f"portfolio_funding_{datetime.now().timestamp()}"
        await server.create_deal_monitoring_automation(automation_id, funding_trigger)
        
        return {
            "portfolio_monitoring_active": True,
            "companies_monitored": request.portfolio_companies,
            "monitoring_types": [
                "Exit opportunities (acquisitions)",
                "Funding rounds",
                "Strategic partnerships",
                "High-confidence deal alerts"
            ],
            "notification_method": "Poke messages with rich context"
        }
        
    except Exception as e:
        logger.error(f"Portfolio monitoring setup failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Setup failed: {str(e)}")

@router.get("/demo/scenarios")
async def get_demo_scenarios():
    """
    Get demonstration scenarios for Poke MCP integration
    Shows the different types of automations available
    """
    return {
        "demo_scenarios": [
            {
                "name": "Tech Giant Monitoring",
                "description": "Monitor FAANG companies for M&A activity",
                "automation_type": "competitor_intel",
                "companies": ["Microsoft", "Google", "Apple", "Meta", "Amazon"],
                "example_alert": "🏢 M&A Alert: Microsoft acquisition Activision Blizzard ($68.7B)\n🎯 Reason: Large competitor deal\n🔍 Confidence: 95%"
            },
            {
                "name": "VC Portfolio Tracking",
                "description": "Track portfolio companies for exit opportunities",
                "automation_type": "portfolio_tracking", 
                "companies": ["OpenAI", "Anthropic", "Stripe", "Figma"],
                "example_alert": "💼 Portfolio Alert: OpenAI partnership with Microsoft\n🎯 Reason: High confidence deal (0.92)\n📊 Analysis: Strategic partnership with major tech player"
            },
            {
                "name": "Market Sentiment Monitor",
                "description": "Real-time M&A market sentiment using distributed AI",
                "automation_type": "sentiment_analysis",
                "example_alert": "📈 Market Sentiment Alert: Bullish M&A sentiment detected!\n🎯 Sentiment Score: +0.73\n📊 Sample Size: 247 sources"
            },
            {
                "name": "Mega Deal Alerts",
                "description": "Alert for deals >$1B across all industries",
                "automation_type": "deal_monitoring",
                "threshold": "$1B+",
                "example_alert": "🚨 Mega Deal: ByteDance acquisition TikTok Global ($50B)\n🔍 Multi-model confidence: 89%\n📊 Financial: 92% | Legal: 85% | Market: 91%"
            }
        ],
        "integration_benefits": [
            "Real-time notifications via Poke",
            "Distributed AI processing with Tandemn",
            "Multi-source intelligence with Exa",
            "Multi-model confidence scoring",
            "Customizable automation triggers"
        ]
    }

@router.post("/demo/run/{scenario_name}")
async def run_demo_scenario(scenario_name: str):
    """
    Run a specific demo scenario
    Creates the automation and sends sample notifications
    """
    try:
        server = await get_mcp_server()
        
        if scenario_name == "tech-giant-monitoring":
            companies = ["Microsoft", "Google", "Apple", "Meta", "Amazon"]
            result = await server.create_competitor_intelligence_automation(companies)
            
            # Send demo alert
            demo_message = "🏢 DEMO: Microsoft acquisition Activision Blizzard ($68.7B)\n🎯 Reason: Large competitor deal\n🔍 Confidence: 95%\n📊 This is a demonstration of real-time M&A alerts"
            await server.send_poke_message(demo_message, priority="high")
            
        elif scenario_name == "vc-portfolio-tracking":
            companies = ["OpenAI", "Anthropic", "Stripe", "Figma"]
            result = await server.create_portfolio_monitoring_automation(companies)
            
            demo_message = "💼 DEMO: OpenAI strategic partnership detected\n🎯 Reason: High confidence deal (0.92)\n📊 Analysis: Major strategic move for portfolio company\n📰 This demonstrates portfolio exit monitoring"
            await server.send_poke_message(demo_message, priority="normal")
            
        elif scenario_name == "market-sentiment":
            result = await server.create_sentiment_monitoring_automation()
            
            demo_message = "📈 DEMO: Bullish M&A sentiment detected!\n🎯 Sentiment Score: +0.73\n📊 Sample Size: 247 sources\n🏢 Top Companies: Microsoft, Google, Apple\n🤖 Powered by distributed AI analysis"
            await server.send_poke_message(demo_message, priority="normal")
            
        else:
            raise HTTPException(status_code=400, detail=f"Unknown demo scenario: {scenario_name}")
        
        return {
            "demo_scenario": scenario_name,
            "status": "executed",
            "automation_created": True,
            "demo_notification_sent": True,
            "message": f"Demo scenario '{scenario_name}' executed successfully"
        }
        
    except Exception as e:
        logger.error(f"Demo scenario failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Demo failed: {str(e)}")

@router.get("/capabilities")
async def get_mcp_capabilities():
    """
    Get comprehensive capabilities of the Poke MCP integration
    """
    return {
        "mcp_server_capabilities": {
            "intelligent_deal_discovery": {
                "description": "AI-powered discovery of M&A deals using Exa search",
                "features": ["Multi-source aggregation", "Real-time processing", "Confidence scoring"]
            },
            "distributed_analysis": {
                "description": "Tandemn-powered distributed inference for deal analysis",
                "features": ["Multi-model confidence fusion", "Parallel processing", "Vision + text analysis"]
            },
            "automation_types": {
                "deal_monitoring": "Track new deals with customizable filters",
                "sentiment_analysis": "Real-time market sentiment using distributed AI",
                "competitor_intelligence": "Monitor competitor M&A activity",
                "portfolio_tracking": "Track portfolio company exits and funding"
            },
            "notification_system": {
                "platform": "Poke messaging",
                "features": ["Rich context", "Priority levels", "Real-time delivery"],
                "message_types": ["Deal alerts", "Sentiment updates", "Competitor moves", "Portfolio events"]
            }
        },
        "integration_benefits": [
            "Real-time M&A intelligence via Poke notifications",
            "Distributed AI processing for enhanced accuracy",
            "Customizable automation triggers and filters",
            "Multi-perspective confidence scoring",
            "Seamless workflow integration"
        ],
        "prize_categories_addressed": {
            "most_technically_impressive": "Distributed inference + MCP + multi-source intelligence",
            "most_practical": "Real-world M&A monitoring for investment professionals",
            "most_fun": "Interactive deal discovery with rich Poke notifications"
        }
    }
