#!/usr/bin/env python3
"""
Rebuild Vector Databases with Updated Confidence Values
Updates both chroma_db and chroma_db_v2 with the latest graph data
"""

import os
import sys
import json
import shutil
import logging
from pathlib import Path
from datetime import datetime

# Add backend to path
sys.path.append(str(Path(__file__).parent))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def rebuild_vector_databases():
    """Rebuild both vector databases with updated graph data"""
    
    # Paths
    graph_data_path = "../data_agent/data_agent/output/graph_data_for_frontend.json"
    db_paths = ["./chroma_db", "./chroma_db_v2"]
    
    # Check if graph data exists
    if not os.path.exists(graph_data_path):
        logger.error(f"Graph data file not found: {graph_data_path}")
        return False
    
    # Load and verify graph data
    try:
        with open(graph_data_path, 'r') as f:
            graph_data = json.load(f)
        logger.info(f"✅ Loaded graph data with {len(graph_data.get('nodes', []))} nodes and {len(graph_data.get('edges', []))} edges")
        
        # Check confidence scores in edges
        confidence_scores = []
        for edge in graph_data.get('edges', []):
            if 'data' in edge and 'confidence_score' in edge['data']:
                confidence_scores.append(edge['data']['confidence_score'])
        
        if confidence_scores:
            unique_scores = set(confidence_scores)
            logger.info(f"Found {len(confidence_scores)} confidence scores with unique values: {unique_scores}")
            
            if len(unique_scores) == 1 and 1 in unique_scores:
                logger.info("✅ All confidence scores are set to 1 as expected")
            else:
                logger.warning(f"⚠️ Confidence scores are not all set to 1: {unique_scores}")
        
    except Exception as e:
        logger.error(f"Error loading graph data: {e}")
        return False
    
    # Import vector database service
    try:
        from services.vector_database_service import VectorDatabaseService
    except ImportError as e:
        logger.error(f"Failed to import VectorDatabaseService: {e}")
        return False
    
    success_count = 0
    
    # Rebuild each database
    for db_path in db_paths:
        logger.info(f"\n🔄 Rebuilding vector database: {db_path}")
        
        # Remove existing database
        if os.path.exists(db_path):
            logger.info(f"🗑️ Removing existing database: {db_path}")
            shutil.rmtree(db_path)
        
        # Create new database
        try:
            vector_db = VectorDatabaseService(persist_directory=db_path)
            
            if vector_db.build_vector_database(graph_data_path):
                logger.info(f"✅ Successfully rebuilt {db_path}")
                
                # Get stats
                stats = vector_db.get_database_stats()
                logger.info(f"Database stats: {stats}")
                success_count += 1
                
                # Test search
                test_results = vector_db.semantic_search("AI companies", k=2)
                logger.info(f"Test search returned {len(test_results)} results")
                
            else:
                logger.error(f"❌ Failed to rebuild {db_path}")
                
        except Exception as e:
            logger.error(f"❌ Error rebuilding {db_path}: {e}")
    
    if success_count == len(db_paths):
        logger.info(f"\n🎉 Successfully rebuilt all {len(db_paths)} vector databases!")
        logger.info("Vector databases now support the updated confidence values of 1")
        return True
    else:
        logger.error(f"\n❌ Only {success_count}/{len(db_paths)} databases rebuilt successfully")
        return False

if __name__ == "__main__":
    success = rebuild_vector_databases()
    sys.exit(0 if success else 1)
