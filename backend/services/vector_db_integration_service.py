"""
Vector Database Integration Service
Automatically updates vector database when new MA events are discovered
"""

import asyncio
import logging
from typing import List, Any, Optional
from datetime import datetime
from pathlib import Path

from services.vector_database_service import VectorDatabaseService, load_vector_db
from models.ma_events import MAEvent

logger = logging.getLogger(__name__)

class VectorDBIntegrationService:
    def __init__(self, vector_db_path: str = "./chroma_db"):
        self.vector_db_path = vector_db_path
        self.vector_db: Optional[VectorDatabaseService] = None
        self.last_processed_event_time = None
        
    def initialize_vector_db(self) -> bool:
        """Initialize or load the vector database"""
        try:
            # Try to load existing database
            self.vector_db = load_vector_db(self.vector_db_path)
            
            if self.vector_db is None:
                logger.error("Failed to load vector database. Run initialize_vector_db.py first.")
                return False
            
            logger.info("Vector database integration service initialized")
            return True
            
        except Exception as e:
            logger.error(f"Error initializing vector database: {e}")
            return False
    
    async def process_new_ma_events(self, new_events: List[MAEvent]) -> bool:
        """Process and add new MA events to vector database"""
        if not self.vector_db:
            if not self.initialize_vector_db():
                return False
        
        if not new_events:
            logger.debug("No new MA events to process")
            return True
        
        try:
            # Filter events that haven't been processed yet
            events_to_process = []
            
            for event in new_events:
                # Check if this event is newer than our last processed time
                if (self.last_processed_event_time is None or 
                    event.discovered_at > self.last_processed_event_time):
                    events_to_process.append(event)
            
            if not events_to_process:
                logger.debug("No new events to add to vector database")
                return True
            
            # Add events to vector database
            success = self.vector_db.add_ma_events_to_database(events_to_process)
            
            if success:
                # Update last processed time
                self.last_processed_event_time = max(
                    event.discovered_at for event in events_to_process
                )
                
                logger.info(f"Successfully added {len(events_to_process)} new MA events to vector database")
                
                # Log event details
                for event in events_to_process:
                    event_type = event.event_type.value if hasattr(event.event_type, 'value') else str(event.event_type)
                    primary_company = event.primary_company.name if event.primary_company else 'Unknown'
                    secondary_company = event.secondary_company.name if event.secondary_company else None
                    
                    if secondary_company:
                        logger.info(f"  📊 Added: {event_type} - {primary_company} ↔ {secondary_company}")
                    else:
                        logger.info(f"  📊 Added: {event_type} - {primary_company}")
                
                return True
            else:
                logger.error("Failed to add MA events to vector database")
                return False
                
        except Exception as e:
            logger.error(f"Error processing new MA events: {e}")
            return False
    
    async def sync_with_ma_data(self, ma_data_file: str = None) -> bool:
        """Sync vector database with existing MA events data"""
        if not self.vector_db:
            if not self.initialize_vector_db():
                return False
        
        try:
            # Default path to MA events data
            if ma_data_file is None:
                ma_data_file = Path(__file__).parent.parent / "data" / "ma_events.json"
            
            if not Path(ma_data_file).exists():
                logger.warning(f"MA events file not found: {ma_data_file}")
                return True
            
            # Load existing MA events
            import json
            with open(ma_data_file, 'r') as f:
                events_data = json.load(f)
            
            # Convert to MAEvent objects
            ma_events = [MAEvent(**event_data) for event_data in events_data]
            
            # Process all events
            success = await self.process_new_ma_events(ma_events)
            
            if success:
                logger.info(f"Successfully synced {len(ma_events)} MA events with vector database")
            
            return success
            
        except Exception as e:
            logger.error(f"Error syncing with MA data: {e}")
            return False
    
    def get_vector_db_stats(self) -> dict:
        """Get vector database statistics"""
        if not self.vector_db:
            return {"error": "Vector database not initialized"}
        
        return self.vector_db.get_database_stats()
    
    async def search_ma_events(self, query: str, k: int = 5) -> List[dict]:
        """Search MA events in vector database"""
        if not self.vector_db:
            if not self.initialize_vector_db():
                return []
        
        return self.vector_db.search_ma_events(query, k=k)
    
    async def get_recent_ma_events(self, hours: int = 24, k: int = 10) -> List[dict]:
        """Get recent MA events from vector database"""
        if not self.vector_db:
            if not self.initialize_vector_db():
                return []
        
        return self.vector_db.get_recent_ma_events(hours=hours, k=k)

# Global instance for easy access
_vector_db_integration = None

def get_vector_db_integration() -> VectorDBIntegrationService:
    """Get global vector database integration service instance"""
    global _vector_db_integration
    
    if _vector_db_integration is None:
        _vector_db_integration = VectorDBIntegrationService()
    
    return _vector_db_integration

async def auto_update_vector_db_with_ma_events(new_events: List[MAEvent]) -> bool:
    """Convenience function to automatically update vector DB with new MA events"""
    integration_service = get_vector_db_integration()
    return await integration_service.process_new_ma_events(new_events)
