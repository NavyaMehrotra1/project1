#!/usr/bin/env python3
"""
Simple HTTP server to serve the real-time vector database dashboard
"""

import http.server
import socketserver
import webbrowser
import os
from pathlib import Path

def serve_dashboard():
    """Serve the web dashboard on localhost"""
    
    # Change to the backend directory
    os.chdir('/Users/sutharsikakumar/project1-1/backend')
    
    PORT = 8080
    
    class CustomHandler(http.server.SimpleHTTPRequestHandler):
        def end_headers(self):
            self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Expires', '0')
            super().end_headers()
    
    try:
        with socketserver.TCPServer(("", PORT), CustomHandler) as httpd:
            print(f"🌐 Real-time Vector Database Dashboard")
            print(f"📊 Serving at: http://localhost:{PORT}/web_dashboard.html")
            print(f"🔴 Live updates will appear automatically")
            print(f"Press Ctrl+C to stop the server")
            print("-" * 60)
            
            # Try to open browser automatically
            try:
                webbrowser.open(f'http://localhost:{PORT}/web_dashboard.html')
                print("✅ Dashboard opened in your default browser")
            except:
                print("⚠️  Please manually open: http://localhost:{PORT}/web_dashboard.html")
            
            httpd.serve_forever()
            
    except KeyboardInterrupt:
        print("\n🛑 Dashboard server stopped")
    except Exception as e:
        print(f"❌ Server error: {e}")

if __name__ == "__main__":
    serve_dashboard()
