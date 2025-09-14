#!/usr/bin/env python3
"""
Run Extraordinary Research Enhancement
Demonstrates the AI-powered deep research capabilities for companies in the graph
"""

import asyncio
import os
import sys
import logging
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).parent))

from services.graph_extraordinary_integration_service import GraphExtraordinaryIntegrationService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def demonstrate_deep_research():
    """
    Demonstrate the comprehensive AI-powered deep research capabilities
    
    This showcases how we use:
    1. Exa API for web-scale search across premium sources
    2. Claude AI for intelligent content analysis and extraction
    3. Multi-strategy research queries for comprehensive coverage
    4. Advanced scoring and ranking algorithms
    """
    
    print("🔬 EXTRAORDINARY DEEP RESEARCH DEMONSTRATION")
    print("=" * 60)
    print()
    
    # Check API keys
    exa_api_key = os.getenv("EXA_API_KEY")
    claude_api_key = os.getenv("ANTHROPIC_API_KEY")
    
    print("🔑 API Configuration:")
    print(f"   Exa API: {'✅ Available' if exa_api_key else '❌ Missing (set EXA_API_KEY)'}")
    print(f"   Claude AI: {'✅ Available' if claude_api_key else '❌ Missing (set ANTHROPIC_API_KEY)'}")
    print()
    
    if not exa_api_key:
        print("⚠️  Without Exa API, research will be limited to basic structure")
        print("   Get your API key from: https://exa.ai")
        print()
    
    if not claude_api_key:
        print("⚠️  Without Claude AI, content analysis will be basic")
        print("   Get your API key from: https://console.anthropic.com")
        print()
    
    # Initialize service
    service = GraphExtraordinaryIntegrationService(exa_api_key=exa_api_key)
    
    print("🎯 RESEARCH METHODOLOGY:")
    print("=" * 40)
    print("1. 🌐 WEB-SCALE SEARCH")
    print("   • Exa API searches across premium sources (Forbes, TechCrunch, Bloomberg)")
    print("   • Neural and keyword search strategies for comprehensive coverage")
    print("   • Domain filtering to focus on high-quality sources")
    print("   • Time-based filtering for recent and relevant content")
    print()
    
    print("2. 🤖 AI-POWERED ANALYSIS")
    print("   • Claude AI analyzes content for extraordinary achievements")
    print("   • Extracts key quotes, metrics, and impact descriptions")
    print("   • Identifies patterns in recognition and award data")
    print("   • Scores impressiveness and significance of discoveries")
    print()
    
    print("3. 📊 COMPREHENSIVE PROFILING")
    print("   • Notable articles with relevance scoring")
    print("   • Awards and recognitions with prestige ranking")
    print("   • Extraordinary feats with impact analysis")
    print("   • Company statistics from multiple sources")
    print()
    
    print("4. 🔗 GRAPH INTEGRATION")
    print("   • Enhanced data integrated into graph_data_for_frontend.json")
    print("   • Maintains existing structure while adding rich research data")
    print("   • Provides summary scores and metadata for visualization")
    print()
    
    # Ask user which companies to research
    print("🏢 SELECT COMPANIES FOR DEEP RESEARCH:")
    print("=" * 40)
    print("Choose an option:")
    print("1. Research top 3 high-value companies (recommended for demo)")
    print("2. Research specific companies (enter names)")
    print("3. Research all companies (may take 30+ minutes)")
    print()
    
    try:
        choice = input("Enter choice (1-3): ").strip()
        
        if choice == "1":
            # Research top companies
            print("\n🔍 Starting deep research for top 3 companies...")
            result = await service.enhance_graph_with_extraordinary_profiles(
                max_companies=3,
                force_regenerate=True
            )
            
        elif choice == "2":
            # Research specific companies
            companies = input("Enter company names (comma-separated): ").strip()
            company_list = [c.strip() for c in companies.split(",") if c.strip()]
            
            if company_list:
                print(f"\n🔍 Starting deep research for: {', '.join(company_list)}")
                result = await service.enhance_graph_with_extraordinary_profiles(
                    target_companies=company_list,
                    max_companies=len(company_list),
                    force_regenerate=True
                )
            else:
                print("❌ No companies specified")
                return
                
        elif choice == "3":
            # Research all companies
            confirm = input("This may take 30+ minutes. Continue? (y/N): ").strip().lower()
            if confirm == 'y':
                print("\n🔍 Starting comprehensive research for all companies...")
                result = await service.enhance_graph_with_extraordinary_profiles(
                    max_companies=50,
                    force_regenerate=True
                )
            else:
                print("❌ Cancelled")
                return
        else:
            print("❌ Invalid choice")
            return
        
        # Display results
        print("\n" + "=" * 60)
        print("🎉 DEEP RESEARCH RESULTS")
        print("=" * 60)
        print(f"Companies processed: {result['companies_processed']}")
        print(f"Profiles generated: {result['profiles_generated']}")
        print(f"Errors encountered: {len(result['errors'])}")
        print()
        
        if result['research_summary']:
            print("📊 RESEARCH QUALITY METRICS:")
            print("-" * 30)
            
            for company_id, summary in result['research_summary'].items():
                print(f"\n🏢 {summary['company_name']}:")
                print(f"   📰 Articles found: {summary['articles_found']}")
                print(f"   🏆 Recognitions: {summary['recognitions_found']}")
                print(f"   🚀 Extraordinary feats: {summary['extraordinary_feats']}")
                print(f"   📊 Overall score: {summary['overall_score']:.2f}")
                print(f"   🔍 Research depth: {summary['research_depth_score']:.2f}")
                print(f"   📚 Sources analyzed: {summary['sources_analyzed']}")
                print(f"   🤖 AI enhanced: {'Yes' if summary['ai_enhanced'] else 'No'}")
        
        if result['errors']:
            print("\n❌ ERRORS:")
            for error in result['errors']:
                print(f"   • {error}")
        
        print(f"\n✅ Enhanced graph data saved to graph_data_for_frontend.json")
        print("\nThe graph now contains rich extraordinary profiles with:")
        print("• Deep research articles and analysis")
        print("• Awards and recognition data")
        print("• Extraordinary achievements and feats")
        print("• AI-enhanced company statistics")
        print("• Comprehensive scoring and metadata")
        
    except KeyboardInterrupt:
        print("\n❌ Research cancelled by user")
    except Exception as e:
        print(f"\n❌ Error during research: {e}")
        logger.error(f"Research error: {e}", exc_info=True)

if __name__ == "__main__":
    asyncio.run(demonstrate_deep_research())
