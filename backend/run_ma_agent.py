#!/usr/bin/env python3
"""
Standalone script to run the M&A monitoring agent
"""

import asyncio
import logging
import signal
import sys
import os
from pathlib import Path

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.ma_monitoring_agent import MAMonitoringAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('ma_agent.log')
    ]
)

logger = logging.getLogger(__name__)

# Global agent instance
agent = None

def signal_handler(signum, frame):
    """Handle shutdown signals gracefully"""
    logger.info(f"Received signal {signum}, shutting down...")
    if agent:
        asyncio.create_task(agent.stop_monitoring())
    sys.exit(0)

async def main():
    """Main function to run the M&A monitoring agent"""
    global agent
    
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    logger.info("🚀 Starting M&A Intelligence Agent...")
    
    try:
        # Initialize the agent
        agent = MAMonitoringAgent()
        
        # Start monitoring
        await agent.start_monitoring()
        
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt, shutting down...")
    except Exception as e:
        logger.error(f"Agent error: {e}")
        raise
    finally:
        if agent:
            await agent.stop_monitoring()
        logger.info("🛑 M&A Intelligence Agent stopped")

if __name__ == "__main__":
    print("=" * 60)
    print("🤖 M&A Intelligence Agent")
    print("Real-time monitoring of mergers, acquisitions, and partnerships")
    print("=" * 60)
    print()
    
    # Check for required environment variables
    if not os.getenv('EXA_API_KEY'):
        print("❌ Error: EXA_API_KEY environment variable not set")
        print("Please set your Exa API key in the .env file")
        sys.exit(1)
    
    print("✅ Environment configured")
    print("🔍 Starting monitoring...")
    print()
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"\n💥 Fatal error: {e}")
        sys.exit(1)
