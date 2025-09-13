#!/usr/bin/env python3
"""
Enhanced DealFlow Backend Startup Script
Automatically loads YC data and starts the FastAPI server with WebSocket support
"""

import os
import sys
import subprocess
from pathlib import Path

def check_requirements():
    """Check if required packages are installed"""
    required_packages = [
        'fastapi', 'uvicorn', 'pydantic', 'python-dotenv', 
        'aiohttp', 'requests', 'pandas', 'networkx'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"Missing packages: {', '.join(missing_packages)}")
        print("Installing requirements...")
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", "requirements-enhanced.txt"
        ])

def start_server():
    """Start the FastAPI server"""
    print("🚀 Starting Enhanced DealFlow Backend...")
    print("📊 Loading YC Top 100 companies data...")
    print("🔗 WebSocket support enabled for real-time updates")
    print("🌐 Server will be available at: http://localhost:8000")
    print("📡 WebSocket endpoint: ws://localhost:8000/ws")
    print("📖 API docs: http://localhost:8000/docs")
    print("\n" + "="*50)
    
    # Change to backend directory
    backend_dir = Path(__file__).parent
    os.chdir(backend_dir)
    
    # Start uvicorn server
    subprocess.run([
        sys.executable, "-m", "uvicorn", 
        "enhanced_main:app", 
        "--host", "0.0.0.0", 
        "--port", "8000", 
        "--reload",
        "--log-level", "info"
    ])

if __name__ == "__main__":
    try:
        check_requirements()
        start_server()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)
