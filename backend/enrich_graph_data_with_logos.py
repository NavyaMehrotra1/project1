#!/usr/bin/env python3
"""
Script to enrich graph_data_for_frontend.json with logo URLs using LogoService
"""

import json
import asyncio
import sys
import os
from pathlib import Path

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.logo_service import LogoService

async def enrich_graph_data_with_logos():
    """Enrich the graph data JSON file with logo URLs"""
    
    # Paths
    graph_data_path = Path(__file__).parent.parent / "data_agent" / "data_agent" / "output" / "graph_data_for_frontend.json"
    backup_path = graph_data_path.with_suffix('.json.backup')
    
    print(f"Reading graph data from: {graph_data_path}")
    
    # Read the existing graph data
    try:
        with open(graph_data_path, 'r', encoding='utf-8') as f:
            graph_data = json.load(f)
    except FileNotFoundError:
        print(f"Error: Graph data file not found at {graph_data_path}")
        return False
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in graph data file: {e}")
        return False
    
    # Create backup
    print(f"Creating backup at: {backup_path}")
    with open(backup_path, 'w', encoding='utf-8') as f:
        json.dump(graph_data, f, indent=2)
    
    # Initialize logo service
    logo_service = LogoService()
    
    nodes = graph_data.get('nodes', [])
    total_nodes = len(nodes)
    
    print(f"Processing {total_nodes} nodes...")
    
    # Process nodes in batches to avoid overwhelming the APIs
    batch_size = 10
    successful_logos = 0
    
    for i in range(0, total_nodes, batch_size):
        batch = nodes[i:i + batch_size]
        batch_tasks = []
        
        print(f"Processing batch {i//batch_size + 1}/{(total_nodes + batch_size - 1)//batch_size}")
        
        for node in batch:
            company_name = node.get('data', {}).get('name') or node.get('label', '')
            if company_name:
                batch_tasks.append(logo_service.get_company_logo(company_name))
            else:
                batch_tasks.append(asyncio.create_task(asyncio.sleep(0)))  # Placeholder
        
        # Execute batch
        try:
            logo_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
            
            for j, (node, logo_url) in enumerate(zip(batch, logo_results)):
                company_name = node.get('data', {}).get('name') or node.get('label', '')
                
                if isinstance(logo_url, Exception):
                    print(f"  ❌ Error fetching logo for {company_name}: {logo_url}")
                    logo_url = None
                elif logo_url:
                    print(f"  ✅ Found logo for {company_name}")
                    successful_logos += 1
                else:
                    print(f"  ⚠️  No logo found for {company_name}")
                
                # Add logo_url to node data
                if 'data' not in node:
                    node['data'] = {}
                node['data']['logo_url'] = logo_url
                
        except Exception as e:
            print(f"  ❌ Batch error: {e}")
            # Add None logo_url for failed batch
            for node in batch:
                if 'data' not in node:
                    node['data'] = {}
                node['data']['logo_url'] = None
        
        # Small delay between batches to be respectful to APIs
        await asyncio.sleep(1)
    
    # Write the enriched data back to the file
    print(f"\nWriting enriched data back to: {graph_data_path}")
    try:
        with open(graph_data_path, 'w', encoding='utf-8') as f:
            json.dump(graph_data, f, indent=2)
        
        print(f"✅ Successfully enriched graph data!")
        print(f"📊 Statistics:")
        print(f"   - Total nodes processed: {total_nodes}")
        print(f"   - Logos found: {successful_logos}")
        print(f"   - Success rate: {(successful_logos/total_nodes)*100:.1f}%")
        print(f"   - Backup saved to: {backup_path}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error writing enriched data: {e}")
        print(f"💾 Original data is backed up at: {backup_path}")
        return False

if __name__ == "__main__":
    print("🚀 Starting logo enrichment for graph data...")
    success = asyncio.run(enrich_graph_data_with_logos())
    
    if success:
        print("\n🎉 Logo enrichment completed successfully!")
    else:
        print("\n💥 Logo enrichment failed!")
        sys.exit(1)
