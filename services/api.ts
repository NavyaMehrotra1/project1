import axios from 'axios'
import { GraphData, PredictionRequest, WhatIfRequest, EducationRequest, SimulationResult, CompanyProfile } from '@/types'
import { generateMockGraphData, getMockCompanyProfile, getMockSimulationResult, mockCompanies } from './mockData'

const API_BASE_URL = process.env.NODE_ENV === 'production' 
  ? 'https://your-backend-url.com' 
  : 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
})

// Development mode flag
const USE_MOCK_DATA = false; // Now using real backend

export const apiService = {
  // Graph data
  async getGraphData(): Promise<GraphData> {
    if (USE_MOCK_DATA) {
      // Simulate network delay
      await new Promise(resolve => setTimeout(resolve, 500))
      return generateMockGraphData(false)
    }
    
    try {
      const response = await api.get('/api/graph-data')
      return response.data
    } catch (error) {
      console.warn('Backend unavailable, using mock data')
      return generateMockGraphData(false)
    }
  },

  // Companies
  async getCompanies() {
    if (USE_MOCK_DATA) {
      await new Promise(resolve => setTimeout(resolve, 300))
      return mockCompanies
    }
    
    try {
      const response = await api.get('/api/companies')
      return response.data.companies
    } catch (error) {
      console.warn('Backend unavailable, using mock companies')
      return mockCompanies
    }
  },

  async getCompanyProfile(companyId: string): Promise<CompanyProfile> {
    if (USE_MOCK_DATA) {
      await new Promise(resolve => setTimeout(resolve, 400))
      return getMockCompanyProfile(companyId)
    }
    
    try {
      const response = await api.get(`/api/company/${companyId}`)
      return response.data
    } catch (error) {
      console.warn('Backend unavailable, using mock company profile')
      return getMockCompanyProfile(companyId)
    }
  },

  // Deals
  async getDeals() {
    if (USE_MOCK_DATA) {
      await new Promise(resolve => setTimeout(resolve, 300))
      return generateMockGraphData(false).edges.map(edge => edge.data)
    }
    
    try {
      const response = await api.get('/api/deals')
      return response.data.deals
    } catch (error) {
      console.warn('Backend unavailable, using mock deals')
      return generateMockGraphData(false).edges.map(edge => edge.data)
    }
  },

  // Predictions
  async predictDeals(request: PredictionRequest) {
    if (USE_MOCK_DATA) {
      await new Promise(resolve => setTimeout(resolve, 1000))
      return generateMockGraphData(true).edges
        .filter(edge => edge.data?.is_predicted)
        .map(edge => edge.data)
    }
    
    try {
      const response = await api.post('/api/predict-deals', request)
      return response.data.predictions
    } catch (error) {
      console.warn('Backend unavailable, using mock predictions')
      return generateMockGraphData(true).edges
        .filter(edge => edge.data?.is_predicted)
        .map(edge => edge.data)
    }
  },

  // What-if simulations
  async simulateScenario(request: WhatIfRequest): Promise<SimulationResult> {
    if (USE_MOCK_DATA) {
      await new Promise(resolve => setTimeout(resolve, 1500))
      return getMockSimulationResult(request.scenario)
    }
    
    try {
      const response = await api.post('/api/what-if', request)
      return response.data
    } catch (error) {
      console.warn('Backend unavailable, using mock simulation')
      return getMockSimulationResult(request.scenario)
    }
  },

  // Education
  async getEducationResponse(request: EducationRequest): Promise<string> {
    const response = await api.post('/api/education', request)
    return response.data.explanation
  },

  // Data ingestion
  async ingestNews(query: string = 'merger acquisition', daysBack: number = 30) {
    const response = await api.post(`/api/ingest-news?query=${encodeURIComponent(query)}&days_back=${daysBack}`)
    return response.data
  },

  // Graph operations
  async addCompanyNode(company: any) {
    const response = await api.post('/api/graph/add-node', company)
    return response.data
  },

  async removeCompanyNode(companyId: string) {
    const response = await api.delete(`/api/graph/remove-node/${companyId}`)
    return response.data
  },

  async addDealEdge(deal: any) {
    const response = await api.post('/api/graph/add-edge', deal)
    return response.data
  },

  async removeDealEdge(dealId: string) {
    const response = await api.delete(`/api/graph/remove-edge/${dealId}`)
    return response.data
  },

  // Health check
  async healthCheck() {
    const response = await api.get('/health')
    return response.data
  }
}

// Error handling interceptor
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error.response?.data || error.message)
    throw error
  }
)
