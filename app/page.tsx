'use client'

import { useState, useEffect } from 'react'
import { NetworkGraph } from '@/components/NetworkGraph'
import { WhatIfSimulator } from '@/components/WhatIfSimulator'
import { EducationChat } from '@/components/EducationChat'
import { DataIngestion } from '@/components/DataIngestion'
import { CompanyProfile } from '@/components/CompanyProfile'
import { PredictionPanel } from '@/components/PredictionPanel'
import { Sidebar } from '@/components/Sidebar'
import { Header } from '@/components/Header'
import { LoadingSpinner } from '@/components/LoadingSpinner'
import { GraphData } from '@/types'
import { apiService } from '@/services/api'
import toast from 'react-hot-toast'

export default function Home() {
  const [graphData, setGraphData] = useState<GraphData | null>(null)
  const [selectedCompany, setSelectedCompany] = useState<string | null>(null)
  const [activeView, setActiveView] = useState<'graph' | 'whatif' | 'education' | 'data'>('graph')
  const [showPredictions, setShowPredictions] = useState(false)
  const [loading, setLoading] = useState(true)
  const [sidebarOpen, setSidebarOpen] = useState(true)

  useEffect(() => {
    loadGraphData()
  }, [])

  const loadGraphData = async () => {
    try {
      setLoading(true)
      const data = await apiService.getGraphData()
      setGraphData(data)
      toast.success('Graph data loaded successfully')
    } catch (error) {
      console.error('Error loading graph data:', error)
      toast.error('Failed to load graph data')
    } finally {
      setLoading(false)
    }
  }

  const handlePredictionToggle = async () => {
    if (!showPredictions && graphData) {
      try {
        const companies = graphData.nodes.map(node => node.label)
        const predictions = await apiService.predictDeals({
          companies: companies.slice(0, 5), // Limit for demo
          time_horizon: 12
        })
        
        // Add predictions to graph data
        const updatedGraphData = { ...graphData }
        // Implementation would add prediction edges here
        setGraphData(updatedGraphData)
        setShowPredictions(true)
        toast.success('Predictions generated')
      } catch (error) {
        toast.error('Failed to generate predictions')
      }
    } else {
      setShowPredictions(!showPredictions)
    }
  }

  const renderMainContent = () => {
    if (loading) {
      return (
        <div className="flex items-center justify-center h-full">
          <LoadingSpinner />
        </div>
      )
    }

    switch (activeView) {
      case 'graph':
        return (
          <div className="relative h-full">
            <NetworkGraph
              data={graphData}
              onNodeClick={setSelectedCompany}
              showPredictions={showPredictions}
            />
            <PredictionPanel
              onTogglePredictions={handlePredictionToggle}
              showPredictions={showPredictions}
              onRefresh={loadGraphData}
            />
          </div>
        )
      case 'whatif':
        return <WhatIfSimulator />
      case 'education':
        return <EducationChat />
      case 'data':
        return <DataIngestion onDataUpdate={loadGraphData} />
      default:
        return null
    }
  }

  return (
    <div className="flex h-screen bg-gray-50">
      <Sidebar
        isOpen={sidebarOpen}
        activeView={activeView}
        onViewChange={setActiveView}
        onToggle={() => setSidebarOpen(!sidebarOpen)}
        graphMetadata={graphData?.metadata}
      />
      
      <div className={`flex-1 flex flex-col transition-all duration-300 ${sidebarOpen ? 'ml-64' : 'ml-16'}`}>
        <Header
          selectedCompany={selectedCompany}
          onCompanySelect={setSelectedCompany}
          companies={graphData?.nodes.map(n => ({ id: n.id, name: n.label })) || []}
        />
        
        <main className="flex-1 relative overflow-hidden">
          {renderMainContent()}
        </main>
      </div>

      {selectedCompany && (
        <CompanyProfile
          companyId={selectedCompany}
          onClose={() => setSelectedCompany(null)}
        />
      )}
    </div>
  )
}
