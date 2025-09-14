#!/usr/bin/env python3
"""
Simple Vector Database Rebuild Script
Uses direct ChromaDB without LangChain wrapper
"""

import os
import sys
import json
import shutil
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def rebuild_with_chromadb():
    """Rebuild vector databases using direct ChromaDB"""
    
    try:
        import chromadb
        from sentence_transformers import SentenceTransformer
    except ImportError as e:
        logger.error(f"Required packages not available: {e}")
        return False
    
    # Paths
    graph_data_path = "../data_agent/data_agent/output/graph_data_for_frontend.json"
    db_paths = ["./chroma_db", "./chroma_db_v2"]
    
    # Load graph data
    try:
        with open(graph_data_path, 'r') as f:
            graph_data = json.load(f)
        logger.info(f"✅ Loaded graph data with {len(graph_data.get('nodes', []))} nodes and {len(graph_data.get('edges', []))} edges")
    except Exception as e:
        logger.error(f"Error loading graph data: {e}")
        return False
    
    # Initialize embedding model
    try:
        model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
        logger.info("✅ Initialized SentenceTransformer model")
    except Exception as e:
        logger.error(f"Error initializing embedding model: {e}")
        return False
    
    success_count = 0
    
    for db_path in db_paths:
        logger.info(f"\n🔄 Rebuilding vector database: {db_path}")
        
        # Remove existing database
        if os.path.exists(db_path):
            logger.info(f"🗑️ Removing existing database: {db_path}")
            shutil.rmtree(db_path)
        
        try:
            # Create ChromaDB client
            client = chromadb.PersistentClient(path=db_path)
            collection = client.create_collection(
                name="graph_data",
                metadata={"description": "Graph data with confidence scores set to 1"}
            )
            
            # Prepare documents and embeddings
            documents = []
            metadatas = []
            ids = []
            
            # Process nodes (companies)
            for i, node in enumerate(graph_data.get('nodes', [])):
                data = node.get('data', {})
                company_name = data.get('name', node.get('label', f'Company_{i}'))
                
                # Create text representation
                text_parts = [f"Company: {company_name}"]
                if data.get('industry'):
                    text_parts.append(f"Industry: {data['industry']}")
                if data.get('batch'):
                    text_parts.append(f"Y Combinator Batch: {data['batch']}")
                if data.get('valuation'):
                    valuation_b = data['valuation'] / 1_000_000_000
                    text_parts.append(f"Valuation: ${valuation_b:.1f}B")
                
                document_text = ". ".join(text_parts) + "."
                documents.append(document_text)
                
                metadatas.append({
                    'type': 'company',
                    'company_id': node.get('id', f'node_{i}'),
                    'company_name': company_name,
                    'industry': data.get('industry', ''),
                    'batch': data.get('batch', ''),
                    'valuation': data.get('valuation', 0),
                    'extraordinary_score': data.get('extraordinary_score', 0)
                })
                
                ids.append(f"company_{i}")
            
            # Process edges (relationships) with confidence scores
            for i, edge in enumerate(graph_data.get('edges', [])):
                edge_data = edge.get('data', {})
                source = edge.get('source', '')
                target = edge.get('target', '')
                confidence_score = edge_data.get('confidence_score', 1)
                
                # Create text representation
                relationship_text = f"{source} connected to {target}. Confidence score: {confidence_score}. Business relationship between companies."
                documents.append(relationship_text)
                
                metadatas.append({
                    'type': 'relationship',
                    'source': source,
                    'target': target,
                    'confidence_score': confidence_score,
                    'relationship_type': edge_data.get('type', 'unknown'),
                    'weight': edge.get('weight', 1)
                })
                
                ids.append(f"edge_{i}")
            
            # Generate embeddings
            logger.info(f"Generating embeddings for {len(documents)} documents...")
            embeddings = model.encode(documents).tolist()
            
            # Add to collection
            collection.add(
                documents=documents,
                metadatas=metadatas,
                embeddings=embeddings,
                ids=ids
            )
            
            logger.info(f"✅ Successfully rebuilt {db_path} with {len(documents)} documents")
            
            # Test query
            test_results = collection.query(
                query_texts=["AI companies"],
                n_results=2
            )
            logger.info(f"Test query returned {len(test_results['documents'][0])} results")
            
            success_count += 1
            
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
    success = rebuild_with_chromadb()
    sys.exit(0 if success else 1)
