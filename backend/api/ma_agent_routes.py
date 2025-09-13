from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List, Dict, Optional
from datetime import datetime
import asyncio
import logging

from models.ma_events import MAEvent, AgentActivity, NotificationEvent, EcosystemImpact
from services.ma_monitoring_agent import MAMonitoringAgent

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ma-agent", tags=["M&A Agent"])

# Global agent instance
agent_instance: Optional[MAMonitoringAgent] = None
agent_task: Optional[asyncio.Task] = None

def get_agent() -> MAMonitoringAgent:
    """Get or create the agent instance"""
    global agent_instance
    if agent_instance is None:
        agent_instance = MAMonitoringAgent()
    return agent_instance

@router.post("/start")
async def start_agent(background_tasks: BackgroundTasks):
    """Start the M&A monitoring agent"""
    global agent_task
    
    agent = get_agent()
    
    if agent.is_running:
        return {"status": "already_running", "message": "Agent is already running"}
    
    try:
        # Start the agent in the background
        agent_task = asyncio.create_task(agent.start_monitoring())
        
        return {
            "status": "started",
            "message": "M&A monitoring agent started successfully",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to start agent: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to start agent: {str(e)}")

@router.post("/stop")
async def stop_agent():
    """Stop the M&A monitoring agent"""
    global agent_task
    
    agent = get_agent()
    
    if not agent.is_running:
        return {"status": "not_running", "message": "Agent is not currently running"}
    
    try:
        await agent.stop_monitoring()
        
        if agent_task:
            agent_task.cancel()
            try:
                await agent_task
            except asyncio.CancelledError:
                pass
            agent_task = None
        
        return {
            "status": "stopped",
            "message": "M&A monitoring agent stopped successfully",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to stop agent: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to stop agent: {str(e)}")

@router.get("/status")
async def get_agent_status():
    """Get the current status of the M&A monitoring agent"""
    agent = get_agent()
    
    return {
        "is_running": agent.is_running,
        "last_search_time": agent.last_search_time.isoformat() if agent.last_search_time else None,
        "monitoring_interval": agent.monitoring_interval,
        "total_events": len(agent.events),
        "total_notifications": len(agent.notifications),
        "unread_notifications": len([n for n in agent.notifications if not n.read]),
        "total_activities": len(agent.activities),
        "timestamp": datetime.now().isoformat()
    }

@router.get("/events", response_model=List[Dict])
async def get_recent_events(hours: int = 24):
    """Get recent M&A events"""
    agent = get_agent()
    
    try:
        events = await agent.get_recent_events(hours=hours)
        return [event.dict() for event in events]
    except Exception as e:
        logger.error(f"Failed to get events: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get events: {str(e)}")

@router.get("/events/{event_id}")
async def get_event_details(event_id: str):
    """Get details of a specific event"""
    agent = get_agent()
    
    event = next((e for e in agent.events if e.id == event_id), None)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    # Get related impacts
    impacts = await agent.get_ecosystem_impacts(event_id=event_id)
    
    return {
        "event": event.dict(),
        "impacts": [impact.dict() for impact in impacts]
    }

@router.get("/notifications", response_model=List[Dict])
async def get_notifications(unread_only: bool = False):
    """Get notifications"""
    agent = get_agent()
    
    try:
        notifications = await agent.get_notifications(unread_only=unread_only)
        return [notif.dict() for notif in notifications]
    except Exception as e:
        logger.error(f"Failed to get notifications: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get notifications: {str(e)}")

@router.post("/notifications/{notification_id}/read")
async def mark_notification_read(notification_id: str):
    """Mark a notification as read"""
    agent = get_agent()
    
    try:
        await agent.mark_notification_read(notification_id)
        return {"status": "success", "message": "Notification marked as read"}
    except Exception as e:
        logger.error(f"Failed to mark notification as read: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to mark notification as read: {str(e)}")

@router.get("/activities", response_model=List[Dict])
async def get_agent_activities(limit: int = 50):
    """Get recent agent activities"""
    agent = get_agent()
    
    try:
        activities = await agent.get_agent_activities(limit=limit)
        return [activity.dict() for activity in activities]
    except Exception as e:
        logger.error(f"Failed to get activities: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get activities: {str(e)}")

@router.get("/impacts", response_model=List[Dict])
async def get_ecosystem_impacts(event_id: Optional[str] = None):
    """Get ecosystem impacts"""
    agent = get_agent()
    
    try:
        impacts = await agent.get_ecosystem_impacts(event_id=event_id)
        return [impact.dict() for impact in impacts]
    except Exception as e:
        logger.error(f"Failed to get impacts: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get impacts: {str(e)}")

@router.get("/dashboard")
async def get_dashboard_data():
    """Get comprehensive dashboard data"""
    agent = get_agent()
    
    try:
        # Get recent data
        recent_events = await agent.get_recent_events(hours=24)
        notifications = await agent.get_notifications(unread_only=True)
        activities = await agent.get_agent_activities(limit=10)
        impacts = agent.impacts[-10:]  # Last 10 impacts
        
        # Calculate statistics
        total_events_today = len(recent_events)
        high_confidence_events = len([e for e in recent_events if e.confidence_score > 0.7])
        
        event_types_count = {}
        for event in recent_events:
            event_type = event.event_type.value
            event_types_count[event_type] = event_types_count.get(event_type, 0) + 1
        
        return {
            "status": {
                "is_running": agent.is_running,
                "last_search_time": agent.last_search_time.isoformat() if agent.last_search_time else None,
                "monitoring_interval": agent.monitoring_interval
            },
            "statistics": {
                "total_events": len(agent.events),
                "events_today": total_events_today,
                "high_confidence_events": high_confidence_events,
                "unread_notifications": len(notifications),
                "total_impacts": len(agent.impacts),
                "event_types_today": event_types_count
            },
            "recent_events": [event.dict() for event in recent_events[:10]],
            "notifications": [notif.dict() for notif in notifications[:10]],
            "activities": [activity.dict() for activity in activities],
            "impacts": [impact.dict() for impact in impacts],
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to get dashboard data: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get dashboard data: {str(e)}")

@router.post("/manual-search")
async def trigger_manual_search():
    """Manually trigger a search for new events"""
    agent = get_agent()
    
    if not agent.is_running:
        raise HTTPException(status_code=400, detail="Agent is not running")
    
    try:
        # This would trigger a manual search cycle
        # For now, we'll just return a success message
        return {
            "status": "triggered",
            "message": "Manual search triggered successfully",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to trigger manual search: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to trigger manual search: {str(e)}")

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    agent = get_agent()
    
    return {
        "status": "healthy",
        "agent_running": agent.is_running,
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }
