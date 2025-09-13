#!/usr/bin/env python3
"""
Real-time demonstration of the M&A agent workflow
Shows: Exa API -> Processing -> Notifications -> Data Storage -> Visualization Updates
"""

import asyncio
import json
import sys
import os
from datetime import datetime
from dotenv import load_dotenv
import time

# Load environment variables
load_dotenv()

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.ma_intelligence_service import MAIntelligenceService
from services.ma_monitoring_agent import MAMonitoringAgent

class RealTimeWorkflowDemo:
    def __init__(self):
        self.step_count = 0
        
    def print_step(self, title, description=""):
        self.step_count += 1
        print(f"\n{'='*60}")
        print(f"STEP {self.step_count}: {title}")
        print(f"{'='*60}")
        if description:
            print(f"📝 {description}")
        print()
        
    def print_substep(self, message):
        print(f"   ➤ {message}")
        
    async def demonstrate_workflow(self):
        """Demonstrate the complete real-time M&A monitoring workflow"""
        
        print("🚀 REAL-TIME M&A AGENT WORKFLOW DEMONSTRATION")
        print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Step 1: Initialize Agent
        self.print_step("AGENT INITIALIZATION", "Setting up the M&A monitoring agent")
        
        agent = MAMonitoringAgent()
        self.print_substep("✅ Agent initialized")
        self.print_substep(f"📁 Data directory: {agent.data_dir}")
        self.print_substep(f"⏱️  Monitoring interval: {agent.monitoring_interval} seconds")
        
        # Step 2: Exa API Connection
        self.print_step("EXA API CONNECTION", "Connecting to Exa API for real-time data")
        
        async with MAIntelligenceService() as intelligence:
            self.print_substep("✅ Connected to Exa API")
            self.print_substep(f"🔑 API Key: {'SET' if intelligence.api_key else 'NOT SET'}")
            
            # Step 3: Real-time Search
            self.print_step("REAL-TIME SEARCH", "Executing M&A search queries")
            
            queries = intelligence.ma_queries[:3]  # Use first 3 queries for demo
            all_events = []
            
            for i, query in enumerate(queries, 1):
                self.print_substep(f"🔍 Query {i}/3: '{query[:50]}...'")
                
                # Show API call in real-time
                start_time = time.time()
                events = await intelligence._search_with_query(query, datetime.now())
                end_time = time.time()
                
                self.print_substep(f"   ⏱️  API call took {end_time - start_time:.2f} seconds")
                self.print_substep(f"   📊 Found {len(events)} events")
                
                all_events.extend(events)
                
                # Rate limiting delay
                await asyncio.sleep(1)
            
            # Step 4: Event Processing
            self.print_step("EVENT PROCESSING", "Analyzing and classifying discovered events")
            
            unique_events = intelligence._deduplicate_events(all_events)
            self.print_substep(f"📋 Total events before deduplication: {len(all_events)}")
            self.print_substep(f"🎯 Unique events after deduplication: {len(unique_events)}")
            
            if unique_events:
                self.print_substep("📈 Event Analysis:")
                for i, event in enumerate(unique_events[:3], 1):
                    self.print_substep(f"   {i}. {event.title[:60]}...")
                    self.print_substep(f"      Type: {event.event_type.value}")
                    self.print_substep(f"      Companies: {event.primary_company.name}")
                    if event.secondary_company:
                        self.print_substep(f"                 → {event.secondary_company.name}")
                    self.print_substep(f"      Confidence: {event.confidence_score}")
                    if event.deal_value:
                        self.print_substep(f"      Deal Value: ${event.deal_value:,.0f}")
            
            # Step 5: Notification Generation
            self.print_step("NOTIFICATION GENERATION", "Creating alerts for significant events")
            
            notifications_created = 0
            for event in unique_events:
                # Simulate notification logic
                if event.confidence_score >= 0.7:  # High confidence events
                    priority = "high"
                    notifications_created += 1
                    self.print_substep(f"🔔 HIGH PRIORITY: {event.title[:50]}...")
                elif event.deal_value and event.deal_value > 1_000_000:  # Large deals
                    priority = "medium"
                    notifications_created += 1
                    self.print_substep(f"📢 MEDIUM PRIORITY: ${event.deal_value:,.0f} deal")
            
            self.print_substep(f"📊 Total notifications created: {notifications_created}")
            
            # Step 6: Data Persistence
            self.print_step("DATA PERSISTENCE", "Saving events to storage for visualization")
            
            # Add events to agent's storage
            agent.events.extend(unique_events)
            
            # Create sample notifications
            from models.ma_events import NotificationEvent
            import uuid
            
            for event in unique_events[:2]:  # Create notifications for first 2 events
                notification = NotificationEvent(
                    id=str(uuid.uuid4()),
                    event_id=event.id,
                    notification_type="new_event",
                    title=f"New {event.event_type.value.replace('_', ' ').title()} Detected",
                    message=f"{event.primary_company.name} - {event.title[:50]}...",
                    priority="high" if event.confidence_score > 0.7 else "medium"
                )
                agent.notifications.append(notification)
            
            # Save data
            await agent._save_data()
            
            self.print_substep("💾 Events saved to ma_events.json")
            self.print_substep("🔔 Notifications saved to notifications.json")
            self.print_substep("📊 Data ready for visualization")
            
            # Step 7: Ecosystem Impact Analysis
            self.print_step("ECOSYSTEM IMPACT ANALYSIS", "Analyzing effects on startup ecosystem")
            
            # Load existing company data
            company_data = await agent._load_company_data()
            self.print_substep(f"📈 Loaded {len(company_data)} existing companies")
            
            impacts_created = 0
            for event in unique_events[:2]:  # Analyze first 2 events
                impact = await intelligence.analyze_ecosystem_impact(event, company_data)
                agent.impacts.append(impact)
                impacts_created += 1
                
                self.print_substep(f"🎯 Impact Analysis for {event.primary_company.name}:")
                self.print_substep(f"   Affected companies: {len(impact.affected_companies)}")
                self.print_substep(f"   Impact score: {impact.impact_score:.2f}")
                self.print_substep(f"   Description: {impact.description[:60]}...")
            
            self.print_substep(f"📊 Total impact analyses: {impacts_created}")
            
            # Step 8: Visualization Data Update
            self.print_step("VISUALIZATION DATA UPDATE", "Preparing data for graph updates")
            
            # Show how data would be used for visualization
            visualization_updates = []
            
            for event in unique_events:
                if event.event_type.value == "merger_acquisition":
                    update = {
                        "type": "add_edge",
                        "source": event.primary_company.name,
                        "target": event.secondary_company.name if event.secondary_company else "Unknown",
                        "edge_type": "acquisition",
                        "deal_value": event.deal_value,
                        "timestamp": event.discovered_at.isoformat()
                    }
                    visualization_updates.append(update)
                elif event.event_type.value == "strategic_alliance":
                    update = {
                        "type": "add_edge",
                        "source": event.primary_company.name,
                        "target": event.secondary_company.name if event.secondary_company else "Unknown",
                        "edge_type": "partnership",
                        "timestamp": event.discovered_at.isoformat()
                    }
                    visualization_updates.append(update)
            
            self.print_substep(f"🎨 Visualization updates prepared: {len(visualization_updates)}")
            
            for i, update in enumerate(visualization_updates[:3], 1):
                self.print_substep(f"   {i}. {update['type']}: {update['source']} → {update.get('target', 'N/A')}")
            
            # Step 9: API Endpoints Ready
            self.print_step("API ENDPOINTS READY", "Data available via REST API")
            
            self.print_substep("🌐 Available endpoints:")
            self.print_substep("   GET /ma-agent/events - Recent M&A events")
            self.print_substep("   GET /ma-agent/notifications - New notifications")
            self.print_substep("   GET /ma-agent/dashboard - Complete dashboard data")
            self.print_substep("   GET /ma-agent/impacts - Ecosystem impact analysis")
            
            # Step 10: Continuous Monitoring
            self.print_step("CONTINUOUS MONITORING", "Agent ready for real-time operation")
            
            self.print_substep("🔄 Agent will repeat this process every 60 seconds")
            self.print_substep("📊 Dashboard updates in real-time")
            self.print_substep("🔔 Notifications sent immediately when events found")
            self.print_substep("📈 Graph visualization data continuously updated")
            
            # Final Summary
            print(f"\n{'='*60}")
            print("🎉 WORKFLOW DEMONSTRATION COMPLETE")
            print(f"{'='*60}")
            print(f"📊 Summary:")
            print(f"   • Events discovered: {len(unique_events)}")
            print(f"   • Notifications created: {notifications_created}")
            print(f"   • Impact analyses: {impacts_created}")
            print(f"   • Visualization updates: {len(visualization_updates)}")
            print(f"   • Data files updated: 4")
            print()
            print("🚀 To see this in action:")
            print("   1. Run: ./start_ma_system.sh")
            print("   2. Visit: http://localhost:3000/ma-agent")
            print("   3. Watch real-time updates every 60 seconds!")

async def main():
    """Run the workflow demonstration"""
    demo = RealTimeWorkflowDemo()
    await demo.demonstrate_workflow()

if __name__ == "__main__":
    asyncio.run(main())
