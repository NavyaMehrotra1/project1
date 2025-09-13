export interface Company {
  id: string
  name: string
  industry: string
  market_cap?: number
  founded_year?: number
  headquarters?: string
  description?: string
  website?: string
  ticker_symbol?: string
  employee_count?: number
  revenue?: number
  is_public: boolean
  extraordinary_score?: number
}

export interface Deal {
  id: string
  source_company_id: string
  target_company_id: string
  deal_type: 'merger' | 'acquisition' | 'partnership' | 'investment' | 'ipo' | 'joint_venture'
  deal_value?: number
  deal_date: string
  description: string
  status: string
  confidence_score?: number
  is_predicted: boolean
}

export interface GraphNode {
  id: string
  label: string
  size: number
  color: string
  x?: number
  y?: number
  data: Record<string, any>
}

export interface GraphEdge {
  id: string
  source: string
  target: string
  label: string
  weight: number
  color: string
  data: Record<string, any>
}

export interface GraphData {
  nodes: GraphNode[]
  edges: GraphEdge[]
  metadata: Record<string, any>
}

export interface PredictionRequest {
  companies: string[]
  context?: string
  time_horizon: number
}

export interface WhatIfRequest {
  scenario: string
  companies_involved: string[]
  deal_type?: string
}

export interface EducationRequest {
  query: string
  expertise_level: 'beginner' | 'intermediate' | 'expert'
  context?: string
}

export interface SimulationResult {
  scenario: string
  impact_analysis: string
  affected_companies: string[]
  market_implications: string
  confidence_score: number
  timeline: string
}

export interface CompanyProfile {
  company: Company
  connections: Deal[]
  predictions?: Deal[]
  financial_metrics: Record<string, any>
  news_sentiment: number
  extraordinary_factors: string[]
}
