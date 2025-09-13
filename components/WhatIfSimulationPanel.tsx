'use client'

import React, { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import Select from 'react-select'
import { Play, RotateCcw, TrendingUp, AlertTriangle, Info } from 'lucide-react'
import { GraphData, WhatIfRequest, SimulationResult } from '@/types'
import { apiService } from '@/services/api'

interface WhatIfSimulationPanelProps {
  graphData: GraphData | null
  onSimulationResult: (result: SimulationResult) => void
  className?: string
}

interface CompanyOption {
  value: string
  label: string
  sector?: string
}

interface ImpactNode {
  id: string
  name: string
  impact: number
  path: string[]
  magnitude: 'high' | 'medium' | 'low'
  type: 'direct' | 'indirect'
}

const dealTypeOptions = [
  { value: 'merger', label: 'Merger' },
  { value: 'acquisition', label: 'Acquisition' },
  { value: 'partnership', label: 'Partnership' },
  { value: 'joint_venture', label: 'Joint Venture' },
  { value: 'investment', label: 'Investment' },
  { value: 'ipo', label: 'IPO' }
]

export const WhatIfSimulationPanel: React.FC<WhatIfSimulationPanelProps> = ({
  graphData,
  onSimulationResult,
  className = ''
}) => {
  const [companyA, setCompanyA] = useState<CompanyOption | null>(null)
  const [companyB, setCompanyB] = useState<CompanyOption | null>(null)
  const [dealType, setDealType] = useState(dealTypeOptions[0])
  const [dealValue, setDealValue] = useState(1000) // in millions
  const [timeHorizon, setTimeHorizon] = useState(12) // months
  const [confidence, setConfidence] = useState(0.7)
  const [isSimulating, setIsSimulating] = useState(false)
  const [simulationResult, setSimulationResult] = useState<SimulationResult | null>(null)
  const [impactNodes, setImpactNodes] = useState<ImpactNode[]>([])
  const [showAdvanced, setShowAdvanced] = useState(false)

  const companyOptions: CompanyOption[] = graphData?.nodes.map(node => ({
    value: node.id,
    label: node.label,
    sector: node.data?.sector || node.data?.industry
  })) || []

  const customSelectStyles = {
    control: (provided: any) => ({
      ...provided,
      backgroundColor: '#374151',
      borderColor: '#4B5563',
      color: 'white',
      '&:hover': {
        borderColor: '#6B7280'
      }
    }),
    menu: (provided: any) => ({
      ...provided,
      backgroundColor: '#374151',
      border: '1px solid #4B5563'
    }),
    option: (provided: any, state: any) => ({
      ...provided,
      backgroundColor: state.isFocused ? '#4B5563' : '#374151',
      color: 'white',
      '&:hover': {
        backgroundColor: '#4B5563'
      }
    }),
    singleValue: (provided: any) => ({
      ...provided,
      color: 'white'
    }),
    input: (provided: any) => ({
      ...provided,
      color: 'white'
    })
  }

  const runSimulation = async () => {
    if (!companyA || !companyB || !graphData) return

    setIsSimulating(true)
    try {
      const request: WhatIfRequest = {
        scenario: `${dealType.label} between ${companyA.label} and ${companyB.label}`,
        companies_involved: [companyA.value, companyB.value],
        deal_type: dealType.value
      }

      const result = await apiService.simulateScenario(request)
      setSimulationResult(result)
      onSimulationResult(result)

      // Calculate impact nodes
      calculateImpactNodes(companyA.value, companyB.value)
    } catch (error) {
      console.error('Simulation error:', error)
    } finally {
      setIsSimulating(false)
    }
  }

  const calculateImpactNodes = (sourceId: string, targetId: string) => {
    if (!graphData) return

    const impacts: ImpactNode[] = []
    const visited = new Set<string>()
    
    // Find direct connections
    const directConnections = graphData.edges.filter(edge => 
      (edge.source === sourceId || edge.target === sourceId ||
       edge.source === targetId || edge.target === targetId) &&
      edge.source !== targetId && edge.target !== sourceId
    )

    directConnections.forEach(edge => {
      const affectedNodeId = edge.source === sourceId || edge.source === targetId 
        ? edge.target : edge.source
      
      if (!visited.has(affectedNodeId)) {
        const node = graphData.nodes.find(n => n.id === affectedNodeId)
        if (node) {
          impacts.push({
            id: affectedNodeId,
            name: node.label,
            impact: Math.random() * 0.8 + 0.2, // Mock impact calculation
            path: [sourceId, affectedNodeId],
            magnitude: Math.random() > 0.6 ? 'high' : Math.random() > 0.3 ? 'medium' : 'low',
            type: 'direct'
          })
          visited.add(affectedNodeId)
        }
      }
    })

    // Find indirect connections (2 degrees)
    directConnections.forEach(edge => {
      const intermediateId = edge.source === sourceId || edge.source === targetId 
        ? edge.target : edge.source
      
      const secondaryConnections = graphData.edges.filter(e => 
        (e.source === intermediateId || e.target === intermediateId) &&
        !visited.has(e.source === intermediateId ? e.target : e.source)
      )

      secondaryConnections.slice(0, 3).forEach(secondaryEdge => {
        const affectedNodeId = secondaryEdge.source === intermediateId 
          ? secondaryEdge.target : secondaryEdge.source
        
        if (!visited.has(affectedNodeId)) {
          const node = graphData.nodes.find(n => n.id === affectedNodeId)
          if (node) {
            impacts.push({
              id: affectedNodeId,
              name: node.label,
              impact: Math.random() * 0.5 + 0.1,
              path: [sourceId, intermediateId, affectedNodeId],
              magnitude: Math.random() > 0.7 ? 'medium' : 'low',
              type: 'indirect'
            })
            visited.add(affectedNodeId)
          }
        }
      })
    })

    setImpactNodes(impacts.sort((a, b) => b.impact - a.impact))
  }

  const resetSimulation = () => {
    setCompanyA(null)
    setCompanyB(null)
    setDealType(dealTypeOptions[0])
    setDealValue(1000)
    setTimeHorizon(12)
    setConfidence(0.7)
    setSimulationResult(null)
    setImpactNodes([])
  }

  const getMagnitudeColor = (magnitude: string) => {
    switch (magnitude) {
      case 'high': return 'text-red-400 bg-red-900'
      case 'medium': return 'text-yellow-400 bg-yellow-900'
      case 'low': return 'text-green-400 bg-green-900'
      default: return 'text-gray-400 bg-gray-900'
    }
  }

  return (
    <div className={`bg-gray-800 rounded-lg p-4 ${className}`}>
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-white">What-If Simulation</h3>
        <button
          onClick={resetSimulation}
          className="p-2 text-gray-400 hover:text-white transition-colors"
          title="Reset"
        >
          <RotateCcw size={16} />
        </button>
      </div>

      <div className="space-y-4">
        {/* Company Selection */}
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Company A
            </label>
            <Select
              value={companyA}
              onChange={setCompanyA}
              options={companyOptions}
              styles={customSelectStyles}
              placeholder="Select company..."
              isSearchable
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Company B
            </label>
            <Select
              value={companyB}
              onChange={setCompanyB}
              options={companyOptions.filter(opt => opt.value !== companyA?.value)}
              styles={customSelectStyles}
              placeholder="Select company..."
              isSearchable
            />
          </div>
        </div>

        {/* Deal Type */}
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">
            Deal Type
          </label>
          <Select
            value={dealType}
            onChange={(option) => option && setDealType(option)}
            options={dealTypeOptions}
            styles={customSelectStyles}
            isSearchable={false}
          />
        </div>

        {/* Deal Parameters */}
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Deal Value ($ millions)
            </label>
            <input
              type="range"
              min="10"
              max="10000"
              step="10"
              value={dealValue}
              onChange={(e) => setDealValue(Number(e.target.value))}
              className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer"
            />
            <div className="text-center text-sm text-gray-400 mt-1">
              ${dealValue.toLocaleString()}M
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Time Horizon (months)
            </label>
            <input
              type="range"
              min="1"
              max="60"
              step="1"
              value={timeHorizon}
              onChange={(e) => setTimeHorizon(Number(e.target.value))}
              className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer"
            />
            <div className="text-center text-sm text-gray-400 mt-1">
              {timeHorizon} months
            </div>
          </div>
        </div>

        {/* Advanced Options */}
        <div>
          <button
            onClick={() => setShowAdvanced(!showAdvanced)}
            className="flex items-center gap-2 text-sm text-blue-400 hover:text-blue-300 transition-colors"
          >
            <Info size={14} />
            Advanced Options
          </button>
          
          <AnimatePresence>
            {showAdvanced && (
              <motion.div
                initial={{ height: 0, opacity: 0 }}
                animate={{ height: 'auto', opacity: 1 }}
                exit={{ height: 0, opacity: 0 }}
                className="mt-2 space-y-3"
              >
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Confidence Level
                  </label>
                  <input
                    type="range"
                    min="0.1"
                    max="1"
                    step="0.1"
                    value={confidence}
                    onChange={(e) => setConfidence(Number(e.target.value))}
                    className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer"
                  />
                  <div className="text-center text-sm text-gray-400 mt-1">
                    {(confidence * 100).toFixed(0)}%
                  </div>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* Run Simulation Button */}
        <button
          onClick={runSimulation}
          disabled={!companyA || !companyB || isSimulating}
          className="w-full flex items-center justify-center gap-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white py-2 px-4 rounded-lg transition-colors"
        >
          {isSimulating ? (
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
          ) : (
            <Play size={16} />
          )}
          {isSimulating ? 'Simulating...' : 'Run Simulation'}
        </button>

        {/* Results */}
        <AnimatePresence>
          {simulationResult && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="space-y-4"
            >
              {/* Summary */}
              <div className="bg-gray-700 rounded-lg p-4">
                <h4 className="font-medium text-white mb-2">Simulation Results</h4>
                <p className="text-sm text-gray-300 mb-3">{simulationResult.impact_analysis}</p>
                <div className="flex items-center gap-4 text-sm">
                  <div className="flex items-center gap-1">
                    <TrendingUp size={14} className="text-green-400" />
                    <span className="text-gray-300">
                      Confidence: {(simulationResult.confidence_score * 100).toFixed(0)}%
                    </span>
                  </div>
                  <div className="flex items-center gap-1">
                    <AlertTriangle size={14} className="text-yellow-400" />
                    <span className="text-gray-300">Timeline: {simulationResult.timeline}</span>
                  </div>
                </div>
              </div>

              {/* Impact Table */}
              {impactNodes.length > 0 && (
                <div className="bg-gray-700 rounded-lg p-4">
                  <h4 className="font-medium text-white mb-3">Affected Companies</h4>
                  <div className="space-y-2 max-h-64 overflow-y-auto">
                    {impactNodes.map((node) => (
                      <div
                        key={node.id}
                        className="flex items-center justify-between p-2 bg-gray-600 rounded"
                      >
                        <div className="flex-1">
                          <div className="flex items-center gap-2">
                            <span className="text-white text-sm font-medium">
                              {node.name}
                            </span>
                            <span className={`px-2 py-1 rounded text-xs ${getMagnitudeColor(node.magnitude)}`}>
                              {node.magnitude}
                            </span>
                            <span className="text-xs text-gray-400">
                              ({node.type})
                            </span>
                          </div>
                          <div className="text-xs text-gray-400 mt-1">
                            Path: {node.path.map(id => 
                              graphData?.nodes.find(n => n.id === id)?.label || id
                            ).join(' → ')}
                          </div>
                        </div>
                        <div className="text-right">
                          <div className="text-sm font-medium text-white">
                            {(node.impact * 100).toFixed(1)}%
                          </div>
                          <div className="text-xs text-gray-400">impact</div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Market Implications */}
              {simulationResult.market_implications && (
                <div className="bg-gray-700 rounded-lg p-4">
                  <h4 className="font-medium text-white mb-2">Market Implications</h4>
                  <p className="text-sm text-gray-300">{simulationResult.market_implications}</p>
                </div>
              )}
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  )
}
