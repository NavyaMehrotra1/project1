import axios from 'axios'
import { GraphData, PredictionRequest, WhatIfRequest, EducationRequest, SimulationResult, CompanyProfile } from '@/types'

const API_BASE_URL = process.env.NODE_ENV === 'production' 
  ? 'https://your-backend-url.com' 
  : 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
})

export const apiService = {
  // Graph data
  async getGraphData(): Promise<GraphData> {
    const response = await api.get('/api/graph-data')
    return response.data
  },

  // Companies
  async getCompanies() {
    const response = await api.get('/api/companies')
    return response.data.companies
  },

  async getCompanyProfile(companyId: string): Promise<CompanyProfile> {
    const response = await api.get(`/api/company/${companyId}`)
    return response.data
  },

  // Deals
  async getDeals() {
    const response = await api.get('/api/deals')
    return response.data.deals
  },

  // Predictions
  async predictDeals(request: PredictionRequest) {
    const response = await api.post('/api/predict-deals', request)
    return response.data.predictions
  },

  // What-if simulations
  async simulateScenario(request: WhatIfRequest): Promise<SimulationResult> {
    const response = await api.post('/api/what-if', request)
    return response.data
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
