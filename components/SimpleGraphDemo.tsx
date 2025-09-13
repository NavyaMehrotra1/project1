'use client'

import React, { useState, useEffect } from 'react'
import { GraphVisualization } from './GraphVisualization'
import { GraphIntegration } from './GraphIntegration'
import { GraphData } from '@/types'
import { apiService } from '@/services/api'
import { aiTeachService, UserProfile } from '@/services/ai-teach-service'
import { motion } from 'framer-motion'
import { RefreshCw, Eye, EyeOff, Zap, Brain } from 'lucide-react'
import toast from 'react-hot-toast'

export const SimpleGraphDemo: React.FC = () => {
  const [graphData, setGraphData] = useState<GraphData | null>(null)
  const [loading, setLoading] = useState(true)
  const [showPredictions, setShowPredictions] = useState(true)
  const [refreshing, setRefreshing] = useState(false)
  const [showAITeach, setShowAITeach] = useState(false)
  const [userProfile, setUserProfile] = useState<UserProfile | null>(null)

  useEffect(() => {
    loadGraphData()
    loadUserProfile()
  }, [])

  const loadUserProfile = async () => {
    try {
      // Try to load existing profile from localStorage
      const savedProfile = localStorage.getItem('ai-teach-profile')
      if (savedProfile) {
        setUserProfile(JSON.parse(savedProfile))
      }
    } catch (error) {
      console.error('Error loading user profile:', error)
    }
  }

  const loadGraphData = async () => {
    try {
      setLoading(true)
      const data = await apiService.getGraphData()
      setGraphData(data)
      console.log('Graph data loaded:', data)
      toast.success(`Loaded ${data.nodes.length} companies with ${data.metadata.ai_inferred_relationships || 0} AI predictions`)
    } catch (error) {
      console.error('Error loading graph data:', error)
      toast.error('Failed to load graph data')
    } finally {
      setLoading(false)
    }
  }

  const handleRefresh = async () => {
    setRefreshing(true)
    await loadGraphData()
    setRefreshing(false)
  }

  const handleNodeClick = (nodeId: string) => {
    console.log('Node clicked:', nodeId)
    toast.success(`Selected: ${nodeId}`)
  }

  const handleConceptExplain = async (concept: string, context: any) => {
    try {
      toast.success(`Learning about: ${concept.replace('_', ' ')}`)
      // In a real implementation, this would open the AI-Teach concept explorer
      // or provide an inline explanation
    } catch (error) {
      console.error('Error explaining concept:', error)
      toast.error('Failed to explain concept')
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-900 via-slate-900 to-purple-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-white mx-auto mb-4"></div>
          <p className="text-white text-lg">Loading AI-Inference Graph...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-900 via-slate-900 to-purple-900 relative overflow-hidden">
      {/* Animated Background */}
      <div className="absolute inset-0">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-purple-500/20 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-blue-500/20 rounded-full blur-3xl animate-pulse delay-1000"></div>
      </div>

      {/* Header */}
      <div className="relative z-10 p-6">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-4xl font-bold bg-gradient-to-r from-white to-purple-200 bg-clip-text text-transparent">
              AI-Inference Graph MVP
            </h1>
            <p className="text-purple-200 mt-2">
              {graphData ? `${graphData.nodes.length} companies • ${graphData.edges.length} relationships • ${graphData.metadata.ai_inferred_relationships || 0} AI predictions` : 'Loading...'}
            </p>
          </div>
          
          <div className="flex items-center gap-4">
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => setShowPredictions(!showPredictions)}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-all ${
                showPredictions 
                  ? 'bg-yellow-500/20 text-yellow-300 border border-yellow-500/30' 
                  : 'bg-white/10 text-white border border-white/20'
              }`}
            >
              {showPredictions ? <Eye size={18} /> : <EyeOff size={18} />}
              AI Predictions
            </motion.button>

            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => setShowAITeach(!showAITeach)}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-all ${
                showAITeach 
                  ? 'bg-blue-500/20 text-blue-300 border border-blue-500/30' 
                  : 'bg-white/10 text-white border border-white/20'
              }`}
            >
              <Brain size={18} />
              AI Teacher
            </motion.button>

            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={handleRefresh}
              disabled={refreshing}
              className="flex items-center gap-2 px-4 py-2 bg-white/10 hover:bg-white/20 text-white rounded-lg border border-white/20 transition-all"
            >
              <RefreshCw size={18} className={refreshing ? 'animate-spin' : ''} />
              Refresh
            </motion.button>
          </div>
        </div>

        {/* Stats Bar */}
        <div className="grid grid-cols-4 gap-4 mb-6">
          <div className="bg-black/20 backdrop-blur-md rounded-lg p-4 border border-white/10">
            <div className="text-2xl font-bold text-white">{graphData?.nodes.length || 0}</div>
            <div className="text-purple-200 text-sm">Companies</div>
          </div>
          <div className="bg-black/20 backdrop-blur-md rounded-lg p-4 border border-white/10">
            <div className="text-2xl font-bold text-white">{graphData?.edges.length || 0}</div>
            <div className="text-purple-200 text-sm">Relationships</div>
          </div>
          <div className="bg-black/20 backdrop-blur-md rounded-lg p-4 border border-white/10">
            <div className="text-2xl font-bold text-yellow-300">{graphData?.metadata.ai_inferred_relationships || 0}</div>
            <div className="text-purple-200 text-sm">AI Predictions</div>
          </div>
          <div className="bg-black/20 backdrop-blur-md rounded-lg p-4 border border-white/10">
            <div className="text-2xl font-bold text-white">{graphData?.metadata.industries?.length || 0}</div>
            <div className="text-purple-200 text-sm">Industries</div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex gap-6">
        {/* Graph Container */}
        <div className={showAITeach ? "flex-1" : "w-full"}>
          <div className="bg-black/20 backdrop-blur-md rounded-xl border border-white/10 overflow-hidden">
            {graphData && (
              <GraphVisualization
                data={graphData}
                onNodeClick={handleNodeClick}
                showPredictions={showPredictions}
              />
            )}
          </div>
        </div>

        {/* AI Teacher Integration Panel */}
        {showAITeach && userProfile && (
          <div className="w-96">
            <GraphIntegration
              graphData={graphData}
              userProfile={userProfile}
              onConceptExplain={handleConceptExplain}
            />
          </div>
        )}

        {/* AI Teacher Setup Panel */}
        {showAITeach && !userProfile && (
          <div className="w-96">
            <div className="bg-black/20 backdrop-blur-md rounded-xl p-6 border border-white/10">
              <div className="text-center">
                <Brain className="w-12 h-12 text-blue-400 mx-auto mb-4" />
                <h3 className="text-white font-semibold mb-2">AI Teacher Setup</h3>
                <p className="text-gray-300 text-sm mb-4">
                  Complete your background assessment to unlock AI-powered learning from the graph data.
                </p>
                <a
                  href="/ai-teach"
                  className="inline-flex items-center gap-2 bg-gradient-to-r from-blue-500 to-purple-500 text-white px-4 py-2 rounded-lg hover:from-blue-600 hover:to-purple-600 transition-all"
                >
                  <Brain className="w-4 h-4" />
                  Start AI Teacher
                </a>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Legend */}
      <div className="absolute bottom-6 left-6 bg-black/30 backdrop-blur-md rounded-xl p-4 border border-white/10">
        <h3 className="text-white font-semibold mb-3 flex items-center gap-2">
          <Zap className="w-4 h-4 text-yellow-400" />
          Legend
        </h3>
        <div className="space-y-2 text-sm">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-green-400"></div>
            <span className="text-gray-200">Partnerships</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-blue-400"></div>
            <span className="text-gray-200">Investments</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-yellow-400"></div>
            <span className="text-gray-200">AI Predictions</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-red-400"></div>
            <span className="text-gray-200">Acquisitions</span>
          </div>
        </div>
      </div>

      {/* Instructions */}
      <div className="absolute bottom-6 right-6 bg-black/30 backdrop-blur-md rounded-xl p-4 max-w-sm border border-white/10">
        <h3 className="text-white font-semibold mb-3">How to Use</h3>
        <ul className="text-gray-200 text-sm space-y-1">
          <li>• Click nodes to view company details</li>
          <li>• Yellow edges show AI predictions</li>
          <li>• Zoom and pan to explore</li>
          <li>• Toggle predictions on/off</li>
        </ul>
      </div>
    </div>
  )
}
