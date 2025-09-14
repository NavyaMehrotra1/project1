// API Integration Service - Connects to NewsAPI, Exa, Anthropic, and ChromaDB
// Handles data ingestion, LLM processing, and vector database operations

export interface CompanyData {
  id: string
  name: string
  industry: string
  batch: string
  status: string
  valuation: number
  deal_activity_count: number
  extraordinary_score: number
  logo_url?: string
}

export interface DealData {
  id: string
  source: string
  target: string
  deal_type: string
  deal_value: number | null
  deal_date: string
  description: string
  confidence_score: number
}

export interface GraphData {
  nodes: CompanyData[]
  edges: DealData[]
  metadata: {
    total_companies: number
    total_deals: number
    last_updated: string
  }
}

class DataService {
  private baseUrl = '/api'

  // NewsAPI Integration - Real-time news ingestion
  async fetchNewsData(query: string = 'M&A deals'): Promise<any[]> {
    try {
      const response = await fetch(`${this.baseUrl}/news?q=${encodeURIComponent(query)}`)
      if (!response.ok) throw new Error('News API failed')
      return await response.json()
    } catch (error) {
      console.error('NewsAPI integration error:', error)
      return []
    }
  }

  // Exa API Integration - Enhanced search and company intelligence
  async fetchExaData(companyName: string): Promise<any> {
    try {
      const response = await fetch(`${this.baseUrl}/exa/company`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ company: companyName })
      })
      if (!response.ok) throw new Error('Exa API failed')
      return await response.json()
    } catch (error) {
      console.error('Exa API integration error:', error)
      return null
    }
  }

  // Anthropic API Integration - LLM processing for predictions and analysis
  async processWithLLM(prompt: string, context: any): Promise<string> {
    try {
      const response = await fetch(`${this.baseUrl}/llm/process`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt, context })
      })
      if (!response.ok) throw new Error('Anthropic API failed')
      const data = await response.json()
      return data.response
    } catch (error) {
      console.error('Anthropic API integration error:', error)
      return 'Error processing request'
    }
  }

  // ChromaDB Integration - Vector database for embeddings and similarity search
  async storeInVectorDB(data: any[], collection: string): Promise<boolean> {
    try {
      const response = await fetch(`${this.baseUrl}/chromadb/store`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ data, collection })
      })
      return response.ok
    } catch (error) {
      console.error('ChromaDB integration error:', error)
      return false
    }
  }

  async searchVectorDB(query: string, collection: string, limit: number = 10): Promise<any[]> {
    try {
      const response = await fetch(`${this.baseUrl}/chromadb/search`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query, collection, limit })
      })
      if (!response.ok) throw new Error('ChromaDB search failed')
      return await response.json()
    } catch (error) {
      console.error('ChromaDB search error:', error)
      return []
    }
  }

  // Main graph data fetching - integrates data_agent output
  async fetchGraphData(): Promise<GraphData> {
    try {
      // First try to get data from data_agent output
      const response = await fetch('/data/graph_data_for_frontend.json')
      if (response.ok) {
        const data = await response.json()
        return this.transformDataAgentOutput(data)
      }
      
      // Fallback to mock data if data_agent output not available
      return this.getMockGraphData()
    } catch (error) {
      console.error('Graph data fetch error:', error)
      return this.getMockGraphData()
    }
  }

  // Transform data_agent output to frontend format
  private transformDataAgentOutput(data: any): GraphData {
    const nodes = data.nodes?.map((node: any) => ({
      id: node.id,
      name: node.data?.name || node.label,
      industry: node.data?.industry || 'Unknown',
      batch: node.data?.batch || 'N/A',
      status: node.data?.status || 'Private',
      valuation: node.data?.valuation || 0,
      deal_activity_count: node.data?.deal_activity_count || 0,
      extraordinary_score: node.data?.extraordinary_score || 0,
      logo_url: node.data?.logo_url
    })) || []

    const edges = data.edges?.map((edge: any) => ({
      id: edge.id,
      source: edge.source,
      target: edge.target,
      deal_type: edge.data?.deal_type || 'unknown',
      deal_value: edge.data?.deal_value,
      deal_date: edge.data?.deal_date || new Date().toISOString(),
      description: edge.data?.description || '',
      confidence_score: edge.data?.confidence_score || 0.5
    })) || []

    return {
      nodes,
      edges,
      metadata: {
        total_companies: nodes.length,
        total_deals: edges.length,
        last_updated: new Date().toISOString()
      }
    }
  }

  // Prediction Pipeline - Uses LLM + vector similarity for deal predictions
  async generatePredictions(companyId: string): Promise<any[]> {
    try {
      // Get company context from vector DB
      const context = await this.searchVectorDB(companyId, 'companies', 5)
      
      // Generate predictions using LLM
      const prompt = `Based on the company data and recent M&A trends, predict potential deals for ${companyId}. Consider industry patterns, valuation trends, and strategic fit.`
      const prediction = await this.processWithLLM(prompt, context)
      
      return JSON.parse(prediction || '[]')
    } catch (error) {
      console.error('Prediction generation error:', error)
      return []
    }
  }

  // Manual Edge Creation - Allows users to create custom relationships
  async createManualEdge(sourceId: string, targetId: string, edgeData: Partial<DealData>): Promise<boolean> {
    try {
      const response = await fetch(`${this.baseUrl}/graph/edge`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          source: sourceId,
          target: targetId,
          ...edgeData,
          manual: true,
          created_at: new Date().toISOString()
        })
      })
      return response.ok
    } catch (error) {
      console.error('Manual edge creation error:', error)
      return false
    }
  }

  // Impact Propagation - Simulates effects of deals across the graph
  async simulateImpact(sourceId: string, targetId: string, dealType: string): Promise<any> {
    try {
      const response = await fetch(`${this.baseUrl}/graph/simulate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ source: sourceId, target: targetId, deal_type: dealType })
      })
      if (!response.ok) throw new Error('Impact simulation failed')
      return await response.json()
    } catch (error) {
      console.error('Impact simulation error:', error)
      return { positive_effects: [], negative_effects: [], explanation: 'Simulation unavailable' }
    }
  }

  // Teaching Tool - Natural language query processing
  async askTeachingAssistant(question: string, context?: any): Promise<string> {
    try {
      const prompt = `You are an M&A intelligence teaching assistant. Answer this question about deals, companies, or market trends: ${question}`
      return await this.processWithLLM(prompt, context)
    } catch (error) {
      console.error('Teaching assistant error:', error)
      return 'I apologize, but I cannot process your question right now. Please try again later.'
    }
  }

  // Mock data for development/fallback
  private getMockGraphData(): GraphData {
    return {
      nodes: [
        {
          id: "openai",
          name: "OpenAI",
          industry: "AI/ML",
          batch: "N/A",
          status: "Private",
          valuation: 80000000000,
          deal_activity_count: 15,
          extraordinary_score: 95
        },
        {
          id: "stripe",
          name: "Stripe",
          industry: "Fintech",
          batch: "S09",
          status: "Private",
          valuation: 95000000000,
          deal_activity_count: 12,
          extraordinary_score: 92
        },
        {
          id: "anthropic",
          name: "Anthropic",
          industry: "AI/ML",
          batch: "N/A",
          status: "Private",
          valuation: 15000000000,
          deal_activity_count: 8,
          extraordinary_score: 88
        }
      ],
      edges: [
        {
          id: "edge1",
          source: "openai",
          target: "stripe",
          deal_type: "partnership",
          deal_value: 1000000000,
          deal_date: "2024-01-15",
          description: "Strategic AI integration partnership",
          confidence_score: 0.85
        },
        {
          id: "edge2",
          source: "anthropic",
          target: "openai",
          deal_type: "competition",
          deal_value: null,
          deal_date: "2024-02-01",
          description: "AI model competition and talent acquisition",
          confidence_score: 0.92
        }
      ],
      metadata: {
        total_companies: 3,
        total_deals: 2,
        last_updated: new Date().toISOString()
      }
    }
  }
}

export const dataService = new DataService()
export default dataService
