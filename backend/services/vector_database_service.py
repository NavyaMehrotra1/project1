"""
Vector Database Service using LangChain and ChromaDB
Creates embeddings from graph_data_for_frontend.json for semantic search
"""

import json
import os
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

try:
    from langchain_openai import OpenAIEmbeddings
    from langchain_chroma import Chroma
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    from langchain_core.documents import Document as LangChainDocument
    LANGCHAIN_AVAILABLE = True
except ImportError:
    try:
        # Fallback to older imports
        from langchain.embeddings import OpenAIEmbeddings
        from langchain.vectorstores import Chroma
        from langchain.text_splitter import RecursiveCharacterTextSplitter
        from langchain.schema import Document as LangChainDocument
        LANGCHAIN_AVAILABLE = True
    except ImportError:
        try:
            # Try community embeddings
            from langchain_community.embeddings import HuggingFaceEmbeddings
            from langchain_community.vectorstores import Chroma
            from langchain_text_splitters import RecursiveCharacterTextSplitter
            from langchain_core.documents import Document as LangChainDocument
            LANGCHAIN_AVAILABLE = True
        except ImportError:
            LANGCHAIN_AVAILABLE = False
            LangChainDocument = None
            print("LangChain not available. Install with: pip install langchain chromadb openai")

logger = logging.getLogger(__name__)

class VectorDatabaseService:
    def __init__(self, persist_directory: str = "./chroma_db"):
        self.persist_directory = persist_directory
        self.vectorstore = None
        self.embeddings = None
        
        if LANGCHAIN_AVAILABLE:
            self._initialize_embeddings()
        else:
            logger.warning("LangChain not available. Vector database functionality disabled.")
    
    def _initialize_embeddings(self):
        """Initialize OpenAI embeddings or fallback to sentence transformers"""
        try:
            # Try OpenAI embeddings first
            if os.getenv("OPENAI_API_KEY"):
                self.embeddings = OpenAIEmbeddings()
                logger.info("Using OpenAI embeddings")
            else:
                # Fallback to sentence transformers
                try:
                    from langchain_community.embeddings import HuggingFaceEmbeddings
                    self.embeddings = HuggingFaceEmbeddings(
                        model_name="sentence-transformers/all-MiniLM-L6-v2"
                    )
                    logger.info("Using HuggingFace sentence transformers embeddings")
                except ImportError:
                    try:
                        from langchain.embeddings import HuggingFaceEmbeddings
                        self.embeddings = HuggingFaceEmbeddings(
                            model_name="sentence-transformers/all-MiniLM-L6-v2"
                        )
                        logger.info("Using HuggingFace sentence transformers embeddings")
                    except ImportError:
                        logger.error("No embedding model available. Install openai or sentence-transformers")
                        return
        except Exception as e:
            logger.error(f"Error initializing embeddings: {e}")
    
    def load_graph_data(self, json_path: str) -> Dict[str, Any]:
        """Load graph data from JSON file"""
        try:
            with open(json_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading graph data: {e}")
            return {}
    
    def create_company_documents(self, graph_data: Dict[str, Any]) -> List[Any]:
        """Convert company nodes to LangChain documents"""
        documents = []
        
        for node in graph_data.get('nodes', []):
            data = node.get('data', {})
            
            # Create comprehensive text representation of company
            company_text = self._format_company_text(node, data)
            
            # Create document with metadata
            if LANGCHAIN_AVAILABLE:
                doc = LangChainDocument(
                    page_content=company_text,
                    metadata={
                        'company_id': node.get('id'),
                        'company_name': data.get('name'),
                        'industry': data.get('industry'),
                        'batch': data.get('batch'),
                        'status': data.get('status'),
                        'valuation': data.get('valuation', 0),
                        'extraordinary_score': data.get('extraordinary_score', 0),
                        'deal_activity_count': data.get('deal_activity_count', 0),
                        'type': 'company'
                    }
                )
            else:
                doc = None
            if doc is not None:
                documents.append(doc)
        
        return documents
    
    def create_relationship_documents(self, graph_data: Dict[str, Any]) -> List[Any]:
        """Convert edges/relationships to LangChain documents"""
        documents = []
        
        for edge in graph_data.get('edges', []):
            # Create text representation of relationship
            relationship_text = self._format_relationship_text(edge)
            
            if LANGCHAIN_AVAILABLE:
                doc = LangChainDocument(
                    page_content=relationship_text,
                    metadata={
                        'source': edge.get('source'),
                        'target': edge.get('target'),
                        'relationship_type': edge.get('data', {}).get('type', 'unknown'),
                        'weight': edge.get('weight', 1),
                        'type': 'relationship'
                    }
                )
            else:
                doc = None
            if doc is not None:
                documents.append(doc)
        
        return documents
    
    def _format_company_text(self, node: Dict, data: Dict) -> str:
        """Format company data as searchable text"""
        parts = []
        
        # Basic info
        name = data.get('name', node.get('label', ''))
        parts.append(f"Company: {name}")
        
        if data.get('industry'):
            parts.append(f"Industry: {data['industry']}")
        
        if data.get('batch'):
            parts.append(f"Y Combinator Batch: {data['batch']}")
        
        if data.get('status'):
            parts.append(f"Status: {data['status']}")
        
        # Financial info
        if data.get('valuation'):
            valuation_b = data['valuation'] / 1_000_000_000
            parts.append(f"Valuation: ${valuation_b:.1f}B")
        
        # Extraordinary score
        if data.get('extraordinary_score'):
            score = data['extraordinary_score']
            parts.append(f"Extraordinary Score: {score}/100")
            
            # Add qualitative description based on score
            if score >= 80:
                parts.append("Classification: Exceptional company with outstanding achievements")
            elif score >= 60:
                parts.append("Classification: High-performing company with notable success")
            elif score >= 40:
                parts.append("Classification: Solid company with good performance")
            else:
                parts.append("Classification: Emerging company with potential")
        
        # Deal activity
        if data.get('deal_activity_count'):
            parts.append(f"Deal Activity: {data['deal_activity_count']} transactions")
        
        # Additional searchable terms based on industry
        industry_keywords = self._get_industry_keywords(data.get('industry', ''))
        if industry_keywords:
            parts.append(f"Related terms: {', '.join(industry_keywords)}")
        
        return ". ".join(parts) + "."
    
    def _format_relationship_text(self, edge: Dict) -> str:
        """Format relationship data as searchable text"""
        source = edge.get('source', '')
        target = edge.get('target', '')
        rel_type = edge.get('data', {}).get('type', 'connected to')
        
        return f"{source} {rel_type} {target}. This represents a business relationship or connection between these companies."
    
    def _get_industry_keywords(self, industry: str) -> List[str]:
        """Get additional searchable keywords for industries"""
        keyword_map = {
            'AI': ['artificial intelligence', 'machine learning', 'deep learning', 'neural networks', 'automation'],
            'Fintech': ['financial technology', 'payments', 'banking', 'cryptocurrency', 'blockchain'],
            'Travel': ['tourism', 'hospitality', 'booking', 'accommodation', 'transportation'],
            'E-commerce': ['online retail', 'marketplace', 'shopping', 'commerce', 'retail'],
            'SaaS': ['software as a service', 'cloud software', 'enterprise software', 'business tools'],
            'Healthcare': ['medical technology', 'health tech', 'telemedicine', 'biotech', 'pharmaceuticals'],
            'Education': ['edtech', 'learning', 'online education', 'training', 'academic'],
            'Social': ['social media', 'networking', 'community', 'communication', 'messaging']
        }
        return keyword_map.get(industry, [])
    
    def build_vector_database(self, json_path: str) -> bool:
        """Build vector database from graph JSON file"""
        if not LANGCHAIN_AVAILABLE or not self.embeddings:
            logger.error("Cannot build vector database: LangChain or embeddings not available")
            return False
        
        try:
            # Load graph data
            graph_data = self.load_graph_data(json_path)
            if not graph_data:
                logger.error("No graph data loaded")
                return False
            
            # Create documents
            company_docs = self.create_company_documents(graph_data)
            relationship_docs = self.create_relationship_documents(graph_data)
            
            all_documents = company_docs + relationship_docs
            
            if not all_documents:
                logger.error("No documents created")
                return False
            
            # Create vector store
            self.vectorstore = Chroma.from_documents(
                documents=all_documents,
                embedding=self.embeddings,
                persist_directory=self.persist_directory
            )
            
            # Note: ChromaDB now auto-persists, no need to call persist()
            
            logger.info(f"Vector database created with {len(all_documents)} documents")
            logger.info(f"Companies: {len(company_docs)}, Relationships: {len(relationship_docs)}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error building vector database: {e}")
            return False
    
    def load_existing_database(self) -> bool:
        """Load existing vector database"""
        if not LANGCHAIN_AVAILABLE or not self.embeddings:
            return False
        
        try:
            if os.path.exists(self.persist_directory):
                self.vectorstore = Chroma(
                    persist_directory=self.persist_directory,
                    embedding_function=self.embeddings
                )
                logger.info("Loaded existing vector database")
                return True
            else:
                logger.info("No existing database found")
                return False
        except Exception as e:
            logger.error(f"Error loading existing database: {e}")
            return False
    
    def semantic_search(self, query: str, k: int = 5, filter_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Perform semantic search on the vector database"""
        if not self.vectorstore:
            logger.error("Vector database not initialized")
            return []
        
        try:
            # Create filter if specified
            filter_dict = None
            if filter_type:
                filter_dict = {"type": filter_type}
            
            # Perform similarity search
            docs = self.vectorstore.similarity_search(
                query, 
                k=k,
                filter=filter_dict
            )
            
            # Format results
            results = []
            for doc in docs:
                result = {
                    'content': doc.page_content,
                    'metadata': doc.metadata,
                    'score': getattr(doc, 'score', None)
                }
                results.append(result)
            
            return results
            
        except Exception as e:
            logger.error(f"Error in semantic search: {e}")
            return []
    
    def search_companies(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """Search specifically for companies"""
        return self.semantic_search(query, k=k, filter_type='company')
    
    def search_relationships(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """Search specifically for relationships"""
        return self.semantic_search(query, k=k, filter_type='relationship')
    
    def get_similar_companies(self, company_name: str, k: int = 5) -> List[Dict[str, Any]]:
        """Find companies similar to a given company"""
        query = f"companies similar to {company_name}"
        results = self.search_companies(query, k=k+1)  # +1 to account for the company itself
        
        # Filter out the exact match if present
        filtered_results = [
            r for r in results 
            if r['metadata'].get('company_name', '').lower() != company_name.lower()
        ]
        
        return filtered_results[:k]
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector database"""
        if not self.vectorstore:
            return {"error": "Database not initialized"}
        
        try:
            # Get collection info
            collection = self.vectorstore._collection
            count = collection.count()
            
            return {
                "total_documents": count,
                "persist_directory": self.persist_directory,
                "embedding_model": type(self.embeddings).__name__ if self.embeddings else "None",
                "created_at": datetime.now().isoformat()
            }
        except Exception as e:
            return {"error": str(e)}

# Utility functions for easy usage
def create_vector_db_from_graph(json_path: str, persist_dir: str = "./chroma_db") -> VectorDatabaseService:
    """Convenience function to create vector database from graph JSON"""
    service = VectorDatabaseService(persist_directory=persist_dir)
    
    if service.build_vector_database(json_path):
        return service
    else:
        return None

def load_vector_db(persist_dir: str = "./chroma_db") -> VectorDatabaseService:
    """Convenience function to load existing vector database"""
    service = VectorDatabaseService(persist_directory=persist_dir)
    
    if service.load_existing_database():
        return service
    else:
        return None
