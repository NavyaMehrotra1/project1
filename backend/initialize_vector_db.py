#!/usr/bin/env python3
"""
Initialize Vector Database from Graph Data
Creates and populates the LangChain vector database with company data
"""

import os
import sys
import logging
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).parent))

from services.vector_database_service import VectorDatabaseService, create_vector_db_from_graph

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Initialize the vector database"""
    
    # Paths
    graph_data_path = "../data_agent/data_agent/output/graph_data_for_frontend.json"
    persist_dir = "./chroma_db"
    
    # Check if graph data exists
    if not os.path.exists(graph_data_path):
        logger.error(f"Graph data file not found: {graph_data_path}")
        return False
    
    logger.info("Initializing vector database from graph data...")
    logger.info(f"Graph data: {graph_data_path}")
    logger.info(f"Persist directory: {persist_dir}")
    
    # Create vector database
    vector_db = create_vector_db_from_graph(graph_data_path, persist_dir)
    
    if vector_db is None:
        logger.error("Failed to create vector database")
        return False
    
    # Get stats
    stats = vector_db.get_database_stats()
    logger.info("Vector database created successfully!")
    logger.info(f"Stats: {stats}")
    
    # Test some searches
    logger.info("\n=== Testing Vector Database ===")
    
    test_queries = [
        "AI companies with high valuations",
        "fintech startups",
        "companies similar to Stripe",
        "exceptional performers"
    ]
    
    for query in test_queries:
        logger.info(f"\nTesting query: '{query}'")
        results = vector_db.semantic_search(query, k=3)
        
        for i, result in enumerate(results, 1):
            company_name = result['metadata'].get('company_name', 'Unknown')
            industry = result['metadata'].get('industry', 'Unknown')
            logger.info(f"  {i}. {company_name} ({industry})")
    
    # Test similar companies
    logger.info(f"\n=== Testing Similar Companies ===")
    similar_to_openai = vector_db.get_similar_companies("OpenAI", k=3)
    logger.info("Companies similar to OpenAI:")
    for i, result in enumerate(similar_to_openai, 1):
        company_name = result['metadata'].get('company_name', 'Unknown')
        industry = result['metadata'].get('industry', 'Unknown')
        logger.info(f"  {i}. {company_name} ({industry})")
    
    logger.info("\nVector database initialization complete!")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
