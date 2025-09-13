'use client'

import { useState } from 'react'
import { Zap, Send, Loader2, TrendingUp, AlertCircle } from 'lucide-react'
import { apiService } from '@/services/api'
import { SimulationResult } from '@/types'
import toast from 'react-hot-toast'

export function WhatIfSimulator() {
  const [scenario, setScenario] = useState('')
  const [companiesInvolved, setCompaniesInvolved] = useState('')
  const [dealType, setDealType] = useState('')
  const [result, setResult] = useState<SimulationResult | null>(null)
  const [loading, setLoading] = useState(false)

  const predefinedScenarios = [
    "OpenAI partners with Epic Games",
    "Microsoft acquires Anthropic",
    "Google merges with Meta",
    "Apple invests in Tesla",
    "Amazon acquires Salesforce"
  ]

  const dealTypes = [
    { value: '', label: 'Any Deal Type' },
    { value: 'acquisition', label: 'Acquisition' },
    { value: 'merger', label: 'Merger' },
    { value: 'partnership', label: 'Partnership' },
    { value: 'investment', label: 'Investment' },
    { value: 'joint_venture', label: 'Joint Venture' }
  ]

  const handleSimulate = async () => {
    if (!scenario.trim()) {
      toast.error('Please enter a scenario')
      return
    }

    setLoading(true)
    try {
      const companies = companiesInvolved
        .split(',')
        .map(c => c.trim())
        .filter(c => c.length > 0)

      const simulationResult = await apiService.simulateScenario({
        scenario,
        companies_involved: companies,
        deal_type: dealType || undefined
      })

      setResult(simulationResult)
      toast.success('Simulation completed')
    } catch (error) {
      console.error('Simulation error:', error)
      toast.error('Failed to run simulation')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-800 mb-2 flex items-center gap-3">
          <Zap className="text-yellow-500" />
          What-If Simulator
        </h1>
        <p className="text-gray-600">
          Simulate hypothetical M&A scenarios and analyze their potential impact on the market
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Input Panel */}
        <div className="space-y-6">
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h2 className="text-xl font-semibold mb-4">Scenario Setup</h2>
            
            {/* Predefined Scenarios */}
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Quick Scenarios
              </label>
              <div className="grid grid-cols-1 gap-2">
                {predefinedScenarios.map((predefined, index) => (
                  <button
                    key={index}
                    onClick={() => setScenario(predefined)}
                    className="text-left p-3 border border-gray-200 rounded-md hover:bg-gray-50 transition-colors text-sm"
                  >
                    {predefined}
                  </button>
                ))}
              </div>
            </div>

            {/* Custom Scenario */}
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Custom Scenario
              </label>
              <textarea
                value={scenario}
                onChange={(e) => setScenario(e.target.value)}
                placeholder="Describe your hypothetical scenario (e.g., 'What if Microsoft acquires OpenAI for $100B?')"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 h-24 resize-none"
              />
            </div>

            {/* Companies Involved */}
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Companies Involved (comma-separated)
              </label>
              <input
                type="text"
                value={companiesInvolved}
                onChange={(e) => setCompaniesInvolved(e.target.value)}
                placeholder="e.g., Microsoft, OpenAI, Google"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            {/* Deal Type */}
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Deal Type
              </label>
              <select
                value={dealType}
                onChange={(e) => setDealType(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                {dealTypes.map(type => (
                  <option key={type.value} value={type.value}>
                    {type.label}
                  </option>
                ))}
              </select>
            </div>

            {/* Simulate Button */}
            <button
              onClick={handleSimulate}
              disabled={loading || !scenario.trim()}
              className="w-full flex items-center justify-center gap-2 bg-blue-600 text-white px-4 py-3 rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {loading ? (
                <>
                  <Loader2 size={20} className="animate-spin" />
                  Simulating...
                </>
              ) : (
                <>
                  <Send size={20} />
                  Run Simulation
                </>
              )}
            </button>
          </div>
        </div>

        {/* Results Panel */}
        <div className="space-y-6">
          {result ? (
            <div className="bg-white rounded-lg shadow-lg p-6">
              <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
                <TrendingUp className="text-green-500" />
                Simulation Results
              </h2>

              <div className="space-y-4">
                {/* Scenario */}
                <div>
                  <h3 className="font-medium text-gray-700 mb-2">Scenario</h3>
                  <p className="text-gray-600 bg-gray-50 p-3 rounded-md">
                    {result.scenario}
                  </p>
                </div>

                {/* Confidence Score */}
                <div>
                  <h3 className="font-medium text-gray-700 mb-2">Confidence Score</h3>
                  <div className="flex items-center gap-2">
                    <div className="flex-1 bg-gray-200 rounded-full h-2">
                      <div 
                        className="bg-blue-500 h-2 rounded-full transition-all duration-500"
                        style={{ width: `${result.confidence_score * 100}%` }}
                      />
                    </div>
                    <span className="text-sm font-medium">
                      {(result.confidence_score * 100).toFixed(0)}%
                    </span>
                  </div>
                </div>

                {/* Impact Analysis */}
                <div>
                  <h3 className="font-medium text-gray-700 mb-2">Impact Analysis</h3>
                  <p className="text-gray-600 bg-blue-50 p-3 rounded-md">
                    {result.impact_analysis}
                  </p>
                </div>

                {/* Market Implications */}
                <div>
                  <h3 className="font-medium text-gray-700 mb-2">Market Implications</h3>
                  <p className="text-gray-600 bg-yellow-50 p-3 rounded-md">
                    {result.market_implications}
                  </p>
                </div>

                {/* Timeline */}
                <div>
                  <h3 className="font-medium text-gray-700 mb-2">Timeline</h3>
                  <p className="text-gray-600 bg-green-50 p-3 rounded-md">
                    {result.timeline}
                  </p>
                </div>

                {/* Affected Companies */}
                <div>
                  <h3 className="font-medium text-gray-700 mb-2">Affected Companies</h3>
                  <div className="flex flex-wrap gap-2">
                    {result.affected_companies.map((company, index) => (
                      <span 
                        key={index}
                        className="px-3 py-1 bg-purple-100 text-purple-800 rounded-full text-sm"
                      >
                        {company}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          ) : (
            <div className="bg-white rounded-lg shadow-lg p-6 text-center">
              <AlertCircle className="mx-auto text-gray-400 mb-4" size={48} />
              <h3 className="text-lg font-medium text-gray-700 mb-2">
                No Simulation Yet
              </h3>
              <p className="text-gray-500">
                Enter a scenario and run a simulation to see the results here
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
