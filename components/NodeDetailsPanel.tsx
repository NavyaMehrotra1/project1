'use client'

import React, { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { X, TrendingUp, TrendingDown, Calendar, DollarSign, Users, Globe, ChevronDown, ChevronUp } from 'lucide-react'
import { GraphData, Deal, Company } from '@/types'
import { apiService } from '@/services/api'

interface NodeDetailsPanelProps {
  nodeId: string | null
  graphData: GraphData | null
  onClose: () => void
  showPredictions: boolean
}

interface NodeDetails {
  company: Company
  connections: Deal[]
  predictions: Deal[]
  metrics: {
    totalConnections: number
    recentDeals: number
    predictedDeals: number
    avgDealValue: number
    sectors: string[]
  }
}

export const NodeDetailsPanel: React.FC<NodeDetailsPanelProps> = ({
  nodeId,
  graphData,
  onClose,
  showPredictions
}) => {
  const [nodeDetails, setNodeDetails] = useState<NodeDetails | null>(null)
  const [loading, setLoading] = useState(false)
  const [activeTab, setActiveTab] = useState<'overview' | 'connections' | 'predictions'>('overview')
  const [expandedSections, setExpandedSections] = useState<Set<string>>(new Set(['overview']))

  useEffect(() => {
    if (nodeId) {
      loadNodeDetails()
    }
  }, [nodeId])

  const loadNodeDetails = async () => {
    if (!nodeId || !graphData) return
    
    setLoading(true)
    try {
      // Get company profile from API
      const profile = await apiService.getCompanyProfile(nodeId)
      
      // Calculate metrics from graph data
      const connections = graphData.edges.filter(
        edge => edge.source === nodeId || edge.target === nodeId
      )
      
      const recentDeals = connections.filter(edge => {
        const dealDate = new Date(edge.data?.deal_date || '1970-01-01')
        const monthsAgo = new Date()
        monthsAgo.setMonth(monthsAgo.getMonth() - 6)
        return dealDate > monthsAgo && !edge.data?.is_predicted
      })

      const predictions = connections.filter(edge => edge.data?.is_predicted)
      
      const dealValues = connections
        .map(edge => edge.data?.deal_value)
        .filter(value => value && value > 0)
      
      const avgDealValue = dealValues.length > 0 
        ? dealValues.reduce((sum, val) => sum + val, 0) / dealValues.length 
        : 0

      const sectors = [...new Set(connections.map(edge => {
        const partnerId = edge.source === nodeId ? edge.target : edge.source
        const partner = graphData.nodes.find(n => n.id === partnerId)
        return partner?.data?.sector || partner?.data?.industry || 'Unknown'
      }))]

      setNodeDetails({
        company: profile.company,
        connections: profile.connections,
        predictions: profile.predictions || [],
        metrics: {
          totalConnections: connections.length,
          recentDeals: recentDeals.length,
          predictedDeals: predictions.length,
          avgDealValue,
          sectors
        }
      })
    } catch (error) {
      console.error('Error loading node details:', error)
    } finally {
      setLoading(false)
    }
  }

  const toggleSection = (section: string) => {
    const newExpanded = new Set(expandedSections)
    if (newExpanded.has(section)) {
      newExpanded.delete(section)
    } else {
      newExpanded.add(section)
    }
    setExpandedSections(newExpanded)
  }

  const formatCurrency = (value: number) => {
    if (value >= 1e9) return `$${(value / 1e9).toFixed(1)}B`
    if (value >= 1e6) return `$${(value / 1e6).toFixed(1)}M`
    if (value >= 1e3) return `$${(value / 1e3).toFixed(1)}K`
    return `$${value.toFixed(0)}`
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    })
  }

  const getDealTypeColor = (dealType: string) => {
    switch (dealType) {
      case 'merger':
      case 'acquisition':
        return 'text-red-400'
      case 'partnership':
      case 'joint_venture':
        return 'text-green-400'
      case 'investment':
        return 'text-blue-400'
      case 'ipo':
        return 'text-purple-400'
      default:
        return 'text-gray-400'
    }
  }

  if (!nodeId) return null

  return (
    <AnimatePresence>
      <motion.div
        initial={{ x: '100%' }}
        animate={{ x: 0 }}
        exit={{ x: '100%' }}
        transition={{ type: 'spring', damping: 25, stiffness: 200 }}
        className="fixed right-0 top-0 h-full w-96 bg-black/40 backdrop-blur-xl text-white shadow-2xl z-50 overflow-hidden border-l border-white/10"
      >
        {/* Modern Header */}
        <div className="flex items-center justify-between p-6 border-b border-white/10">
          <h2 className="text-xl font-bold bg-gradient-to-r from-white to-gray-300 bg-clip-text text-transparent">Company Details</h2>
          <button
            onClick={onClose}
            className="p-2 hover:bg-white/10 rounded-xl transition-all duration-200"
          >
            <X size={20} />
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto">
          {loading ? (
            <div className="flex items-center justify-center h-32">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-white"></div>
            </div>
          ) : nodeDetails ? (
            <div className="p-4 space-y-4">
              {/* Company Overview */}
              <div className="bg-gray-800 rounded-lg p-4">
                <div className="flex items-center gap-3 mb-3">
                  <div className="w-12 h-12 bg-blue-600 rounded-lg flex items-center justify-center">
                    <span className="text-lg font-bold">
                      {nodeDetails.company.name.charAt(0)}
                    </span>
                  </div>
                  <div>
                    <h3 className="font-semibold text-lg">{nodeDetails.company.name}</h3>
                    <p className="text-gray-400 text-sm">{nodeDetails.company.industry}</p>
                  </div>
                </div>

                {/* Key Metrics */}
                <div className="grid grid-cols-2 gap-3 mb-3">
                  <div className="bg-gray-700 rounded p-2">
                    <div className="text-2xl font-bold text-blue-400">
                      {nodeDetails.metrics.totalConnections}
                    </div>
                    <div className="text-xs text-gray-400">Total Connections</div>
                  </div>
                  <div className="bg-gray-700 rounded p-2">
                    <div className="text-2xl font-bold text-green-400">
                      {nodeDetails.metrics.recentDeals}
                    </div>
                    <div className="text-xs text-gray-400">Recent Deals</div>
                  </div>
                </div>

                {/* Company Info */}
                <div className="space-y-2 text-sm">
                  {nodeDetails.company.market_cap && (
                    <div className="flex items-center gap-2">
                      <DollarSign size={14} className="text-gray-400" />
                      <span>Market Cap: {formatCurrency(nodeDetails.company.market_cap)}</span>
                    </div>
                  )}
                  {nodeDetails.company.employee_count && (
                    <div className="flex items-center gap-2">
                      <Users size={14} className="text-gray-400" />
                      <span>Employees: {nodeDetails.company.employee_count.toLocaleString()}</span>
                    </div>
                  )}
                  {nodeDetails.company.founded_year && (
                    <div className="flex items-center gap-2">
                      <Calendar size={14} className="text-gray-400" />
                      <span>Founded: {nodeDetails.company.founded_year}</span>
                    </div>
                  )}
                  {nodeDetails.company.website && (
                    <div className="flex items-center gap-2">
                      <Globe size={14} className="text-gray-400" />
                      <a 
                        href={nodeDetails.company.website} 
                        target="_blank" 
                        rel="noopener noreferrer"
                        className="text-blue-400 hover:underline"
                      >
                        Website
                      </a>
                    </div>
                  )}
                </div>
              </div>

              {/* Tabs */}
              <div className="flex border-b border-gray-700">
                {['overview', 'connections', 'predictions'].map((tab) => (
                  <button
                    key={tab}
                    onClick={() => setActiveTab(tab as typeof activeTab)}
                    className={`flex-1 py-2 px-3 text-sm font-medium capitalize transition-colors ${
                      activeTab === tab
                        ? 'text-blue-400 border-b-2 border-blue-400'
                        : 'text-gray-400 hover:text-white'
                    }`}
                  >
                    {tab}
                  </button>
                ))}
              </div>

              {/* Tab Content */}
              <div className="space-y-4">
                {activeTab === 'overview' && (
                  <div className="space-y-3">
                    {/* Sectors */}
                    <div className="bg-gray-800 rounded-lg p-3">
                      <h4 className="font-medium mb-2">Connected Sectors</h4>
                      <div className="flex flex-wrap gap-1">
                        {nodeDetails.metrics.sectors.map((sector, index) => (
                          <span
                            key={index}
                            className="px-2 py-1 bg-gray-700 rounded text-xs"
                          >
                            {sector}
                          </span>
                        ))}
                      </div>
                    </div>

                    {/* Average Deal Value */}
                    {nodeDetails.metrics.avgDealValue > 0 && (
                      <div className="bg-gray-800 rounded-lg p-3">
                        <h4 className="font-medium mb-1">Average Deal Value</h4>
                        <div className="text-2xl font-bold text-green-400">
                          {formatCurrency(nodeDetails.metrics.avgDealValue)}
                        </div>
                      </div>
                    )}
                  </div>
                )}

                {activeTab === 'connections' && (
                  <div className="space-y-2">
                    {nodeDetails.connections.length > 0 ? (
                      nodeDetails.connections.map((deal) => (
                        <div key={deal.id} className="bg-gray-800 rounded-lg p-3">
                          <div className="flex items-center justify-between mb-2">
                            <span className={`text-sm font-medium ${getDealTypeColor(deal.deal_type)}`}>
                              {deal.deal_type.toUpperCase()}
                            </span>
                            <span className="text-xs text-gray-400">
                              {formatDate(deal.deal_date)}
                            </span>
                          </div>
                          <p className="text-sm text-gray-300 mb-2">{deal.description}</p>
                          {deal.deal_value && (
                            <div className="text-sm font-medium text-green-400">
                              {formatCurrency(deal.deal_value)}
                            </div>
                          )}
                        </div>
                      ))
                    ) : (
                      <div className="text-center text-gray-400 py-8">
                        No connections found
                      </div>
                    )}
                  </div>
                )}

                {activeTab === 'predictions' && (
                  <div className="space-y-2">
                    {showPredictions && nodeDetails.predictions.length > 0 ? (
                      nodeDetails.predictions.map((prediction) => (
                        <div key={prediction.id} className="bg-gray-800 rounded-lg p-3 border-l-4 border-yellow-400">
                          <div className="flex items-center justify-between mb-2">
                            <span className="text-sm font-medium text-yellow-400">
                              PREDICTED {prediction.deal_type.toUpperCase()}
                            </span>
                            <span className="text-xs text-gray-400">
                              Confidence: {(prediction.confidence_score || 0) * 100}%
                            </span>
                          </div>
                          <p className="text-sm text-gray-300 mb-2">{prediction.description}</p>
                          {prediction.deal_value && (
                            <div className="text-sm font-medium text-green-400">
                              Est. {formatCurrency(prediction.deal_value)}
                            </div>
                          )}
                        </div>
                      ))
                    ) : (
                      <div className="text-center text-gray-400 py-8">
                        {showPredictions ? 'No predictions available' : 'Enable predictions to view forecasts'}
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
          ) : (
            <div className="text-center text-gray-400 py-8">
              No data available
            </div>
          )}
        </div>
      </motion.div>
    </AnimatePresence>
  )
}
