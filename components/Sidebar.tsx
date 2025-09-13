'use client'

import { useState } from 'react'
import { 
  Network, 
  Zap, 
  GraduationCap, 
  Database, 
  Menu, 
  X,
  TrendingUp,
  Users,
  Activity
} from 'lucide-react'

interface SidebarProps {
  isOpen: boolean
  activeView: string
  onViewChange: (view: 'graph' | 'whatif' | 'education' | 'data') => void
  onToggle: () => void
  graphMetadata?: Record<string, any>
}

export function Sidebar({ isOpen, activeView, onViewChange, onToggle, graphMetadata }: SidebarProps) {
  const menuItems = [
    {
      id: 'graph',
      label: 'Network Graph',
      icon: Network,
      description: 'Visualize M&A network'
    },
    {
      id: 'whatif',
      label: 'What-If Simulator',
      icon: Zap,
      description: 'Simulate scenarios'
    },
    {
      id: 'education',
      label: 'Education Mode',
      icon: GraduationCap,
      description: 'Learn about deals'
    },
    {
      id: 'data',
      label: 'Data Ingestion',
      icon: Database,
      description: 'Import new data'
    }
  ]

  return (
    <>
      {/* Mobile overlay */}
      {isOpen && (
        <div 
          className="fixed inset-0 bg-black bg-opacity-50 z-40 lg:hidden"
          onClick={onToggle}
        />
      )}

      {/* Sidebar */}
      <div className={`
        fixed left-0 top-0 h-full bg-white shadow-lg z-50 transition-all duration-300
        ${isOpen ? 'w-64' : 'w-16'}
      `}>
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b">
          {isOpen && (
            <div>
              <h1 className="text-xl font-bold text-primary-700">DealFlow</h1>
              <p className="text-sm text-gray-500">AI-Native M&A Intelligence</p>
            </div>
          )}
          <button
            onClick={onToggle}
            className="p-2 rounded-lg hover:bg-gray-100 transition-colors"
          >
            {isOpen ? <X size={20} /> : <Menu size={20} />}
          </button>
        </div>

        {/* Navigation */}
        <nav className="p-4 space-y-2">
          {menuItems.map((item) => {
            const Icon = item.icon
            const isActive = activeView === item.id
            
            return (
              <button
                key={item.id}
                onClick={() => onViewChange(item.id as any)}
                className={`
                  w-full flex items-center gap-3 p-3 rounded-lg transition-all
                  ${isActive 
                    ? 'bg-primary-100 text-primary-700 border-l-4 border-primary-500' 
                    : 'hover:bg-gray-100 text-gray-600'
                  }
                  ${!isOpen && 'justify-center'}
                `}
                title={!isOpen ? item.label : undefined}
              >
                <Icon size={20} />
                {isOpen && (
                  <div className="text-left">
                    <div className="font-medium">{item.label}</div>
                    <div className="text-xs text-gray-500">{item.description}</div>
                  </div>
                )}
              </button>
            )
          })}
        </nav>

        {/* Stats Panel */}
        {isOpen && graphMetadata && (
          <div className="p-4 border-t mt-auto">
            <h3 className="font-semibold text-gray-700 mb-3">Network Stats</h3>
            <div className="space-y-3">
              <div className="flex items-center gap-2">
                <Users size={16} className="text-blue-500" />
                <div>
                  <div className="text-sm font-medium">{graphMetadata.total_companies || 0}</div>
                  <div className="text-xs text-gray-500">Companies</div>
                </div>
              </div>
              
              <div className="flex items-center gap-2">
                <Activity size={16} className="text-green-500" />
                <div>
                  <div className="text-sm font-medium">{graphMetadata.total_deals || 0}</div>
                  <div className="text-xs text-gray-500">Deals</div>
                </div>
              </div>
              
              <div className="flex items-center gap-2">
                <TrendingUp size={16} className="text-yellow-500" />
                <div>
                  <div className="text-sm font-medium">{graphMetadata.predicted_deals || 0}</div>
                  <div className="text-xs text-gray-500">Predictions</div>
                </div>
              </div>
            </div>

            {graphMetadata.industries && (
              <div className="mt-4">
                <h4 className="text-xs font-medium text-gray-600 mb-2">Industries</h4>
                <div className="flex flex-wrap gap-1">
                  {graphMetadata.industries.slice(0, 3).map((industry: string) => (
                    <span 
                      key={industry}
                      className="px-2 py-1 bg-gray-100 text-xs rounded"
                    >
                      {industry}
                    </span>
                  ))}
                  {graphMetadata.industries.length > 3 && (
                    <span className="px-2 py-1 bg-gray-100 text-xs rounded">
                      +{graphMetadata.industries.length - 3}
                    </span>
                  )}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </>
  )
}
