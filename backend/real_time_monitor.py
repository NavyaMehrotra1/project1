#!/usr/bin/env python3
"""
Real-time Vector Database Monitor
Shows live updates as they're added to the ChromaDB vector database
"""

import asyncio
import json
import time
from datetime import datetime
from typing import Dict, List
import sys
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).parent))

from services.real_time_data_agent import RealTimeDataAgent

class RealTimeMonitor:
    def __init__(self):
        self.agent = RealTimeDataAgent()
        self.last_update_count = 0
        
    def display_header(self):
        """Display monitoring header"""
        print("\n" + "="*80)
        print("🔴 LIVE: Real-time Vector Database Updates")
        print("="*80)
        print("Monitoring company data from Reddit, Hacker News, and other sources...")
        print("Updates will appear below as they're added to ChromaDB")
        print("Press Ctrl+C to stop")
        print("-"*80)
    
    def display_update(self, update: Dict):
        """Display a single update in real-time"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        company = update.get('company', 'Unknown')
        update_type = update.get('type', 'news').upper()
        source = update.get('source', 'Unknown')
        confidence = update.get('confidence', 0)
        content = update.get('content', '')[:100] + "..." if len(update.get('content', '')) > 100 else update.get('content', '')
        url = update.get('url', '')
        
        # Color coding for different update types
        type_colors = {
            'FUNDING': '💰',
            'DEAL': '🤝',
            'PARTNERSHIP': '🤝',
            'COMPETITION': '⚔️',
            'NEWS': '📰'
        }
        
        icon = type_colors.get(update_type, '📰')
        
        print(f"\n[{timestamp}] {icon} NEW UPDATE ADDED TO VECTOR DB")
        print(f"   Company: {company}")
        print(f"   Type: {update_type}")
        print(f"   Source: {source}")
        print(f"   Confidence: {confidence:.2f}")
        print(f"   Content: {content}")
        if url:
            print(f"   🔗 Source URL: {url}")
        print(f"   → Added to ChromaDB collection: company_updates")
        print("-"*80)
    
    def display_stats(self):
        """Display current database statistics"""
        try:
            companies_count = self.agent.companies_collection.count()
            updates_count = self.agent.updates_collection.count()
            recent_updates = len(self.agent.get_recent_updates(10))
            
            print(f"\n📊 CURRENT DATABASE STATS:")
            print(f"   Companies indexed: {companies_count}")
            print(f"   Total updates: {updates_count}")
            print(f"   Recent updates (last 10): {recent_updates}")
            
        except Exception as e:
            print(f"   Error getting stats: {e}")
    
    async def monitor_updates(self):
        """Monitor for new updates and display them in real-time"""
        self.display_header()
        self.display_stats()
        
        while True:
            try:
                # Check for new updates
                current_updates = self.agent.get_recent_updates(50)
                
                if len(current_updates) > self.last_update_count:
                    # New updates found
                    new_updates = current_updates[self.last_update_count:]
                    
                    for update in new_updates:
                        self.display_update(update)
                    
                    self.last_update_count = len(current_updates)
                
                # Wait before checking again
                await asyncio.sleep(5)
                
            except KeyboardInterrupt:
                print("\n\n🛑 Monitoring stopped by user")
                break
            except Exception as e:
                print(f"\n❌ Monitor error: {e}")
                await asyncio.sleep(5)

async def run_agent_and_monitor():
    """Run both the data agent and monitor concurrently"""
    agent = RealTimeDataAgent()
    monitor = RealTimeMonitor()
    
    # Start both tasks concurrently
    agent_task = asyncio.create_task(agent.run_continuous_monitoring())
    monitor_task = asyncio.create_task(monitor.monitor_updates())
    
    try:
        await asyncio.gather(agent_task, monitor_task)
    except KeyboardInterrupt:
        print("\n👋 Shutting down real-time monitoring system...")
        agent_task.cancel()
        monitor_task.cancel()

def main():
    """Main function"""
    print("🚀 Starting Real-time Vector Database Monitoring System")
    print("This will show live updates as company data is added to ChromaDB")
    
    try:
        asyncio.run(run_agent_and_monitor())
    except KeyboardInterrupt:
        print("\n👋 Real-time monitoring stopped")

if __name__ == "__main__":
    main()
