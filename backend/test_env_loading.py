#!/usr/bin/env python3
"""
Test .env file loading to debug API key issues
"""

import os
from pathlib import Path
from dotenv import load_dotenv

def test_env_loading():
    print("🔍 Testing .env file loading...")
    
    # Check if .env file exists
    env_path = Path(__file__).parent / ".env"
    print(f"Looking for .env at: {env_path}")
    print(f".env file exists: {env_path.exists()}")
    
    if env_path.exists():
        print(f".env file size: {env_path.stat().st_size} bytes")
        
        # Load the .env file
        load_dotenv(env_path)
        print("✅ Loaded .env file")
        
        # Check for API keys
        exa_key = os.getenv("EXA_API_KEY")
        claude_key = os.getenv("ANTHROPIC_API_KEY")
        
        print(f"EXA_API_KEY found: {'Yes' if exa_key else 'No'}")
        if exa_key:
            print(f"EXA_API_KEY length: {len(exa_key)} characters")
            print(f"EXA_API_KEY starts with: {exa_key[:10]}...")
        
        print(f"ANTHROPIC_API_KEY found: {'Yes' if claude_key else 'No'}")
        if claude_key:
            print(f"ANTHROPIC_API_KEY length: {len(claude_key)} characters")
            print(f"ANTHROPIC_API_KEY starts with: {claude_key[:10]}...")
            
        # Test Exa client initialization
        if exa_key:
            try:
                from exa_py import Exa
                client = Exa(api_key=exa_key)
                print("✅ Exa client initialized successfully")
                
                # Test a simple search
                print("🔍 Testing Exa API with simple search...")
                results = client.search("OpenAI ChatGPT", num_results=1)
                print(f"✅ Exa API test successful - found {len(results.results)} results")
                
            except ImportError:
                print("❌ exa_py not installed")
            except Exception as e:
                print(f"❌ Exa client error: {e}")
        
        # Test Claude client
        if claude_key:
            try:
                import anthropic
                client = anthropic.Anthropic(api_key=claude_key)
                print("✅ Claude client initialized successfully")
            except ImportError:
                print("❌ anthropic not installed")
            except Exception as e:
                print(f"❌ Claude client error: {e}")
                
    else:
        print("❌ .env file not found")
        print("Current directory contents:")
        for item in Path(__file__).parent.iterdir():
            if not item.name.startswith('.git'):
                print(f"  {item.name}")

if __name__ == "__main__":
    test_env_loading()
