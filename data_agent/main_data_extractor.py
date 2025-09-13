"""
Main Data Extraction Orchestrator
This script coordinates the entire data extraction pipeline for YC companies and M&A information.
"""

import asyncio
import json
import csv
from datetime import datetime
from typing import List, Dict, Any
import os

from yc_scraper import YCCompaniesScraper
from multi_source_agent import MultiSourceDataAgent

class DataExtractionOrchestrator:
    def __init__(self, newsapi_key: str = None):
        """
        Initialize the main data extraction orchestrator.
        
        Args:
            newsapi_key: Optional NewsAPI key for enhanced news search
        """
        self.yc_scraper = YCCompaniesScraper()
        self.data_agent = MultiSourceDataAgent(newsapi_key=newsapi_key)
        self.output_dir = "data_agent/output"
        
        # Create output directory
        os.makedirs(self.output_dir, exist_ok=True)
        
        print("🎯 Data Extraction Orchestrator initialized")
        print("📁 Output directory:", self.output_dir)
    
    async def run_complete_extraction(self) -> Dict[str, Any]:
        """
        Run the complete data extraction pipeline.
        
        Returns:
            Dictionary containing all extracted data and metadata
        """
        print("\n" + "="*60)
        print("🚀 STARTING COMPLETE DATA EXTRACTION PIPELINE")
        print("="*60)
        
        start_time = datetime.now()
        
        # Step 1: Extract YC Companies
        print("\n📋 STEP 1: Extracting Top 100 YC Companies")
        print("-" * 40)
        yc_companies = self.yc_scraper.get_top_100_yc_companies()
        company_names = [company['name'] for company in yc_companies]
        
        # Save YC companies data
        yc_output_file = f"{self.output_dir}/yc_companies.json"
        with open(yc_output_file, 'w') as f:
            json.dump(yc_companies, f, indent=2, default=str)
        print(f"💾 YC companies saved to: {yc_output_file}")
        
        # Step 2: Collect M&A Data from Multiple Sources
        print("\n📰 STEP 2: Collecting M&A Data from Multiple Sources")
        print("-" * 40)
        news_items = await self.data_agent.collect_all_sources(company_names, days_back=90)
        
        # Step 3: Format Data for Graph Visualization
        print("\n📊 STEP 3: Formatting Data for Graph Visualization")
        print("-" * 40)
        formatted_deals = self.data_agent.format_for_graph(news_items)
        
        # Step 4: Create Company Nodes for Graph
        print("\n🏢 STEP 4: Creating Company Nodes for Graph")
        print("-" * 40)
        company_nodes = self._create_company_nodes(yc_companies, formatted_deals)
        
        # Step 5: Generate Final Graph Data Structure
        print("\n🔗 STEP 5: Generating Final Graph Data Structure")
        print("-" * 40)
        graph_data = self._create_graph_data_structure(company_nodes, formatted_deals)
        
        # Step 6: Save All Output Files
        print("\n💾 STEP 6: Saving Output Files")
        print("-" * 40)
        output_files = self._save_output_files(yc_companies, news_items, formatted_deals, graph_data)
        
        # Step 7: Generate Summary Report
        print("\n📈 STEP 7: Generating Summary Report")
        print("-" * 40)
        summary = self._generate_summary_report(yc_companies, news_items, formatted_deals, start_time)
        
        print("\n" + "="*60)
        print("✅ DATA EXTRACTION PIPELINE COMPLETED SUCCESSFULLY!")
        print("="*60)
        
        return {
            'yc_companies': yc_companies,
            'news_items': [item.__dict__ for item in news_items],
            'formatted_deals': formatted_deals,
            'graph_data': graph_data,
            'output_files': output_files,
            'summary': summary
        }
    
    def _create_company_nodes(self, yc_companies: List[Dict], deals: List[Dict]) -> List[Dict]:
        """
        Create company nodes for graph visualization.
        """
        print("🏗️  Creating company nodes with deal activity metrics...")
        
        # Count deal activity for each company
        deal_counts = {}
        for deal in deals:
            source = deal.get('source_company', '')
            target = deal.get('target_company', '')
            deal_counts[source] = deal_counts.get(source, 0) + 1
            deal_counts[target] = deal_counts.get(target, 0) + 1
        
        company_nodes = []
        for company in yc_companies:
            name = company['name']
            deal_activity = deal_counts.get(name, 0)
            
            # Calculate node size based on valuation and deal activity
            base_size = 20
            if company.get('valuation'):
                size_multiplier = min(3, (company['valuation'] / 1e9) ** 0.3)
                base_size = int(base_size * size_multiplier)
            
            # Add deal activity bonus
            base_size += deal_activity * 5
            
            # Determine color based on industry
            industry_colors = {
                'AI': '#8b5cf6',
                'Fintech': '#10b981',
                'Healthcare': '#f59e0b',
                'DevTools': '#3b82f6',
                'E-commerce': '#ec4899',
                'Social Media': '#ef4444',
                'Technology': '#6366f1'
            }
            
            color = industry_colors.get(company.get('industry', ''), '#64748b')
            
            node = {
                'id': name.lower().replace(' ', '_'),
                'label': name,
                'size': max(20, min(80, base_size)),
                'color': color,
                'data': {
                    'name': name,
                    'industry': company.get('industry', 'Unknown'),
                    'batch': company.get('batch', 'Unknown'),
                    'status': company.get('status', 'Unknown'),
                    'valuation': company.get('valuation'),
                    'deal_activity_count': deal_activity,
                    'extraordinary_score': company.get('valuation', 0) / 1e9 if company.get('valuation') else 0
                }
            }
            company_nodes.append(node)
        
        print(f"✅ Created {len(company_nodes)} company nodes")
        return company_nodes
    
    def _create_graph_data_structure(self, company_nodes: List[Dict], deals: List[Dict]) -> Dict:
        """
        Create the final graph data structure for visualization.
        """
        print("🔗 Creating graph edges from deals...")
        
        # Create edges from deals
        edges = []
        node_ids = {node['data']['name']: node['id'] for node in company_nodes}
        
        for deal in deals:
            source_name = deal.get('source_company', '')
            target_name = deal.get('target_company', '')
            
            source_id = node_ids.get(source_name)
            target_id = node_ids.get(target_name)
            
            if source_id and target_id and source_id != target_id:
                # Determine edge color based on deal type
                deal_colors = {
                    'acquisition': '#ef4444',
                    'merger': '#8b5cf6',
                    'investment': '#3b82f6',
                    'partnership': '#10b981',
                    'ipo': '#f59e0b'
                }
                
                color = deal_colors.get(deal.get('deal_type', ''), '#64748b')
                
                # Calculate edge weight based on deal value
                weight = 2
                if deal.get('deal_value'):
                    weight = max(1, min(10, (deal['deal_value'] / 1e9) * 3))
                
                edge = {
                    'id': deal['id'],
                    'source': source_id,
                    'target': target_id,
                    'label': f"{deal.get('deal_type', 'deal')} ({deal.get('deal_date', '')[:4]})",
                    'weight': weight,
                    'color': color,
                    'data': deal
                }
                edges.append(edge)
        
        # Create metadata
        metadata = {
            'total_companies': len(company_nodes),
            'total_deals': len(edges),
            'industries': list(set([node['data']['industry'] for node in company_nodes])),
            'deal_types': list(set([edge['data'].get('deal_type') for edge in edges if edge['data'].get('deal_type')])),
            'date_range': {
                'start': min([deal.get('deal_date', '') for deal in deals if deal.get('deal_date')], default=''),
                'end': max([deal.get('deal_date', '') for deal in deals if deal.get('deal_date')], default='')
            },
            'total_deal_value': sum([deal.get('deal_value', 0) for deal in deals if deal.get('deal_value')]),
            'extraction_timestamp': datetime.now().isoformat()
        }
        
        graph_data = {
            'nodes': company_nodes,
            'edges': edges,
            'metadata': metadata
        }
        
        print(f"✅ Created graph with {len(company_nodes)} nodes and {len(edges)} edges")
        return graph_data
    
    def _save_output_files(self, yc_companies: List[Dict], news_items: List, 
                          deals: List[Dict], graph_data: Dict) -> Dict[str, str]:
        """
        Save all output files in various formats.
        """
        output_files = {}
        
        # 1. YC Companies (JSON and CSV)
        yc_json_file = f"{self.output_dir}/yc_companies.json"
        with open(yc_json_file, 'w') as f:
            json.dump(yc_companies, f, indent=2, default=str)
        output_files['yc_companies_json'] = yc_json_file
        
        yc_csv_file = f"{self.output_dir}/yc_companies.csv"
        with open(yc_csv_file, 'w', newline='') as f:
            if yc_companies:
                writer = csv.DictWriter(f, fieldnames=yc_companies[0].keys())
                writer.writeheader()
                writer.writerows(yc_companies)
        output_files['yc_companies_csv'] = yc_csv_file
        
        # 2. Raw News Items (JSON)
        news_json_file = f"{self.output_dir}/raw_news_items.json"
        with open(news_json_file, 'w') as f:
            json.dump([item.__dict__ for item in news_items], f, indent=2, default=str)
        output_files['news_items_json'] = news_json_file
        
        # 3. Formatted Deals (JSON and CSV)
        deals_json_file = f"{self.output_dir}/formatted_deals.json"
        with open(deals_json_file, 'w') as f:
            json.dump(deals, f, indent=2, default=str)
        output_files['deals_json'] = deals_json_file
        
        deals_csv_file = f"{self.output_dir}/formatted_deals.csv"
        with open(deals_csv_file, 'w', newline='') as f:
            if deals:
                writer = csv.DictWriter(f, fieldnames=deals[0].keys())
                writer.writeheader()
                writer.writerows(deals)
        output_files['deals_csv'] = deals_csv_file
        
        # 4. Complete Graph Data (JSON)
        graph_json_file = f"{self.output_dir}/complete_graph_data.json"
        with open(graph_json_file, 'w') as f:
            json.dump(graph_data, f, indent=2, default=str)
        output_files['graph_data_json'] = graph_json_file
        
        # 5. Graph Data for Frontend (simplified format)
        frontend_data = {
            'nodes': graph_data['nodes'],
            'edges': graph_data['edges'],
            'metadata': graph_data['metadata']
        }
        frontend_json_file = f"{self.output_dir}/graph_data_for_frontend.json"
        with open(frontend_json_file, 'w') as f:
            json.dump(frontend_data, f, indent=2, default=str)
        output_files['frontend_graph_json'] = frontend_json_file
        
        print(f"💾 Saved {len(output_files)} output files:")
        for file_type, file_path in output_files.items():
            print(f"   📄 {file_type}: {file_path}")
        
        return output_files
    
    def _generate_summary_report(self, yc_companies: List[Dict], news_items: List, 
                               deals: List[Dict], start_time: datetime) -> Dict:
        """
        Generate a comprehensive summary report.
        """
        end_time = datetime.now()
        duration = end_time - start_time
        
        # Calculate statistics
        total_valuation = sum([c.get('valuation', 0) for c in yc_companies if c.get('valuation')])
        deal_values = [d.get('deal_value', 0) for d in deals if d.get('deal_value')]
        total_deal_value = sum(deal_values)
        
        # Industry breakdown
        industry_counts = {}
        for company in yc_companies:
            industry = company.get('industry', 'Unknown')
            industry_counts[industry] = industry_counts.get(industry, 0) + 1
        
        # Deal type breakdown
        deal_type_counts = {}
        for deal in deals:
            deal_type = deal.get('deal_type', 'Unknown')
            deal_type_counts[deal_type] = deal_type_counts.get(deal_type, 0) + 1
        
        # Source breakdown
        source_counts = {}
        for item in news_items:
            source = item.source
            source_counts[source] = source_counts.get(source, 0) + 1
        
        summary = {
            'extraction_metadata': {
                'start_time': start_time.isoformat(),
                'end_time': end_time.isoformat(),
                'duration_seconds': duration.total_seconds(),
                'extraction_date': datetime.now().strftime('%Y-%m-%d')
            },
            'yc_companies_stats': {
                'total_companies': len(yc_companies),
                'total_valuation': total_valuation,
                'average_valuation': total_valuation / len([c for c in yc_companies if c.get('valuation')]) if any(c.get('valuation') for c in yc_companies) else 0,
                'industry_breakdown': industry_counts,
                'top_5_by_valuation': sorted(yc_companies, key=lambda x: x.get('valuation', 0), reverse=True)[:5]
            },
            'news_collection_stats': {
                'total_news_items': len(news_items),
                'source_breakdown': source_counts,
                'unique_companies_mentioned': len(set([company for item in news_items for company in item.companies_mentioned]))
            },
            'deals_stats': {
                'total_deals_found': len(deals),
                'total_deal_value': total_deal_value,
                'average_deal_value': sum(deal_values) / len(deal_values) if deal_values else 0,
                'deal_type_breakdown': deal_type_counts,
                'largest_deals': sorted(deals, key=lambda x: x.get('deal_value', 0), reverse=True)[:5]
            }
        }
        
        # Save summary report
        summary_file = f"{self.output_dir}/extraction_summary.json"
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2, default=str)
        
        # Print summary to console
        print("\n📈 EXTRACTION SUMMARY REPORT")
        print("=" * 40)
        print(f"⏱️  Duration: {duration.total_seconds():.1f} seconds")
        print(f"🏢 YC Companies: {len(yc_companies)}")
        print(f"📰 News Items: {len(news_items)}")
        print(f"🤝 Deals Found: {len(deals)}")
        print(f"💰 Total Deal Value: ${total_deal_value/1e9:.1f}B")
        print(f"🏭 Industries: {len(industry_counts)}")
        print(f"📊 Deal Types: {len(deal_type_counts)}")
        print(f"📡 Sources Used: {len(source_counts)}")
        
        return summary

async def main():
    """
    Main execution function
    """
    print("🎯 Starting YC Companies M&A Data Extraction")
    print("=" * 50)
    
    # Initialize orchestrator (add your NewsAPI key if available)
    newsapi_key = os.getenv('NEWSAPI_KEY')  # Set this environment variable if you have a key
    orchestrator = DataExtractionOrchestrator(newsapi_key=newsapi_key)
    
    # Run complete extraction
    results = await orchestrator.run_complete_extraction()
    
    print(f"\n🎉 All done! Check the output directory: {orchestrator.output_dir}")
    print("📁 Files created:")
    for file_type, file_path in results['output_files'].items():
        print(f"   • {file_path}")

if __name__ == "__main__":
    asyncio.run(main())
