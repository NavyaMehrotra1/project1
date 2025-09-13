import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from pathlib import Path
import uuid

from models.ma_events import MAEvent, AgentActivity, NotificationEvent, EcosystemImpact
from services.ma_intelligence_service import MAIntelligenceService

logger = logging.getLogger(__name__)

class MAMonitoringAgent:
    def __init__(self, data_dir: str = None):
        self.data_dir = Path(data_dir) if data_dir else Path(__file__).parent.parent / "data"
        self.data_dir.mkdir(exist_ok=True)
        
        # Data files
        self.events_file = self.data_dir / "ma_events.json"
        self.activities_file = self.data_dir / "agent_activities.json"
        self.notifications_file = self.data_dir / "notifications.json"
        self.impacts_file = self.data_dir / "ecosystem_impacts.json"
        
        # In-memory storage
        self.events: List[MAEvent] = []
        self.activities: List[AgentActivity] = []
        self.notifications: List[NotificationEvent] = []
        self.impacts: List[EcosystemImpact] = []
        
        # Agent state
        self.is_running = False
        self.monitoring_interval = 60  # 1 minute
        self.last_search_time = None
        
        # Load existing data
        self._load_data()
        
        # Initialize services
        self.intelligence_service = None
    
    async def start_monitoring(self):
        """Start the continuous monitoring process"""
        if self.is_running:
            logger.warning("Agent is already running")
            return
        
        self.is_running = True
        logger.info("🚀 Starting M&A Monitoring Agent")
        
        # Log startup activity
        await self._log_activity(
            activity_type="startup",
            description="M&A Monitoring Agent started",
            status="completed"
        )
        
        try:
            while self.is_running:
                await self._monitoring_cycle()
                await asyncio.sleep(self.monitoring_interval)
        except Exception as e:
            logger.error(f"Agent monitoring error: {e}")
            await self._log_activity(
                activity_type="error",
                description=f"Agent error: {str(e)}",
                status="failed"
            )
        finally:
            self.is_running = False
            logger.info("🛑 M&A Monitoring Agent stopped")
    
    async def stop_monitoring(self):
        """Stop the monitoring process"""
        self.is_running = False
        await self._log_activity(
            activity_type="shutdown",
            description="M&A Monitoring Agent stopped",
            status="completed"
        )
    
    async def _monitoring_cycle(self):
        """Execute one monitoring cycle"""
        cycle_start = datetime.now()
        
        try:
            # Initialize intelligence service for this cycle
            async with MAIntelligenceService() as intelligence:
                self.intelligence_service = intelligence
                
                # Search for new M&A events
                await self._search_for_events()
                
                # Analyze ecosystem impacts
                await self._analyze_impacts()
                
                # Clean up old data
                await self._cleanup_old_data()
                
                # Save all data
                await self._save_data()
        
        except Exception as e:
            logger.error(f"Monitoring cycle error: {e}")
            await self._log_activity(
                activity_type="search",
                description=f"Monitoring cycle failed: {str(e)}",
                status="failed",
                execution_time=(datetime.now() - cycle_start).total_seconds()
            )
    
    async def _search_for_events(self):
        """Search for new M&A events"""
        search_start = datetime.now()
        
        try:
            # Determine search time range
            hours_to_search = 24  # Default to 24 hours
            if self.last_search_time:
                hours_since_last = (datetime.now() - self.last_search_time).total_seconds() / 3600
                hours_to_search = max(1, min(24, int(hours_since_last) + 1))
            
            # Search for events
            new_events = await self.intelligence_service.search_ma_events(
                time_range_hours=hours_to_search
            )
            
            # Filter out events we already have
            truly_new_events = []
            existing_event_ids = {event.id for event in self.events}
            
            for event in new_events:
                if event.id not in existing_event_ids:
                    # Check for similar events (different ID but same content)
                    if not self._is_duplicate_event(event):
                        truly_new_events.append(event)
                        self.events.append(event)
            
            # Log activity
            execution_time = (datetime.now() - search_start).total_seconds()
            await self._log_activity(
                activity_type="search",
                description=f"Searched for M&A events in last {hours_to_search} hours",
                events_found=len(new_events),
                events_updated=len(truly_new_events),
                sources_checked=["Exa API"],
                execution_time=execution_time,
                status="completed"
            )
            
            # Create notifications for new events
            for event in truly_new_events:
                await self._create_notification(
                    event_id=event.id,
                    notification_type="new_event",
                    title=f"New {event.event_type.value.replace('_', ' ').title()} Detected",
                    message=f"{event.primary_company.name} - {event.title}",
                    priority="high" if event.confidence_score > 0.7 else "medium"
                )
            
            self.last_search_time = datetime.now()
            
        except Exception as e:
            logger.error(f"Event search error: {e}")
            await self._log_activity(
                activity_type="search",
                description=f"Event search failed: {str(e)}",
                status="failed",
                execution_time=(datetime.now() - search_start).total_seconds()
            )
    
    async def _analyze_impacts(self):
        """Analyze ecosystem impacts of recent events"""
        analysis_start = datetime.now()
        
        try:
            # Load existing company data for impact analysis
            company_data = await self._load_company_data()
            
            # Analyze impacts for recent events (last 24 hours)
            recent_events = [
                event for event in self.events
                if event.discovered_at > datetime.now() - timedelta(hours=24)
            ]
            
            new_impacts = []
            for event in recent_events:
                # Check if we already analyzed this event
                existing_impact_ids = {impact.event_id for impact in self.impacts}
                if event.id not in existing_impact_ids:
                    impact = await self.intelligence_service.analyze_ecosystem_impact(
                        event, company_data
                    )
                    new_impacts.append(impact)
                    self.impacts.append(impact)
            
            # Update graph data files with new M&A events
            await self._update_graph_data_files(recent_events)
            
            # Log activity
            execution_time = (datetime.now() - analysis_start).total_seconds()
            await self._log_activity(
                activity_type="analysis",
                description=f"Analyzed ecosystem impacts for {len(recent_events)} recent events",
                events_found=len(new_impacts),
                execution_time=execution_time,
                status="completed"
            )
            
            # Create notifications for significant impacts
            for impact in new_impacts:
                if impact.impact_score > 0.5:  # Significant impact threshold
                    await self._create_notification(
                        event_id=impact.event_id,
                        notification_type="impact_analysis",
                        title="Significant Ecosystem Impact Detected",
                        message=f"Impact on {len(impact.affected_companies)} companies: {impact.description}",
                        priority="high" if impact.impact_score > 0.8 else "medium"
                    )
        
        except Exception as e:
            logger.error(f"Impact analysis error: {e}")
            await self._log_activity(
                activity_type="analysis",
                description=f"Impact analysis failed: {str(e)}",
                status="failed",
                execution_time=(datetime.now() - analysis_start).total_seconds()
            )
    
    async def _load_company_data(self) -> List[Dict]:
        """Load existing company data for impact analysis"""
        try:
            # Try to load from the graph data file
            graph_data_path = Path(__file__).parent.parent.parent / "data_agent" / "data_agent" / "output" / "graph_data_for_frontend.json"
            
            if graph_data_path.exists():
                with open(graph_data_path, 'r') as f:
                    graph_data = json.load(f)
                    return [node.get('data', {}) for node in graph_data.get('nodes', [])]
            
            # Fallback to empty list
            return []
            
        except Exception as e:
            logger.error(f"Error loading company data: {e}")
            return []
    
    def _is_duplicate_event(self, new_event: MAEvent) -> bool:
        """Check if an event is a duplicate of existing events"""
        for existing_event in self.events:
            # Check for similar companies and event type
            if (existing_event.event_type == new_event.event_type and
                existing_event.primary_company.name == new_event.primary_company.name):
                
                # Check if secondary companies match
                existing_secondary = existing_event.secondary_company.name if existing_event.secondary_company else None
                new_secondary = new_event.secondary_company.name if new_event.secondary_company else None
                
                if existing_secondary == new_secondary:
                    return True
        
        return False
    
    async def _create_notification(self, event_id: str, notification_type: str,
                                 title: str, message: str, priority: str = "medium"):
        """Create a new notification"""
        notification = NotificationEvent(
            id=str(uuid.uuid4()),
            event_id=event_id,
            notification_type=notification_type,
            title=title,
            message=message,
            priority=priority
        )
        
        self.notifications.append(notification)
        logger.info(f"📢 Notification: {title}")
    
    async def _log_activity(self, activity_type: str, description: str,
                          events_found: int = 0, events_updated: int = 0,
                          sources_checked: List[str] = None,
                          execution_time: float = 0.0, status: str = "completed"):
        """Log agent activity"""
        activity = AgentActivity(
            id=str(uuid.uuid4()),
            activity_type=activity_type,
            description=description,
            events_found=events_found,
            events_updated=events_updated,
            sources_checked=sources_checked or [],
            execution_time=execution_time,
            status=status
        )
        
        self.activities.append(activity)
        logger.info(f"🤖 Agent Activity: {description}")
    
    async def _cleanup_old_data(self):
        """Clean up old data to prevent memory issues"""
        cutoff_date = datetime.now() - timedelta(days=7)  # Keep 7 days of data
        
        # Clean old activities
        self.activities = [
            activity for activity in self.activities
            if activity.timestamp > cutoff_date
        ]
        
        # Clean old notifications (keep read notifications for 1 day, unread for 7 days)
        self.notifications = [
            notif for notif in self.notifications
            if (notif.created_at > cutoff_date or 
                (not notif.read and notif.created_at > datetime.now() - timedelta(days=1)))
        ]
        
        # Keep all events and impacts (they're valuable historical data)
    
    def _load_data(self):
        """Load existing data from files"""
        try:
            if self.events_file.exists():
                with open(self.events_file, 'r') as f:
                    events_data = json.load(f)
                    self.events = [MAEvent(**event) for event in events_data]
            
            if self.activities_file.exists():
                with open(self.activities_file, 'r') as f:
                    activities_data = json.load(f)
                    self.activities = [AgentActivity(**activity) for activity in activities_data]
            
            if self.notifications_file.exists():
                with open(self.notifications_file, 'r') as f:
                    notifications_data = json.load(f)
                    self.notifications = [NotificationEvent(**notif) for notif in notifications_data]
            
            if self.impacts_file.exists():
                with open(self.impacts_file, 'r') as f:
                    impacts_data = json.load(f)
                    self.impacts = [EcosystemImpact(**impact) for impact in impacts_data]
                    
        except Exception as e:
            logger.error(f"Error loading data: {e}")
    
    async def _save_data(self):
        """Save all data to files"""
        try:
            # Save events
            with open(self.events_file, 'w') as f:
                json.dump([event.dict() for event in self.events], f, indent=2, default=str)
            
            # Save activities
            with open(self.activities_file, 'w') as f:
                json.dump([activity.dict() for activity in self.activities], f, indent=2, default=str)
            
            # Save notifications
            with open(self.notifications_file, 'w') as f:
                json.dump([notif.dict() for notif in self.notifications], f, indent=2, default=str)
            
            # Save impacts
            with open(self.impacts_file, 'w') as f:
                json.dump([impact.dict() for impact in self.impacts], f, indent=2, default=str)
                
        except Exception as e:
            logger.error(f"Error saving data: {e}")
    
    # API methods for external access
    async def get_recent_events(self, hours: int = 24) -> List[MAEvent]:
        """Get events from the last N hours"""
        cutoff = datetime.now() - timedelta(hours=hours)
        return [event for event in self.events if event.discovered_at > cutoff]
    
    async def get_notifications(self, unread_only: bool = False) -> List[NotificationEvent]:
        """Get notifications"""
        if unread_only:
            return [notif for notif in self.notifications if not notif.read]
        return self.notifications
    
    async def mark_notification_read(self, notification_id: str):
        """Mark a notification as read"""
        for notif in self.notifications:
            if notif.id == notification_id:
                notif.read = True
                break
    
    async def get_agent_activities(self, limit: int = 50) -> List[AgentActivity]:
        """Get recent agent activities"""
        return sorted(self.activities, key=lambda x: x.timestamp, reverse=True)[:limit]
    
    async def get_ecosystem_impacts(self, event_id: str = None) -> List[EcosystemImpact]:
        """Get ecosystem impacts"""
        if event_id:
            return [impact for impact in self.impacts if impact.event_id == event_id]
        return self.impacts
    
    async def _update_graph_data_files(self, new_events: List):
        """Update graph data files in data_agent/output with new M&A events"""
        try:
            # Path to graph data files
            graph_data_path = Path(__file__).parent.parent.parent / "data_agent" / "data_agent" / "output" / "graph_data_for_frontend.json"
            complete_graph_path = Path(__file__).parent.parent.parent / "data_agent" / "data_agent" / "output" / "complete_graph_data.json"
            
            # Load existing graph data
            graph_data = {}
            if graph_data_path.exists():
                with open(graph_data_path, 'r') as f:
                    graph_data = json.load(f)
            
            # Add new nodes and edges for M&A events
            nodes = graph_data.get('nodes', [])
            edges = graph_data.get('edges', [])
            
            # Track existing node IDs
            existing_node_ids = {node['id'] for node in nodes}
            
            for event in new_events:
                # Add primary company as node if not exists
                primary_id = event.primary_company.name.lower().replace(' ', '_')
                if primary_id not in existing_node_ids:
                    nodes.append({
                        "id": primary_id,
                        "label": event.primary_company.name,
                        "size": 50,
                        "color": "#e74c3c",  # Red for M&A companies
                        "data": {
                            "name": event.primary_company.name,
                            "industry": "M&A Activity",
                            "status": "Active",
                            "deal_activity_count": 1,
                            "extraordinary_score": 50.0,
                            "ma_event_type": event.event_type.value,
                            "discovered_at": event.discovered_at.isoformat()
                        }
                    })
                    existing_node_ids.add(primary_id)
                
                # Add secondary company if exists
                if event.secondary_company:
                    secondary_id = event.secondary_company.name.lower().replace(' ', '_')
                    if secondary_id not in existing_node_ids:
                        nodes.append({
                            "id": secondary_id,
                            "label": event.secondary_company.name,
                            "size": 40,
                            "color": "#f39c12",  # Orange for acquired companies
                            "data": {
                                "name": event.secondary_company.name,
                                "industry": "M&A Target",
                                "status": "Acquired",
                                "deal_activity_count": 1,
                                "extraordinary_score": 30.0,
                                "ma_event_type": event.event_type.value,
                                "discovered_at": event.discovered_at.isoformat()
                            }
                        })
                        existing_node_ids.add(secondary_id)
                    
                    # Add edge between companies
                    edge_id = f"ma_{event.id}"
                    edges.append({
                        "id": edge_id,
                        "source": primary_id,
                        "target": secondary_id,
                        "type": event.event_type.value,
                        "deal_value": event.deal_value,
                        "confidence": event.confidence_score,
                        "discovered_at": event.discovered_at.isoformat(),
                        "color": "#e74c3c",
                        "width": 3 if event.deal_value and event.deal_value > 1_000_000 else 2
                    })
            
            # Update graph data
            updated_graph_data = {
                "nodes": nodes,
                "edges": edges,
                "metadata": {
                    "last_updated": datetime.now().isoformat(),
                    "ma_events_count": len([e for e in edges if e.get("type") in ["merger_acquisition", "business_partnership", "joint_venture", "strategic_alliance", "consolidation"]]),
                    "total_nodes": len(nodes),
                    "total_edges": len(edges)
                }
            }
            
            # Save updated graph data
            with open(graph_data_path, 'w') as f:
                json.dump(updated_graph_data, f, indent=2)
            
            # Also update complete graph data if it exists
            if complete_graph_path.exists():
                with open(complete_graph_path, 'w') as f:
                    json.dump(updated_graph_data, f, indent=2)
            
            logger.info(f"Updated graph data files with {len(new_events)} new M&A events")
            
        except Exception as e:
            logger.error(f"Error updating graph data files: {e}")
