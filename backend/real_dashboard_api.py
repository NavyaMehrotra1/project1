#!/usr/bin/env python3
"""
Real Dashboard API
Serves actual ChromaDB data to the web dashboard
"""

import json
import time
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import sys
from pathlib import Path

# Add backend to path
sys.path.append('/Users/sutharsikakumar/project1-1/backend')

try:
    from services.real_time_data_agent import RealTimeDataAgent
    AGENT_AVAILABLE = True
except ImportError:
    AGENT_AVAILABLE = False

class DashboardAPIHandler(BaseHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        if AGENT_AVAILABLE:
            self.agent = RealTimeDataAgent()
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == '/api/updates':
            self.serve_updates()
        elif parsed_path.path == '/api/stats':
            self.serve_stats()
        elif parsed_path.path == '/web_dashboard.html':
            self.serve_dashboard()
        else:
            self.send_error(404)
    
    def serve_updates(self):
        """Serve recent updates from ChromaDB"""
        if not AGENT_AVAILABLE:
            self.send_json_response([])
            return
            
        try:
            # Get recent updates from the agent's log
            recent_updates = self.agent.get_recent_updates(50)
            
            # Format for dashboard
            formatted_updates = []
            for update in recent_updates:
                formatted_updates.append({
                    'id': f"{update['company']}_{update['timestamp']}",
                    'company': update['company'],
                    'type': update['type'],
                    'content': update['content'],
                    'timestamp': update['timestamp'],
                    'confidence': update['confidence'],
                    'source': update['source'],
                    'url': update.get('url', '')
                })
            
            self.send_json_response(formatted_updates)
            
        except Exception as e:
            print(f"Error serving updates: {e}")
            self.send_json_response([])
    
    def serve_stats(self):
        """Serve database statistics"""
        if not AGENT_AVAILABLE:
            self.send_json_response({
                'totalUpdates': 0,
                'companiesTracked': 0,
                'updatesPerMinute': 0,
                'avgConfidence': 0
            })
            return
            
        try:
            companies_count = self.agent.companies_collection.count()
            updates_count = self.agent.updates_collection.count()
            recent_updates = self.agent.get_recent_updates(10)
            
            # Calculate average confidence
            avg_confidence = 0
            if recent_updates:
                avg_confidence = sum(u['confidence'] for u in recent_updates) / len(recent_updates)
            
            stats = {
                'totalUpdates': updates_count,
                'companiesTracked': companies_count,
                'updatesPerMinute': len(recent_updates),  # Simplified
                'avgConfidence': round(avg_confidence * 100)
            }
            
            self.send_json_response(stats)
            
        except Exception as e:
            print(f"Error serving stats: {e}")
            self.send_json_response({
                'totalUpdates': 0,
                'companiesTracked': 0,
                'updatesPerMinute': 0,
                'avgConfidence': 0
            })
    
    def serve_dashboard(self):
        """Serve the dashboard HTML with real data integration"""
        try:
            dashboard_path = Path('/Users/sutharsikakumar/project1-1/backend/web_dashboard_real.html')
            if dashboard_path.exists():
                with open(dashboard_path, 'r') as f:
                    content = f.read()
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.send_header('Cache-Control', 'no-cache')
                self.end_headers()
                self.wfile.write(content.encode())
            else:
                self.send_error(404, "Dashboard not found")
        except Exception as e:
            print(f"Error serving dashboard: {e}")
            self.send_error(500)
    
    def send_json_response(self, data):
        """Send JSON response with CORS headers"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Cache-Control', 'no-cache')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

def main():
    port = 8081
    server = HTTPServer(('localhost', port), DashboardAPIHandler)
    print(f"🌐 Real Dashboard API Server")
    print(f"📊 Serving at: http://localhost:{port}/web_dashboard.html")
    print(f"🔗 API endpoints:")
    print(f"   - /api/updates (recent updates)")
    print(f"   - /api/stats (database statistics)")
    print(f"Press Ctrl+C to stop")
    print("-" * 60)
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 API server stopped")

if __name__ == "__main__":
    main()
