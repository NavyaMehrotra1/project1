#!/usr/bin/env python3
"""
Simple Vector Database Real-time Demo
Demonstrates adding new data to ChromaDB and querying it
"""

import chromadb
import json
import time
from datetime import datetime
import uuid
import random

def load_company_data():
    """Load company data from the graph JSON file"""
    try:
        with open('/Users/sutharsikakumar/project1-1/data_agent/data_agent/output/graph_data_for_frontend.json', 'r') as f:
            data = json.load(f)
        return data.get('nodes', [])[:10]  # Use first 10 companies for demo
    except Exception as e:
        print(f"Error loading company data: {e}")
        return []

def simulate_real_time_updates():
    """Simulate real-time company updates"""
    updates = [
        {"type": "funding", "content": "raised $50M Series B funding round"},
        {"type": "partnership", "content": "announced strategic partnership with major tech company"},
        {"type": "product", "content": "launched new AI-powered feature for enterprise customers"},
        {"type": "expansion", "content": "expanded operations to 3 new international markets"},
        {"type": "acquisition", "content": "acquired smaller competitor to strengthen market position"},
        {"type": "news", "content": "featured in major tech publication for innovation"},
    ]
    return random.choice(updates)

def main():
    print("🚀 Real-time Vector Database Demo")
    print("="*60)
    
    # Initialize ChromaDB
    client = chromadb.PersistentClient(path="./chroma_db_demo")
    
    # Get or create collections
    try:
        companies_collection = client.get_collection("companies")
        print(f"✅ Found existing companies collection with {companies_collection.count()} items")
    except:
        companies_collection = client.create_collection("companies")
        print("📝 Created new companies collection")
    
    try:
        updates_collection = client.get_collection("company_updates")
        print(f"✅ Found existing updates collection with {updates_collection.count()} items")
    except:
        updates_collection = client.create_collection("company_updates")
        print("📝 Created new updates collection")
    
    # Load and add company data if collection is empty
    if companies_collection.count() == 0:
        print("\n📊 Loading initial company data...")
        companies = load_company_data()
        
        if companies:
            for company in companies:
                company_id = str(uuid.uuid4())
                company_name = company.get('id', 'Unknown')
                description = company.get('description', f"{company_name} company")
                
                companies_collection.add(
                    documents=[description],
                    metadatas=[{
                        'name': company_name,
                        'type': 'company',
                        'added_at': datetime.now().isoformat()
                    }],
                    ids=[company_id]
                )
            
            print(f"✅ Added {len(companies)} companies to vector database")
        else:
            # Add some sample companies if file not found
            sample_companies = [
                {"name": "TechCorp", "description": "AI-powered software solutions for enterprises"},
                {"name": "DataFlow", "description": "Real-time data processing and analytics platform"},
                {"name": "CloudSync", "description": "Cloud infrastructure and synchronization services"}
            ]
            
            for company in sample_companies:
                company_id = str(uuid.uuid4())
                companies_collection.add(
                    documents=[company['description']],
                    metadatas=[{
                        'name': company['name'],
                        'type': 'company',
                        'added_at': datetime.now().isoformat()
                    }],
                    ids=[company_id]
                )
            
            print(f"✅ Added {len(sample_companies)} sample companies to vector database")
    
    print(f"\n📈 Current Database Stats:")
    print(f"   Companies: {companies_collection.count()}")
    print(f"   Updates: {updates_collection.count()}")
    
    # Demonstrate real-time updates
    print(f"\n🔴 LIVE: Simulating real-time company updates...")
    print("Press Ctrl+C to stop\n")
    
    try:
        update_count = 0
        while update_count < 5:  # Demo with 5 updates
            # Get a random company
            all_companies = companies_collection.get()
            if all_companies['metadatas']:
                company_metadata = random.choice(all_companies['metadatas'])
                company_name = company_metadata.get('name', 'Unknown Company')
                
                # Generate update
                update = simulate_real_time_updates()
                timestamp = datetime.now()
                
                # Add to updates collection
                update_id = str(uuid.uuid4())
                update_content = f"{company_name} {update['content']}"
                
                updates_collection.add(
                    documents=[update_content],
                    metadatas=[{
                        'company': company_name,
                        'type': update['type'],
                        'timestamp': timestamp.isoformat(),
                        'source': 'demo_simulation'
                    }],
                    ids=[update_id]
                )
                
                # Display the update
                print(f"[{timestamp.strftime('%H:%M:%S')}] 📰 NEW UPDATE ADDED")
                print(f"   Company: {company_name}")
                print(f"   Type: {update['type'].upper()}")
                print(f"   Content: {update['content']}")
                print(f"   → Added to ChromaDB updates collection")
                print("-" * 50)
                
                update_count += 1
                time.sleep(2)  # Wait 2 seconds between updates
        
        # Demonstrate semantic search on updates
        print(f"\n🔍 SEMANTIC SEARCH DEMO")
        print("Searching for funding-related updates...")
        
        funding_results = updates_collection.query(
            query_texts=["funding investment money raised"],
            n_results=3
        )
        
        if funding_results['documents'][0]:
            print("Found funding-related updates:")
            for i, (doc, metadata) in enumerate(zip(funding_results['documents'][0], funding_results['metadatas'][0])):
                print(f"   {i+1}. {doc}")
                print(f"      Company: {metadata.get('company', 'Unknown')}")
                print(f"      Type: {metadata.get('type', 'Unknown')}")
                print()
        
        print(f"✅ Demo completed successfully!")
        print(f"Final stats - Companies: {companies_collection.count()}, Updates: {updates_collection.count()}")
        
    except KeyboardInterrupt:
        print(f"\n🛑 Demo stopped by user")
        print(f"Final stats - Companies: {companies_collection.count()}, Updates: {updates_collection.count()}")

if __name__ == "__main__":
    main()
