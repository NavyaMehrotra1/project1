'use client'

import React, { useState, useEffect } from 'react'
import { EnhancedGraphVisualization } from './EnhancedGraphVisualization'
import { GraphData } from '@/types'
import { generateMockGraphData } from '@/services/mockData'
import { Toaster } from 'react-hot-toast'

export const GraphDemo: React.FC = () => {
  const [graphData, setGraphData] = useState<GraphData | null>(null)
  const [showPredictions, setShowPredictions] = useState(false)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Simulate loading and then show mock data
    const loadData = async () => {
      setLoading(true)
      
      // Simulate API delay
      await new Promise(resolve => setTimeout(resolve, 1000))
      
      const mockData = generateMockGraphData(showPredictions)
      setGraphData(mockData)
      setLoading(false)
    }

    loadData()
  }, [showPredictions])

  const handleTogglePredictions = () => {
    setShowPredictions(!showPredictions)
  }

  const handleDataUpdate = (newData: GraphData) => {
    setGraphData(newData)
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen bg-gray-900">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <div className="text-white text-lg">Loading Graph Visualization...</div>
          <div className="text-gray-400 text-sm mt-2">Using mock data for demonstration</div>
        </div>
      </div>
    )
  }

  return (
    <div className="h-screen w-full bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 relative overflow-hidden">
      <Toaster 
        position="top-right"
        toastOptions={{
          style: {
            background: 'rgba(0, 0, 0, 0.8)',
            backdropFilter: 'blur(12px)',
            color: '#fff',
            border: '1px solid rgba(255, 255, 255, 0.1)',
            borderRadius: '12px',
          },
        }}
      />
      
      {/* Animated Background Elements */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-purple-500/20 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-blue-500/20 rounded-full blur-3xl animate-pulse delay-1000"></div>
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-indigo-500/10 rounded-full blur-3xl animate-pulse delay-500"></div>
      </div>
      
      {/* Modern Header */}
      <div className="absolute top-0 left-0 right-0 z-50 bg-black/20 backdrop-blur-xl p-6 border-b border-white/10">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-white mb-1 bg-gradient-to-r from-white to-gray-300 bg-clip-text text-transparent">
              Enhanced Graph Visualization
            </h1>
            <p className="text-gray-300 text-sm">
              Interactive dealflow analysis • {graphData?.nodes.length} companies • {graphData?.edges.length} connections
            </p>
          </div>
          
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2 px-3 py-1.5 bg-emerald-500/20 rounded-full border border-emerald-500/30">
              <div className="w-2 h-2 bg-emerald-400 rounded-full animate-pulse"></div>
              <span className="text-emerald-300 text-sm font-medium">Live Demo</span>
            </div>
            
            <button
              onClick={handleTogglePredictions}
              className={`px-4 py-2 rounded-xl font-medium transition-all duration-200 ${
                showPredictions 
                  ? 'bg-amber-500/20 text-amber-300 border border-amber-500/30 shadow-lg shadow-amber-500/20' 
                  : 'bg-white/10 text-gray-300 border border-white/20 hover:bg-white/15 hover:border-white/30'
              }`}
            >
              {showPredictions ? '✨ Hide Predictions' : '🔮 Show Predictions'}
            </button>
          </div>
        </div>
      </div>

      {/* Graph */}
      <div className="pt-20 h-full">
        <EnhancedGraphVisualization
          data={graphData}
          onDataUpdate={handleDataUpdate}
          showPredictions={showPredictions}
          onTogglePredictions={handleTogglePredictions}
          className="w-full h-full"
        />
      </div>

      {/* Modern Instructions Overlay */}
      <div className="absolute bottom-6 right-6 bg-black/30 backdrop-blur-md rounded-xl p-4 max-w-sm border border-white/10 shadow-xl">
        <h3 className="text-white font-semibold mb-3 flex items-center gap-2">
          <span className="w-2 h-2 bg-blue-400 rounded-full"></span>
          Quick Guide
        </h3>
        <ul className="text-gray-200 text-sm space-y-2">
          <li className="flex items-center gap-2">
            <span className="text-blue-400">👆</span>
            Click nodes to view company details
          </li>
          <li className="flex items-center gap-2">
            <span className="text-purple-400">🎯</span>
            Use "What-If" for scenario analysis
          </li>
          <li className="flex items-center gap-2">
            <span className="text-amber-400">🔮</span>
            Toggle predictions for AI insights
          </li>
          <li className="flex items-center gap-2">
            <span className="text-emerald-400">🔍</span>
            Zoom and pan to explore connections
          </li>
        </ul>
      </div>
    </div>
  )
}
