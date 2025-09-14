'use client'

import React, { useState, useEffect, useCallback, useRef } from 'react'
import { GraphVisualization } from './GraphVisualization'
import { NodeDetailsPanel } from './NodeDetailsPanel'
import { WhatIfSimulationPanel } from './WhatIfSimulationPanel'
import { GraphData, SimulationResult } from '@/types'
import { useWebSocket } from '@/services/websocket'
import { motion, AnimatePresence } from 'framer-motion'
import { Settings, Wifi, WifiOff, Eye, EyeOff, BarChart3, Zap, Crown, Trophy, Star } from 'lucide-react'
import toast from 'react-hot-toast'
import * as d3 from 'd3'

interface EnhancedGraphVisualizationProps {
  data: GraphData | null
  onDataUpdate: (data: GraphData) => void
  showPredictions: boolean
  onTogglePredictions: () => void
  className?: string
}

export const EnhancedGraphVisualization: React.FC<EnhancedGraphVisualizationProps> = ({
  data,
  onDataUpdate,
  showPredictions,
  onTogglePredictions,
  className = ''
}) => {
  const [selectedNode, setSelectedNode] = useState<string | null>(null)
  const [selectedEdge, setSelectedEdge] = useState<string | null>(null)
  const [showNodeDetails, setShowNodeDetails] = useState(false)
  const [showWhatIf, setShowWhatIf] = useState(false)
  const [connectionStatus, setConnectionStatus] = useState<'connected' | 'disconnected' | 'connecting'>('connecting')
  const [realTimeUpdates, setRealTimeUpdates] = useState(true)
  const [simulationResults, setSimulationResults] = useState<SimulationResult[]>([])

  const { socket, isConnected, on, off } = useWebSocket()

  // WebSocket event handlers
  useEffect(() => {
    const handleConnection = () => {
      setConnectionStatus('connected')
      toast.success('Real-time updates connected')
    }

    const handleDisconnection = () => {
      setConnectionStatus('disconnected')
      toast.error('Real-time updates disconnected')
    }

    const handleGraphUpdate = (updatedData: GraphData) => {
      if (realTimeUpdates) {
        onDataUpdate(updatedData)
        toast.success('Graph updated in real-time')
      }
    }

    const handleNodeAdded = (node: any) => {
      if (realTimeUpdates && data) {
        const updatedData = {
          ...data,
          nodes: [...data.nodes, {
            id: node.id,
            label: node.name,
            size: 30,
            color: '#3B82F6',
            data: node
          }]
        }
        onDataUpdate(updatedData)
        toast.success(`New company added: ${node.name}`)
      }
    }

    const handleNodeRemoved = (nodeId: string) => {
      if (realTimeUpdates && data) {
        const updatedData = {
          ...data,
          nodes: data.nodes.filter(n => n.id !== nodeId),
          edges: data.edges.filter(e => e.source !== nodeId && e.target !== nodeId)
        }
        onDataUpdate(updatedData)
        toast.success('Company removed from graph')
      }
    }

    const handleEdgeAdded = (edge: any) => {
      if (realTimeUpdates && data) {
        const updatedData = {
          ...data,
          edges: [...data.edges, {
            id: edge.id,
            source: edge.source_company_id,
            target: edge.target_company_id,
            label: edge.deal_type,
            weight: edge.deal_value ? Math.log10(edge.deal_value) : 1,
            color: '#64748B',
            data: edge
          }]
        }
        onDataUpdate(updatedData)
        toast.success('New deal added to graph')
      }
    }

    const handlePredictionUpdate = (predictions: any[]) => {
      if (realTimeUpdates && data && showPredictions) {
        const predictionEdges = predictions.map(pred => ({
          id: `pred_${pred.id}`,
          source: pred.source_company_id,
          target: pred.target_company_id,
          label: `Predicted ${pred.deal_type}`,
          weight: pred.confidence_score || 0.5,
          color: '#F59E0B',
          data: { ...pred, is_predicted: true }
        }))

        const updatedData = {
          ...data,
          edges: [
            ...data.edges.filter(e => !e.data?.is_predicted),
            ...predictionEdges
          ]
        }
        onDataUpdate(updatedData)
        toast.success('Predictions updated')
      }
    }

    const handleSimulationResult = (result: SimulationResult) => {
      setSimulationResults(prev => [result, ...prev.slice(0, 4)]) // Keep last 5 results
      toast.success('Simulation completed')
    }

    const handleError = (error: string) => {
      toast.error(`WebSocket error: ${error}`)
    }

    // Subscribe to events
    on('connected', handleConnection)
    on('disconnected', handleDisconnection)
    on('graph-update', handleGraphUpdate)
    on('node-added', handleNodeAdded)
    on('node-removed', handleNodeRemoved)
    on('edge-added', handleEdgeAdded)
    on('prediction-update', handlePredictionUpdate)
    on('simulation-result', handleSimulationResult)
    on('error', handleError)

    // Set initial connection status
    setConnectionStatus(isConnected ? 'connected' : 'disconnected')

    // Cleanup
    return () => {
      off('connected', handleConnection)
      off('disconnected', handleDisconnection)
      off('graph-update', handleGraphUpdate)
      off('node-added', handleNodeAdded)
      off('node-removed', handleNodeRemoved)
      off('edge-added', handleEdgeAdded)
      off('prediction-update', handlePredictionUpdate)
      off('simulation-result', handleSimulationResult)
      off('error', handleError)
    }
  }, [on, off, isConnected, realTimeUpdates, data, onDataUpdate, showPredictions])

  const handleNodeClick = useCallback((nodeId: string) => {
    setSelectedNode(nodeId)
    setShowNodeDetails(true)
  }, [])

  const handleEdgeClick = useCallback((edgeId: string) => {
    setSelectedEdge(edgeId)
    // Could show edge details in a tooltip or panel
  }, [])

  const handleSimulationResult = useCallback((result: SimulationResult) => {
    setSimulationResults(prev => [result, ...prev.slice(0, 4)])
    
    // Optionally highlight affected nodes in the graph
    if (data && result.affected_companies) {
      const highlightedData = {
        ...data,
        nodes: data.nodes.map(node => ({
          ...node,
          data: {
            ...node.data,
            highlighted: result.affected_companies.includes(node.id)
          }
        }))
      }
      onDataUpdate(highlightedData)
    }
  }, [data, onDataUpdate])

  const toggleRealTimeUpdates = () => {
    setRealTimeUpdates(!realTimeUpdates)
    toast.success(`Real-time updates ${!realTimeUpdates ? 'enabled' : 'disabled'}`)
  }

  const requestManualUpdate = () => {
    socket.requestGraphUpdate()
    toast.success('Requesting graph update...')
  }

  return (
    <div className={`relative w-full h-full ${className}`}>
      {/* Main Graph */}
      <GraphVisualization
        data={data}
        onNodeClick={handleNodeClick}
        onEdgeClick={handleEdgeClick}
        showPredictions={showPredictions}
        selectedNode={selectedNode}
        className="w-full h-full"
      />

      {/* Top Controls Bar */}
      <div className="absolute top-4 left-4 flex items-center gap-2 bg-gray-800 bg-opacity-90 rounded-lg p-2">
        {/* Connection Status */}
        <div className="flex items-center gap-2">
          {connectionStatus === 'connected' ? (
            <Wifi size={16} className="text-green-400" />
          ) : (
            <WifiOff size={16} className="text-red-400" />
          )}
          <span className="text-white text-sm">
            {connectionStatus === 'connected' ? 'Live' : 'Offline'}
          </span>
        </div>

        {/* Real-time Toggle */}
        <button
          onClick={toggleRealTimeUpdates}
          className={`p-1 rounded transition-colors ${
            realTimeUpdates ? 'text-green-400 hover:bg-green-900' : 'text-gray-400 hover:bg-gray-700'
          }`}
          title="Toggle real-time updates"
        >
          <Zap size={16} />
        </button>

        {/* Predictions Toggle */}
        <button
          onClick={onTogglePredictions}
          className={`p-1 rounded transition-colors ${
            showPredictions ? 'text-yellow-400 hover:bg-yellow-900' : 'text-gray-400 hover:bg-gray-700'
          }`}
          title="Toggle predictions"
        >
          {showPredictions ? <Eye size={16} /> : <EyeOff size={16} />}
        </button>

        {/* Manual Update */}
        <button
          onClick={requestManualUpdate}
          className="p-1 text-blue-400 hover:bg-blue-900 rounded transition-colors"
          title="Request manual update"
        >
          <BarChart3 size={16} />
        </button>

        {/* What-If Toggle */}
        <button
          onClick={() => setShowWhatIf(!showWhatIf)}
          className={`px-2 py-1 text-sm rounded transition-colors ${
            showWhatIf ? 'bg-purple-600 text-white' : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
          }`}
        >
          What-If
        </button>
      </div>

      {/* What-If Simulation Panel */}
      <AnimatePresence>
        {showWhatIf && (
          <motion.div
            initial={{ x: '-100%' }}
            animate={{ x: 0 }}
            exit={{ x: '-100%' }}
            transition={{ type: 'spring', damping: 25, stiffness: 200 }}
            className="absolute left-4 top-20 bottom-4 w-80 z-40"
          >
            <WhatIfSimulationPanel
              graphData={data}
              onSimulationResult={handleSimulationResult}
              className="h-full overflow-y-auto"
            />
          </motion.div>
        )}
      </AnimatePresence>

      {/* Node Details Panel */}
      <AnimatePresence>
        {showNodeDetails && selectedNode && (
          <NodeDetailsPanel
            nodeId={selectedNode}
            graphData={data}
            onClose={() => {
              setShowNodeDetails(false)
              setSelectedNode(null)
            }}
            showPredictions={showPredictions}
          />
        )}
      </AnimatePresence>

      {/* Simulation Results History */}
      <AnimatePresence>
        {simulationResults.length > 0 && (
          <motion.div
            initial={{ y: '100%' }}
            animate={{ y: 0 }}
            exit={{ y: '100%' }}
            className="absolute bottom-4 right-4 w-80 max-h-64 bg-gray-800 bg-opacity-95 rounded-lg p-3 overflow-y-auto"
          >
            <h4 className="text-white font-medium mb-2">Recent Simulations</h4>
            <div className="space-y-2">
              {simulationResults.map((result, index) => (
                <div key={index} className="bg-gray-700 rounded p-2 text-sm">
                  <div className="text-white font-medium truncate">
                    {result.scenario}
                  </div>
                  <div className="text-gray-300 text-xs mt-1">
                    Confidence: {(result.confidence_score * 100).toFixed(0)}%
                  </div>
                </div>
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Loading Overlay for WebSocket Operations */}
      <AnimatePresence>
        {connectionStatus === 'connecting' && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="absolute inset-0 bg-gray-900 bg-opacity-50 flex items-center justify-center z-50"
          >
            <div className="bg-gray-800 rounded-lg p-4 flex items-center gap-3">
              <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-white"></div>
              <span className="text-white">Connecting to real-time updates...</span>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
