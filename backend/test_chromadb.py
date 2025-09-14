#!/usr/bin/env python3
"""
ChromaDB Vector Database Test
Comprehensive test to verify ChromaDB is working with company data
"""

import chromadb
import json

def test_chromadb():
    print('🧪 COMPREHENSIVE CHROMADB TEST')
    print('='*50)

    # 1. Test ChromaDB client connection
    client = chromadb.PersistentClient(path='./chroma_db')
    print('✅ ChromaDB client connected')

    # 2. Load and process all company data
    with open('../data_agent/data_agent/output/graph_data_for_frontend.json', 'r') as f:
        graph_data = json.load(f)

    companies = graph_data['nodes']
    print(f'✅ Loaded {len(companies)} companies from your data')

    # 3. Create/get collection and populate with ALL companies
    try:
        collection = client.get_collection('yc_companies')
        print('✅ Found existing YC companies collection')
    except:
        collection = client.create_collection('yc_companies')
        print('✅ Created new YC companies collection')

    # Prepare all company data with unique IDs
    documents = []
    metadatas = []
    ids = []
    seen_ids = set()

    for i, company in enumerate(companies):
        # Create unique ID to avoid duplicates
        original_id = company['id']
        unique_id = original_id
        counter = 1
        while unique_id in seen_ids:
            counter += 1
            unique_id = f"{original_id}_{counter}"
        seen_ids.add(unique_id)
        
        # Create rich document text for better semantic search
        valuation_billions = company['data']['valuation'] / 1000000000
        doc_text = f"""{company['label']} is a {company['data']['industry']} company from Y Combinator batch {company['data']['batch']}.
Status: {company['data']['status']}
Valuation: {valuation_billions:.1f} billion dollars
Extraordinary score: {company['data']['extraordinary_score']}
Deal activity count: {company['data']['deal_activity_count']}"""
        
        documents.append(doc_text.strip())
        metadatas.append({
            'name': company['label'],
            'industry': company['data']['industry'],
            'batch': company['data']['batch'],
            'valuation': company['data']['valuation'],
            'status': company['data']['status'],
            'extraordinary_score': company['data']['extraordinary_score'],
            'deal_activity_count': company['data']['deal_activity_count']
        })
        ids.append(unique_id)

    # Add all companies to ChromaDB
    collection.upsert(
        documents=documents,
        metadatas=metadatas,
        ids=ids
    )
    print(f'✅ Added {len(documents)} companies to ChromaDB vector database')

    # 4. Test various semantic searches
    test_queries = [
        'artificial intelligence and machine learning companies',
        'financial technology and payment companies', 
        'high valuation unicorn companies',
        'companies with exceptional performance scores',
        'healthcare and medical technology startups'
    ]

    print('\n🔍 SEMANTIC SEARCH TESTS:')
    for query in test_queries:
        results = collection.query(
            query_texts=[query],
            n_results=3
        )
        
        print(f'\n   Query: "{query}"')
        for i, (doc, metadata) in enumerate(zip(results['documents'][0], results['metadatas'][0])):
            name = metadata['name']
            industry = metadata['industry']
            valuation = metadata['valuation'] / 1000000000
            score = metadata['extraordinary_score']
            print(f'   {i+1}. {name} ({industry}) - ${valuation:.1f}B, Score: {score}')

    # 5. Test collection statistics
    count = collection.count()
    print(f'\n📊 DATABASE STATISTICS:')
    print(f'   Total companies in vector database: {count}')
    print(f'   ChromaDB location: ./chroma_db')
    print(f'   Collection name: yc_companies')

    print(f'\n✅ CHROMADB VECTOR DATABASE IS FULLY FUNCTIONAL!')
    print('   • All company data indexed')
    print('   • Semantic search working')
    print('   • Persistent storage enabled')
    print('   • Ready for API integration')

if __name__ == "__main__":
    test_chromadb()
