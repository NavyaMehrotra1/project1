import asyncio
import networkx as nx
from typing import List, Dict, Any, Optional
import math
import random
from models.schemas import Company, Deal, GraphData, GraphNode, GraphEdge
from services.data_ingestion import DataIngestionService

class GraphService:
    def __init__(self):
        self.data_service = DataIngestionService()
        self.graph = nx.Graph()
        
    async def generate_graph_data(self) -> GraphData:
        """Generate graph data for visualization"""
        companies = await self.data_service.get_companies()
        deals = await self.data_service.get_deals()
        
        # Create nodes for companies
        nodes = []
        for company in companies:
            # Calculate node size based on market cap and extraordinary score
            base_size = 20
            if company.market_cap:
                size_multiplier = math.log10(company.market_cap / 1000000000) + 1
                base_size = max(20, min(80, base_size * size_multiplier))
            
            # Adjust size for extraordinary companies
            if company.extraordinary_score and company.extraordinary_score > 0.8:
                base_size *= 1.5
            
            # Color based on industry
            color = self._get_industry_color(company.industry)
            
            node = GraphNode(
                id=company.id,
                label=company.name,
                size=base_size,
                color=color,
                data={
                    "industry": company.industry,
                    "market_cap": company.market_cap,
                    "is_public": company.is_public,
                    "extraordinary_score": company.extraordinary_score,
                    "founded_year": company.founded_year,
                    "headquarters": company.headquarters
                }
            )
            nodes.append(node)
            self.graph.add_node(company.id, **node.dict())
        
        # Create edges for deals
        edges = []
        for deal in deals:
            # Skip if companies don't exist
            if deal.source_company_id not in [c.id for c in companies] or \
               deal.target_company_id not in [c.id for c in companies]:
                continue
            
            # Edge weight based on deal value
            weight = 1
            if deal.deal_value:
                weight = max(1, math.log10(deal.deal_value / 1000000) / 3)
            
            # Color based on deal type and prediction status
            color = self._get_deal_color(deal.deal_type, deal.is_predicted)
            
            edge = GraphEdge(
                id=deal.id,
                source=deal.source_company_id,
                target=deal.target_company_id,
                label=f"{deal.deal_type.value} ({deal.deal_date.year})",
                weight=weight,
                color=color,
                data={
                    "deal_type": deal.deal_type.value,
                    "deal_value": deal.deal_value,
                    "deal_date": deal.deal_date.isoformat(),
                    "description": deal.description,
                    "is_predicted": deal.is_predicted,
                    "confidence_score": deal.confidence_score
                }
            )
            edges.append(edge)
            self.graph.add_edge(deal.source_company_id, deal.target_company_id, **edge.dict())
        
        # Calculate layout positions using spring layout
        if nodes:
            pos = nx.spring_layout(self.graph, k=3, iterations=50)
            for node in nodes:
                if node.id in pos:
                    node.x = pos[node.id][0] * 500 + 400  # Scale and center
                    node.y = pos[node.id][1] * 500 + 300
        
        return GraphData(
            nodes=nodes,
            edges=edges,
            metadata={
                "total_companies": len(nodes),
                "total_deals": len(edges),
                "predicted_deals": len([e for e in edges if e.data.get("is_predicted")]),
                "industries": list(set([n.data.get("industry") for n in nodes if n.data.get("industry")])),
                "deal_types": list(set([e.data.get("deal_type") for e in edges if e.data.get("deal_type")]))
            }
        )
    
    def _get_industry_color(self, industry: str) -> str:
        """Get color based on industry"""
        industry_colors = {
            "Technology": "#3b82f6",
            "Artificial Intelligence": "#8b5cf6",
            "Social Media": "#ef4444",
            "Finance": "#10b981",
            "Healthcare": "#f59e0b",
            "Energy": "#84cc16",
            "Retail": "#ec4899",
            "Manufacturing": "#6b7280",
            "Entertainment": "#f97316"
        }
        return industry_colors.get(industry, "#64748b")
    
    def _get_deal_color(self, deal_type, is_predicted: bool) -> str:
        """Get color based on deal type and prediction status"""
        if is_predicted:
            return "#fbbf24"  # Yellow for predictions
        
        deal_colors = {
            "acquisition": "#ef4444",
            "merger": "#8b5cf6",
            "partnership": "#10b981",
            "investment": "#3b82f6",
            "ipo": "#f59e0b",
            "joint_venture": "#06b6d4"
        }
        return deal_colors.get(deal_type.value if hasattr(deal_type, 'value') else deal_type, "#64748b")
    
    async def add_company_node(self, company: Company) -> Dict[str, Any]:
        """Add a new company node to the graph"""
        self.data_service.add_company(company)
        return {"success": True, "message": f"Added company {company.name}"}
    
    async def remove_company_node(self, company_id: str) -> Dict[str, Any]:
        """Remove a company node from the graph"""
        if company_id in self.data_service.companies_db:
            del self.data_service.companies_db[company_id]
            
            # Remove related deals
            deals_to_remove = [
                deal_id for deal_id, deal in self.data_service.deals_db.items()
                if deal.source_company_id == company_id or deal.target_company_id == company_id
            ]
            for deal_id in deals_to_remove:
                del self.data_service.deals_db[deal_id]
            
            return {"success": True, "message": f"Removed company {company_id} and {len(deals_to_remove)} related deals"}
        
        return {"success": False, "message": "Company not found"}
    
    async def add_deal_edge(self, deal: Deal) -> Dict[str, Any]:
        """Add a new deal edge to the graph"""
        self.data_service.add_deal(deal)
        return {"success": True, "message": f"Added deal {deal.id}"}
    
    async def remove_deal_edge(self, deal_id: str) -> Dict[str, Any]:
        """Remove a deal edge from the graph"""
        if deal_id in self.data_service.deals_db:
            del self.data_service.deals_db[deal_id]
            return {"success": True, "message": f"Removed deal {deal_id}"}
        
        return {"success": False, "message": "Deal not found"}
    
    async def get_company_connections(self, company_id: str) -> Dict[str, Any]:
        """Get all connections for a specific company"""
        if company_id not in self.data_service.companies_db:
            return {"error": "Company not found"}
        
        company = self.data_service.companies_db[company_id]
        deals = await self.data_service.get_deals()
        
        connections = [
            deal for deal in deals
            if deal.source_company_id == company_id or deal.target_company_id == company_id
        ]
        
        return {
            "company": company,
            "connections": connections,
            "connection_count": len(connections)
        }
    
    async def analyze_network_metrics(self) -> Dict[str, Any]:
        """Analyze network metrics and centrality"""
        companies = await self.data_service.get_companies()
        deals = await self.data_service.get_deals()
        
        # Build networkx graph
        G = nx.Graph()
        for company in companies:
            G.add_node(company.id)
        
        for deal in deals:
            if deal.source_company_id in G.nodes and deal.target_company_id in G.nodes:
                G.add_edge(deal.source_company_id, deal.target_company_id)
        
        if len(G.nodes) == 0:
            return {"error": "No companies in network"}
        
        # Calculate centrality metrics
        try:
            degree_centrality = nx.degree_centrality(G)
            betweenness_centrality = nx.betweenness_centrality(G)
            closeness_centrality = nx.closeness_centrality(G)
            
            # Find most connected companies
            most_connected = sorted(degree_centrality.items(), key=lambda x: x[1], reverse=True)[:5]
            
            return {
                "network_size": len(G.nodes),
                "total_connections": len(G.edges),
                "density": nx.density(G),
                "most_connected": most_connected,
                "centrality_metrics": {
                    "degree": degree_centrality,
                    "betweenness": betweenness_centrality,
                    "closeness": closeness_centrality
                }
            }
        except Exception as e:
            return {"error": f"Network analysis failed: {str(e)}"}
