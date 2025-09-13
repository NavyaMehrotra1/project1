import { GraphData, Company, Deal, CompanyProfile, SimulationResult } from '@/types'

// Mock companies data
export const mockCompanies: Company[] = [
  {
    id: 'apple',
    name: 'Apple Inc.',
    industry: 'Technology',
    market_cap: 3000000000000,
    founded_year: 1976,
    headquarters: 'Cupertino, CA',
    description: 'Technology company specializing in consumer electronics',
    website: 'https://apple.com',
    ticker_symbol: 'AAPL',
    employee_count: 164000,
    revenue: 394328000000,
    is_public: true,
    extraordinary_score: 0.95
  },
  {
    id: 'microsoft',
    name: 'Microsoft Corporation',
    industry: 'Technology',
    market_cap: 2800000000000,
    founded_year: 1975,
    headquarters: 'Redmond, WA',
    description: 'Software and cloud computing company',
    website: 'https://microsoft.com',
    ticker_symbol: 'MSFT',
    employee_count: 221000,
    revenue: 211915000000,
    is_public: true,
    extraordinary_score: 0.92
  },
  {
    id: 'google',
    name: 'Alphabet Inc.',
    industry: 'Technology',
    market_cap: 1700000000000,
    founded_year: 1998,
    headquarters: 'Mountain View, CA',
    description: 'Internet services and technology company',
    website: 'https://abc.xyz',
    ticker_symbol: 'GOOGL',
    employee_count: 190000,
    revenue: 307394000000,
    is_public: true,
    extraordinary_score: 0.90
  },
  {
    id: 'tesla',
    name: 'Tesla Inc.',
    industry: 'Automotive',
    market_cap: 800000000000,
    founded_year: 2003,
    headquarters: 'Austin, TX',
    description: 'Electric vehicle and clean energy company',
    website: 'https://tesla.com',
    ticker_symbol: 'TSLA',
    employee_count: 140000,
    revenue: 96773000000,
    is_public: true,
    extraordinary_score: 0.88
  },
  {
    id: 'meta',
    name: 'Meta Platforms Inc.',
    industry: 'Technology',
    market_cap: 750000000000,
    founded_year: 2004,
    headquarters: 'Menlo Park, CA',
    description: 'Social media and virtual reality company',
    website: 'https://meta.com',
    ticker_symbol: 'META',
    employee_count: 77805,
    revenue: 134902000000,
    is_public: true,
    extraordinary_score: 0.85
  },
  {
    id: 'nvidia',
    name: 'NVIDIA Corporation',
    industry: 'Technology',
    market_cap: 1100000000000,
    founded_year: 1993,
    headquarters: 'Santa Clara, CA',
    description: 'Graphics processing and AI computing company',
    website: 'https://nvidia.com',
    ticker_symbol: 'NVDA',
    employee_count: 29600,
    revenue: 79774000000,
    is_public: true,
    extraordinary_score: 0.93
  },
  {
    id: 'amazon',
    name: 'Amazon.com Inc.',
    industry: 'E-commerce',
    market_cap: 1500000000000,
    founded_year: 1994,
    headquarters: 'Seattle, WA',
    description: 'E-commerce and cloud computing company',
    website: 'https://amazon.com',
    ticker_symbol: 'AMZN',
    employee_count: 1541000,
    revenue: 574785000000,
    is_public: true,
    extraordinary_score: 0.91
  },
  {
    id: 'openai',
    name: 'OpenAI',
    industry: 'Technology',
    founded_year: 2015,
    headquarters: 'San Francisco, CA',
    description: 'Artificial intelligence research and deployment company',
    website: 'https://openai.com',
    employee_count: 1500,
    is_public: false,
    extraordinary_score: 0.96
  }
]

// Mock deals data
export const mockDeals: Deal[] = [
  {
    id: 'deal_1',
    source_company_id: 'microsoft',
    target_company_id: 'openai',
    deal_type: 'investment',
    deal_value: 10000000000,
    deal_date: '2023-01-23',
    description: 'Microsoft invests $10B in OpenAI for AI partnership',
    status: 'completed',
    confidence_score: 0.95,
    is_predicted: false
  },
  {
    id: 'deal_2',
    source_company_id: 'google',
    target_company_id: 'nvidia',
    deal_type: 'partnership',
    deal_value: 5000000000,
    deal_date: '2023-06-15',
    description: 'Google partners with NVIDIA for AI cloud infrastructure',
    status: 'completed',
    confidence_score: 0.88,
    is_predicted: false
  },
  {
    id: 'deal_3',
    source_company_id: 'apple',
    target_company_id: 'tesla',
    deal_type: 'partnership',
    deal_value: 2000000000,
    deal_date: '2023-09-10',
    description: 'Apple and Tesla collaborate on autonomous vehicle technology',
    status: 'completed',
    confidence_score: 0.82,
    is_predicted: false
  },
  {
    id: 'deal_4',
    source_company_id: 'meta',
    target_company_id: 'nvidia',
    deal_type: 'investment',
    deal_value: 3000000000,
    deal_date: '2023-11-20',
    description: 'Meta invests in NVIDIA for metaverse computing power',
    status: 'completed',
    confidence_score: 0.90,
    is_predicted: false
  },
  {
    id: 'deal_5',
    source_company_id: 'amazon',
    target_company_id: 'openai',
    deal_type: 'partnership',
    deal_value: 1500000000,
    deal_date: '2024-02-14',
    description: 'Amazon partners with OpenAI for AWS AI services',
    status: 'completed',
    confidence_score: 0.87,
    is_predicted: false
  },
  // Predicted deals
  {
    id: 'pred_1',
    source_company_id: 'apple',
    target_company_id: 'openai',
    deal_type: 'acquisition',
    deal_value: 50000000000,
    deal_date: '2024-12-01',
    description: 'Predicted: Apple may acquire OpenAI for AI integration',
    status: 'predicted',
    confidence_score: 0.75,
    is_predicted: true
  },
  {
    id: 'pred_2',
    source_company_id: 'google',
    target_company_id: 'tesla',
    deal_type: 'partnership',
    deal_value: 8000000000,
    deal_date: '2024-08-15',
    description: 'Predicted: Google and Tesla may partner on autonomous driving',
    status: 'predicted',
    confidence_score: 0.68,
    is_predicted: true
  },
  {
    id: 'pred_3',
    source_company_id: 'microsoft',
    target_company_id: 'nvidia',
    deal_type: 'merger',
    deal_value: 200000000000,
    deal_date: '2025-06-30',
    description: 'Predicted: Microsoft may merge with NVIDIA for AI dominance',
    status: 'predicted',
    confidence_score: 0.62,
    is_predicted: true
  }
]

// Generate mock graph data
export const generateMockGraphData = (includePredictions: boolean = false): GraphData => {
  const nodes = mockCompanies.map(company => ({
    id: company.id,
    label: company.name,
    size: 40,
    color: getSectorColor(company.industry),
    data: company
  }))

  const edges = mockDeals
    .filter(deal => includePredictions || !deal.is_predicted)
    .map(deal => ({
      id: deal.id,
      source: deal.source_company_id,
      target: deal.target_company_id,
      label: deal.deal_type,
      weight: deal.deal_value ? Math.log10(deal.deal_value) / 2 : 1,
      color: getDealTypeColor(deal.deal_type, deal.is_predicted),
      data: deal
    }))

  return {
    nodes,
    edges,
    metadata: {
      total_companies: nodes.length,
      total_deals: edges.length,
      last_updated: new Date().toISOString(),
      prediction_count: mockDeals.filter(d => d.is_predicted).length
    }
  }
}

// Helper functions
const getSectorColor = (industry: string): string => {
  const colors: Record<string, string> = {
    'Technology': '#3B82F6',
    'Healthcare': '#10B981',
    'Finance': '#F59E0B',
    'Energy': '#EF4444',
    'Consumer': '#8B5CF6',
    'Industrial': '#6B7280',
    'Real Estate': '#EC4899',
    'Materials': '#84CC16',
    'Utilities': '#06B6D4',
    'Telecommunications': '#F97316',
    'Automotive': '#DC2626',
    'E-commerce': '#7C3AED'
  }
  return colors[industry] || '#64748B'
}

const getDealTypeColor = (dealType: string, isPredicted: boolean): string => {
  if (isPredicted) return '#F59E0B'
  
  const colors: Record<string, string> = {
    'merger': '#EF4444',
    'acquisition': '#EF4444',
    'partnership': '#10B981',
    'joint_venture': '#10B981',
    'investment': '#3B82F6',
    'ipo': '#8B5CF6'
  }
  return colors[dealType] || '#64748B'
}

// Mock company profile data
export const getMockCompanyProfile = (companyId: string): CompanyProfile => {
  const company = mockCompanies.find(c => c.id === companyId)
  if (!company) throw new Error('Company not found')

  const connections = mockDeals.filter(deal => 
    (deal.source_company_id === companyId || deal.target_company_id === companyId) && 
    !deal.is_predicted
  )

  const predictions = mockDeals.filter(deal => 
    (deal.source_company_id === companyId || deal.target_company_id === companyId) && 
    deal.is_predicted
  )

  return {
    company,
    connections,
    predictions,
    financial_metrics: {
      revenue_growth: Math.random() * 0.3 + 0.05,
      profit_margin: Math.random() * 0.25 + 0.1,
      debt_to_equity: Math.random() * 2,
      current_ratio: Math.random() * 3 + 1
    },
    news_sentiment: Math.random() * 0.6 + 0.2,
    extraordinary_factors: [
      'Strong AI capabilities',
      'Market leadership',
      'Innovation pipeline',
      'Strategic partnerships'
    ]
  }
}

// Mock simulation result
export const getMockSimulationResult = (scenario: string): SimulationResult => {
  return {
    scenario,
    impact_analysis: `The ${scenario} would create significant market disruption with ripple effects across the technology sector. Primary impacts include increased market concentration and potential regulatory scrutiny.`,
    affected_companies: ['apple', 'microsoft', 'google', 'nvidia'],
    market_implications: 'This deal could reshape the competitive landscape in AI and cloud computing, potentially triggering defensive moves by competitors.',
    confidence_score: Math.random() * 0.4 + 0.6,
    timeline: '12-18 months for completion, pending regulatory approval'
  }
}
