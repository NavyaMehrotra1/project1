#!/usr/bin/env python3
"""
Vector Database Demo
Comprehensive demonstration of LangChain vector database capabilities
"""

import os
import sys
import logging
from pathlib import Path
from typing import List, Dict, Any

# Add backend to path
sys.path.append(str(Path(__file__).parent))

from services.vector_database_service import load_vector_db

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

class VectorDBDemo:
    def __init__(self):
        self.vector_db = load_vector_db("./chroma_db")
        if not self.vector_db:
            logger.error("Failed to load vector database. Run initialize_vector_db.py first.")
            sys.exit(1)
    
    def print_header(self, title: str):
        """Print formatted header"""
        print(f"\n{'='*60}")
        print(f"  {title}")
        print(f"{'='*60}")
    
    def print_results(self, results: List[Dict[str, Any]], max_results: int = 5):
        """Print search results in a formatted way"""
        for i, result in enumerate(results[:max_results], 1):
            metadata = result.get('metadata', {})
            company_name = metadata.get('company_name', 'Unknown')
            industry = metadata.get('industry', 'Unknown')
            valuation = metadata.get('valuation', 0)
            score = metadata.get('extraordinary_score', 0)
            
            valuation_str = f"${valuation/1_000_000_000:.1f}B" if valuation > 0 else "N/A"
            
            print(f"  {i}. {company_name}")
            print(f"     Industry: {industry} | Valuation: {valuation_str} | Score: {score}")
            print(f"     Content: {result['content'][:100]}...")
            print()
    
    def demo_basic_search(self):
        """Demonstrate basic semantic search"""
        self.print_header("BASIC SEMANTIC SEARCH")
        
        queries = [
            "artificial intelligence companies",
            "financial technology startups",
            "companies with billion dollar valuations",
            "exceptional performing companies",
            "healthcare and medical technology"
        ]
        
        for query in queries:
            print(f"\n🔍 Query: '{query}'")
            results = self.vector_db.semantic_search(query, k=3)
            self.print_results(results, 3)
    
    def demo_industry_search(self):
        """Demonstrate industry-specific searches"""
        self.print_header("INDUSTRY-SPECIFIC SEARCHES")
        
        industry_queries = [
            ("AI & Machine Learning", "machine learning artificial intelligence neural networks"),
            ("Fintech & Payments", "payments banking financial services cryptocurrency"),
            ("Developer Tools", "developer tools software engineering programming"),
            ("Healthcare & Biotech", "healthcare medical biotech pharmaceuticals"),
            ("E-commerce & Marketplace", "e-commerce marketplace online retail shopping")
        ]
        
        for industry, query in industry_queries:
            print(f"\n🏢 {industry}")
            results = self.vector_db.search_companies(query, k=3)
            self.print_results(results, 3)
    
    def demo_valuation_search(self):
        """Demonstrate valuation-based searches"""
        self.print_header("VALUATION-BASED SEARCHES")
        
        valuation_queries = [
            "unicorn companies billion dollar valuation",
            "high value exceptional companies",
            "most valuable startups",
            "companies with highest extraordinary scores"
        ]
        
        for query in valuation_queries:
            print(f"\n💰 Query: '{query}'")
            results = self.vector_db.search_companies(query, k=3)
            self.print_results(results, 3)
    
    def demo_similar_companies(self):
        """Demonstrate similar company searches"""
        self.print_header("SIMILAR COMPANY DISCOVERY")
        
        reference_companies = ["OpenAI", "Stripe", "Airbnb", "Anthropic", "Notion"]
        
        for company in reference_companies:
            print(f"\n🔗 Companies similar to {company}:")
            results = self.vector_db.get_similar_companies(company, k=3)
            self.print_results(results, 3)
    
    def demo_advanced_queries(self):
        """Demonstrate advanced semantic queries"""
        self.print_header("ADVANCED SEMANTIC QUERIES")
        
        advanced_queries = [
            "companies that are disrupting traditional industries",
            "startups with strong network effects and platform business models",
            "companies focused on automation and productivity tools",
            "emerging companies with high growth potential",
            "companies that went public successfully"
        ]
        
        for query in advanced_queries:
            print(f"\n🚀 Query: '{query}'")
            results = self.vector_db.semantic_search(query, k=3)
            self.print_results(results, 3)
    
    def demo_batch_analysis(self):
        """Demonstrate Y Combinator batch analysis"""
        self.print_header("Y COMBINATOR BATCH ANALYSIS")
        
        batch_queries = [
            "companies from recent Y Combinator batches",
            "successful companies from early YC batches",
            "Winter batch companies",
            "Summer batch companies"
        ]
        
        for query in batch_queries:
            print(f"\n📅 Query: '{query}'")
            results = self.vector_db.search_companies(query, k=3)
            self.print_results(results, 3)
    
    def demo_database_stats(self):
        """Show database statistics"""
        self.print_header("DATABASE STATISTICS")
        
        stats = self.vector_db.get_database_stats()
        
        print(f"📊 Total Documents: {stats.get('total_documents', 'Unknown')}")
        print(f"🧠 Embedding Model: {stats.get('embedding_model', 'Unknown')}")
        print(f"📁 Storage Location: {stats.get('persist_directory', 'Unknown')}")
        print(f"⏰ Created: {stats.get('created_at', 'Unknown')}")
    
    def run_full_demo(self):
        """Run the complete demonstration"""
        print("🎯 LANGCHAIN VECTOR DATABASE DEMO")
        print("Showcasing semantic search capabilities with Y Combinator company data")
        
        self.demo_database_stats()
        self.demo_basic_search()
        self.demo_industry_search()
        self.demo_valuation_search()
        self.demo_similar_companies()
        self.demo_advanced_queries()
        self.demo_batch_analysis()
        
        print(f"\n{'='*60}")
        print("  ✅ DEMO COMPLETE")
        print(f"{'='*60}")
        print("\n🔧 API Endpoints Available:")
        print("  • POST /api/vector-search/search")
        print("  • GET  /api/vector-search/search?q=query")
        print("  • POST /api/vector-search/companies/search")
        print("  • POST /api/vector-search/companies/similar")
        print("  • GET  /api/vector-search/stats")
        print("  • POST /api/vector-search/rebuild")

def main():
    """Main demo function"""
    try:
        demo = VectorDBDemo()
        demo.run_full_demo()
    except KeyboardInterrupt:
        print("\n\n👋 Demo interrupted by user")
    except Exception as e:
        logger.error(f"Demo failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
