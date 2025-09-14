#!/usr/bin/env python3
"""
Create Parallel Vector Database
Creates a new ChromaDB instance alongside the existing one
"""

import os
import sys
import logging
from pathlib import Path
from datetime import datetime

# Add backend to path
sys.path.append(str(Path(__file__).parent))

from services.vector_database_service import VectorDatabaseService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Create a parallel vector database instance"""
    
    # Paths
    graph_data_path = "../data_agent/data_agent/output/graph_data_for_frontend.json"
    original_db_path = "./chroma_db"
    new_db_path = "./chroma_db_v2"
    
    # Check if graph data exists
    if not os.path.exists(graph_data_path):
        logger.error(f"Graph data file not found: {graph_data_path}")
        return False
    
    # Check existing databases
    if os.path.exists(original_db_path):
        logger.info(f"✅ Original database exists at: {original_db_path}")
    else:
        logger.warning(f"⚠️ Original database not found at: {original_db_path}")
    
    if os.path.exists(new_db_path):
        logger.info(f"📁 New database directory already exists: {new_db_path}")
        response = input("Delete existing v2 database and recreate? (y/N): ")
        if response.lower() != 'y':
            logger.info("Cancelled.")
            return False
        
        # Remove existing v2 database
        import shutil
        shutil.rmtree(new_db_path)
        logger.info("🗑️ Removed existing v2 database")
    
    logger.info("🚀 Creating parallel vector database...")
    logger.info(f"Graph data: {graph_data_path}")
    logger.info(f"New database location: {new_db_path}")
    
    # Create new vector database instance
    vector_db = VectorDatabaseService(persist_directory=new_db_path)
    
    # Build the database
    success = vector_db.build_vector_database(graph_data_path)
    
    if not success:
        logger.error("❌ Failed to create parallel vector database")
        return False
    
    # Get stats for both databases
    new_stats = vector_db.get_database_stats()
    logger.info("✅ Parallel vector database created successfully!")
    logger.info(f"New database stats: {new_stats}")
    
    # Compare with original if it exists
    if os.path.exists(original_db_path):
        try:
            from services.vector_database_service import load_vector_db
            original_db = load_vector_db(original_db_path)
            if original_db:
                original_stats = original_db.get_database_stats()
                logger.info(f"Original database stats: {original_stats}")
                
                # Compare document counts
                new_count = new_stats.get('total_documents', 0)
                original_count = original_stats.get('total_documents', 0)
                
                logger.info(f"\n📊 Database Comparison:")
                logger.info(f"  Original: {original_count} documents")
                logger.info(f"  New (v2): {new_count} documents")
                logger.info(f"  Difference: {new_count - original_count} documents")
        except Exception as e:
            logger.warning(f"Could not compare with original database: {e}")
    
    # Test the new database
    logger.info("\n🧪 Testing new database...")
    test_queries = [
        "AI companies",
        "fintech startups", 
        "high valuation companies"
    ]
    
    for query in test_queries:
        results = vector_db.semantic_search(query, k=2)
        logger.info(f"Query '{query}': {len(results)} results")
        if results:
            first_result = results[0]['metadata'].get('company_name', 'Unknown')
            logger.info(f"  Top result: {first_result}")
    
    logger.info(f"\n✅ Parallel database setup complete!")
    logger.info(f"Original database: {original_db_path}")
    logger.info(f"New database (v2): {new_db_path}")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
