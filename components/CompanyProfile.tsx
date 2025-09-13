'use client'

import { useState, useEffect } from 'react'
import { X, Building, MapPin, Calendar, DollarSign, TrendingUp, Star, ExternalLink } from 'lucide-react'
import { apiService } from '@/services/api'
import { CompanyProfile as CompanyProfileType } from '@/types'
import toast from 'react-hot-toast'

interface CompanyProfileProps {
  companyId: string
  onClose: () => void
}

export function CompanyProfile({ companyId, onClose }: CompanyProfileProps) {
  const [profile, setProfile] = useState<CompanyProfileType | null>(null)
  const [loading, setLoading] = useState(true)
  const [activeTab, setActiveTab] = useState<'overview' | 'deals' | 'predictions'>('overview')

  useEffect(() => {
    loadCompanyProfile()
  }, [companyId])

  const loadCompanyProfile = async () => {
    try {
      setLoading(true)
      const data = await apiService.getCompanyProfile(companyId)
      setProfile(data)
    } catch (error) {
      console.error('Error loading company profile:', error)
      toast.error('Failed to load company profile')
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="fixed right-0 top-0 h-full w-96 bg-white shadow-lg z-50 p-6">
        <div className="flex items-center justify-center h-full">
          <div className="spinner"></div>
        </div>
      </div>
    )
  }

  if (!profile) {
    return (
      <div className="fixed right-0 top-0 h-full w-96 bg-white shadow-lg z-50 p-6">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-bold">Company Not Found</h2>
          <button onClick={onClose} className="p-2 hover:bg-gray-100 rounded-lg">
            <X size={20} />
          </button>
        </div>
        <p className="text-gray-600">Unable to load company profile.</p>
      </div>
    )
  }

  const { company, connections, financial_metrics, news_sentiment, extraordinary_factors } = profile

  const formatCurrency = (value: number | undefined) => {
    if (!value) return 'N/A'
    if (value >= 1e9) return `$${(value / 1e9).toFixed(1)}B`
    if (value >= 1e6) return `$${(value / 1e6).toFixed(1)}M`
    return `$${value.toLocaleString()}`
  }

  const tabs = [
    { id: 'overview', label: 'Overview' },
    { id: 'deals', label: `Deals (${connections.length})` },
    { id: 'predictions', label: 'Predictions' }
  ]

  return (
    <div className="fixed right-0 top-0 h-full w-96 bg-white shadow-lg z-50 overflow-y-auto">
      {/* Header */}
      <div className="sticky top-0 bg-white border-b border-gray-200 p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-bold">{company.name}</h2>
          <button onClick={onClose} className="p-2 hover:bg-gray-100 rounded-lg">
            <X size={20} />
          </button>
        </div>

        {/* Tabs */}
        <div className="flex space-x-1 bg-gray-100 rounded-lg p-1">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`flex-1 py-2 px-3 text-sm font-medium rounded-md transition-colors ${
                activeTab === tab.id
                  ? 'bg-white text-blue-600 shadow-sm'
                  : 'text-gray-600 hover:text-gray-800'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      {/* Content */}
      <div className="p-6">
        {activeTab === 'overview' && (
          <div className="space-y-6">
            {/* Basic Info */}
            <div>
              <div className="flex items-center gap-2 mb-3">
                <Building size={18} className="text-gray-600" />
                <h3 className="font-semibold">Company Details</h3>
              </div>
              
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-600">Industry:</span>
                  <span className="font-medium">{company.industry}</span>
                </div>
                
                {company.headquarters && (
                  <div className="flex justify-between">
                    <span className="text-gray-600">Headquarters:</span>
                    <span className="font-medium">{company.headquarters}</span>
                  </div>
                )}
                
                {company.founded_year && (
                  <div className="flex justify-between">
                    <span className="text-gray-600">Founded:</span>
                    <span className="font-medium">{company.founded_year}</span>
                  </div>
                )}
                
                <div className="flex justify-between">
                  <span className="text-gray-600">Type:</span>
                  <span className="font-medium">{company.is_public ? 'Public' : 'Private'}</span>
                </div>
                
                {company.ticker_symbol && (
                  <div className="flex justify-between">
                    <span className="text-gray-600">Ticker:</span>
                    <span className="font-medium">{company.ticker_symbol}</span>
                  </div>
                )}
              </div>
            </div>

            {/* Financial Metrics */}
            <div>
              <div className="flex items-center gap-2 mb-3">
                <DollarSign size={18} className="text-gray-600" />
                <h3 className="font-semibold">Financial Overview</h3>
              </div>
              
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-600">Market Cap:</span>
                  <span className="font-medium">{formatCurrency(company.market_cap)}</span>
                </div>
                
                <div className="flex justify-between">
                  <span className="text-gray-600">Revenue:</span>
                  <span className="font-medium">{formatCurrency(company.revenue)}</span>
                </div>
                
                {financial_metrics.profit_margin && (
                  <div className="flex justify-between">
                    <span className="text-gray-600">Profit Margin:</span>
                    <span className="font-medium">{(financial_metrics.profit_margin * 100).toFixed(1)}%</span>
                  </div>
                )}
                
                {financial_metrics.revenue_growth && (
                  <div className="flex justify-between">
                    <span className="text-gray-600">Revenue Growth:</span>
                    <span className="font-medium text-green-600">+{(financial_metrics.revenue_growth * 100).toFixed(1)}%</span>
                  </div>
                )}
              </div>
            </div>

            {/* Sentiment & Score */}
            <div>
              <div className="flex items-center gap-2 mb-3">
                <TrendingUp size={18} className="text-gray-600" />
                <h3 className="font-semibold">Market Sentiment</h3>
              </div>
              
              <div className="space-y-3">
                <div>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="text-gray-600">News Sentiment</span>
                    <span className="font-medium">{(news_sentiment * 100).toFixed(0)}%</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div 
                      className="bg-green-500 h-2 rounded-full transition-all duration-500"
                      style={{ width: `${news_sentiment * 100}%` }}
                    />
                  </div>
                </div>
                
                {company.extraordinary_score && (
                  <div>
                    <div className="flex justify-between text-sm mb-1">
                      <span className="text-gray-600">Extraordinary Score</span>
                      <span className="font-medium">{(company.extraordinary_score * 100).toFixed(0)}%</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div 
                        className="bg-purple-500 h-2 rounded-full transition-all duration-500"
                        style={{ width: `${company.extraordinary_score * 100}%` }}
                      />
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* Extraordinary Factors */}
            {extraordinary_factors.length > 0 && (
              <div>
                <div className="flex items-center gap-2 mb-3">
                  <Star size={18} className="text-yellow-500" />
                  <h3 className="font-semibold">Extraordinary Factors</h3>
                </div>
                
                <div className="space-y-2">
                  {extraordinary_factors.map((factor, index) => (
                    <div key={index} className="flex items-center gap-2 text-sm">
                      <div className="w-2 h-2 bg-yellow-500 rounded-full"></div>
                      <span>{factor}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Description */}
            {company.description && (
              <div>
                <h3 className="font-semibold mb-2">Description</h3>
                <p className="text-sm text-gray-600">{company.description}</p>
              </div>
            )}

            {/* Website Link */}
            {company.website && (
              <div>
                <a
                  href={company.website}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center gap-2 text-blue-600 hover:text-blue-800 text-sm"
                >
                  <ExternalLink size={16} />
                  Visit Website
                </a>
              </div>
            )}
          </div>
        )}

        {activeTab === 'deals' && (
          <div className="space-y-4">
            {connections.length > 0 ? (
              connections.map((deal) => (
                <div key={deal.id} className="border border-gray-200 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-2">
                    <span className={`px-2 py-1 text-xs rounded-full ${
                      deal.deal_type === 'acquisition' ? 'bg-red-100 text-red-800' :
                      deal.deal_type === 'merger' ? 'bg-purple-100 text-purple-800' :
                      deal.deal_type === 'partnership' ? 'bg-green-100 text-green-800' :
                      deal.deal_type === 'investment' ? 'bg-blue-100 text-blue-800' :
                      'bg-gray-100 text-gray-800'
                    }`}>
                      {deal.deal_type}
                    </span>
                    <span className="text-xs text-gray-500">
                      {new Date(deal.deal_date).toLocaleDateString()}
                    </span>
                  </div>
                  
                  <h4 className="font-medium mb-1">{deal.description}</h4>
                  
                  {deal.deal_value && (
                    <p className="text-sm text-gray-600 mb-1">
                      Value: {formatCurrency(deal.deal_value)}
                    </p>
                  )}
                  
                  <div className="flex items-center justify-between text-xs">
                    <span className={`px-2 py-1 rounded ${
                      deal.status === 'completed' ? 'bg-green-100 text-green-800' :
                      deal.status === 'pending' ? 'bg-yellow-100 text-yellow-800' :
                      'bg-gray-100 text-gray-800'
                    }`}>
                      {deal.status}
                    </span>
                    
                    {deal.confidence_score && (
                      <span className="text-gray-500">
                        Confidence: {(deal.confidence_score * 100).toFixed(0)}%
                      </span>
                    )}
                  </div>
                </div>
              ))
            ) : (
              <div className="text-center text-gray-500 py-8">
                <Building size={48} className="mx-auto mb-4 text-gray-300" />
                <p>No deals found for this company</p>
              </div>
            )}
          </div>
        )}

        {activeTab === 'predictions' && (
          <div className="space-y-4">
            <div className="text-center text-gray-500 py-8">
              <TrendingUp size={48} className="mx-auto mb-4 text-gray-300" />
              <p>AI predictions will appear here</p>
              <p className="text-sm">Use the prediction panel to generate forecasts</p>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
