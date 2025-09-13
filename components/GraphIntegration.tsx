'use client'

import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { 
  Brain, 
  BookOpen, 
  TrendingUp, 
  Building,
  Users,
  DollarSign,
  ArrowRight,
  Lightbulb,
  Target
} from 'lucide-react'
import { GraphData, GraphNode, GraphEdge } from '@/types'
import { UserProfile } from '@/services/ai-teach-service'

interface GraphIntegrationProps {
  graphData: GraphData | null
  userProfile: UserProfile
  onConceptExplain: (concept: string, context: any) => void
}

export const GraphIntegration: React.FC<GraphIntegrationProps> = ({
  graphData,
  userProfile,
  onConceptExplain
}) => {
  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null)
  const [selectedEdge, setSelectedEdge] = useState<GraphEdge | null>(null)
  const [learningOpportunities, setLearningOpportunities] = useState<any[]>([])

  useEffect(() => {
    if (graphData && selectedNode) {
      generateLearningOpportunities()
    }
  }, [selectedNode, graphData])

  const generateLearningOpportunities = () => {
    if (!selectedNode || !graphData) return

    const opportunities = []
    
    // Find connected nodes and edges
    const connectedEdges = graphData.edges.filter(edge => 
      edge.source === selectedNode.id || edge.target === selectedNode.id
    )
    
    // Generate learning opportunities based on connections
    connectedEdges.forEach(edge => {
      const otherNodeId = edge.source === selectedNode.id ? edge.target : edge.source
      const otherNode = graphData.nodes.find(n => n.id === otherNodeId)
      
      if (otherNode && edge.data) {
        opportunities.push({
          type: 'deal_analysis',
          title: `Analyze ${selectedNode.data.name} ↔ ${otherNode.data.name}`,
          description: `Learn about ${edge.data.deal_type || 'strategic'} relationships`,
          concept: edge.data.deal_type || 'strategic_partnership',
          context: {
            companies: [selectedNode.data.name, otherNode.data.name],
            relationship: edge.data.deal_type,
            value: edge.data.deal_value,
            industry: selectedNode.data.sector
          },
          difficulty: getDifficultyForConcept(edge.data.deal_type),
          icon: getDealTypeIcon(edge.data.deal_type)
        })
      }
    })

    // Add industry-specific learning opportunities
    if (selectedNode.data.sector) {
      opportunities.push({
        type: 'industry_analysis',
        title: `${selectedNode.data.sector} M&A Patterns`,
        description: `Explore M&A trends in ${selectedNode.data.sector}`,
        concept: 'industry_consolidation',
        context: {
          industry: selectedNode.data.sector,
          company: selectedNode.data.name,
          market_cap: selectedNode.data.market_cap
        },
        difficulty: 'intermediate',
        icon: Building
      })
    }

    // Add valuation learning opportunities
    if (selectedNode.data.market_cap) {
      opportunities.push({
        type: 'valuation_analysis',
        title: `Valuation Methods for ${selectedNode.data.name}`,
        description: 'Learn valuation techniques used in M&A',
        concept: 'company_valuation',
        context: {
          company: selectedNode.data.name,
          market_cap: selectedNode.data.market_cap,
          sector: selectedNode.data.sector
        },
        difficulty: 'expert',
        icon: DollarSign
      })
    }

    setLearningOpportunities(opportunities.slice(0, 4)) // Limit to 4 opportunities
  }

  const getDifficultyForConcept = (concept: string): string => {
    const conceptDifficulty: { [key: string]: string } = {
      'acquisition': 'beginner',
      'merger': 'intermediate',
      'joint_venture': 'intermediate',
      'strategic_partnership': 'beginner',
      'spin_off': 'expert',
      'leveraged_buyout': 'expert'
    }
    return conceptDifficulty[concept] || 'intermediate'
  }

  const getDealTypeIcon = (dealType: string) => {
    const iconMap: { [key: string]: any } = {
      'acquisition': TrendingUp,
      'merger': Users,
      'joint_venture': Building,
      'strategic_partnership': Target,
      'spin_off': ArrowRight,
      'leveraged_buyout': DollarSign
    }
    return iconMap[dealType] || TrendingUp
  }

  const isConceptKnown = (concept: string): boolean => {
    return userProfile.known_concepts.includes(concept)
  }

  const shouldShowConcept = (difficulty: string): boolean => {
    const levelOrder = ['beginner', 'intermediate', 'expert']
    const userLevelIndex = levelOrder.indexOf(userProfile.current_level)
    const conceptLevelIndex = levelOrder.indexOf(difficulty)
    return conceptLevelIndex <= userLevelIndex + 1 // Show concepts up to one level above user
  }

  return (
    <div className="bg-black/20 backdrop-blur-md rounded-xl p-6 border border-white/10">
      <div className="flex items-center gap-3 mb-6">
        <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-purple-500 rounded-lg flex items-center justify-center">
          <Brain className="w-5 h-5 text-white" />
        </div>
        <div>
          <h3 className="text-white font-semibold">AI Learning Integration</h3>
          <p className="text-gray-400 text-sm">Learn from real M&A data</p>
        </div>
      </div>

      {/* Node Selection */}
      <div className="mb-6">
        <h4 className="text-white font-medium mb-3">Select a Company to Learn</h4>
        <div className="grid grid-cols-2 gap-2 max-h-32 overflow-y-auto">
          {graphData?.nodes.slice(0, 8).map((node) => (
            <button
              key={node.id}
              onClick={() => setSelectedNode(node)}
              className={`p-2 rounded-lg text-left transition-all text-sm ${
                selectedNode?.id === node.id
                  ? 'bg-blue-500/20 text-blue-300 border border-blue-500/30'
                  : 'bg-white/5 text-gray-300 hover:bg-white/10 border border-white/10'
              }`}
            >
              <div className="font-medium truncate">{node.data.name}</div>
              <div className="text-xs text-gray-400">{node.data.sector}</div>
            </button>
          ))}
        </div>
      </div>

      {/* Learning Opportunities */}
      {selectedNode && learningOpportunities.length > 0 && (
        <div>
          <h4 className="text-white font-medium mb-3">Learning Opportunities</h4>
          <div className="space-y-3">
            {learningOpportunities
              .filter(opp => shouldShowConcept(opp.difficulty))
              .map((opportunity, index) => {
                const Icon = opportunity.icon
                const isKnown = isConceptKnown(opportunity.concept)
                
                return (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.1 }}
                    className="bg-white/5 rounded-lg p-4 border border-white/10 hover:border-purple-500/30 transition-all cursor-pointer"
                    onClick={() => onConceptExplain(opportunity.concept, opportunity.context)}
                  >
                    <div className="flex items-start gap-3">
                      <div className={`w-8 h-8 rounded-lg flex items-center justify-center ${
                        isKnown ? 'bg-green-500/20' : 'bg-purple-500/20'
                      }`}>
                        {isKnown ? (
                          <BookOpen className="w-4 h-4 text-green-400" />
                        ) : (
                          <Icon className="w-4 h-4 text-purple-400" />
                        )}
                      </div>
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          <h5 className="text-white font-medium text-sm">{opportunity.title}</h5>
                          <span className={`px-2 py-0.5 rounded text-xs ${
                            opportunity.difficulty === 'beginner' ? 'bg-green-500/20 text-green-300' :
                            opportunity.difficulty === 'intermediate' ? 'bg-yellow-500/20 text-yellow-300' :
                            'bg-red-500/20 text-red-300'
                          }`}>
                            {opportunity.difficulty}
                          </span>
                          {isKnown && (
                            <span className="px-2 py-0.5 bg-green-500/20 text-green-300 rounded text-xs">
                              Known
                            </span>
                          )}
                        </div>
                        <p className="text-gray-400 text-xs">{opportunity.description}</p>
                      </div>
                      <ArrowRight className="w-4 h-4 text-gray-500" />
                    </div>
                  </motion.div>
                )
              })}
          </div>
        </div>
      )}

      {/* No Selection State */}
      {!selectedNode && (
        <div className="text-center py-8">
          <Lightbulb className="w-12 h-12 text-gray-500 mx-auto mb-3" />
          <p className="text-gray-400 mb-2">Select a company to discover learning opportunities</p>
          <p className="text-gray-500 text-sm">Learn M&A concepts using real market data</p>
        </div>
      )}

      {/* User Level Indicator */}
      <div className="mt-6 pt-4 border-t border-white/10">
        <div className="flex items-center justify-between text-sm">
          <span className="text-gray-400">Your Level:</span>
          <span className={`px-2 py-1 rounded ${
            userProfile.current_level === 'beginner' ? 'bg-green-500/20 text-green-300' :
            userProfile.current_level === 'intermediate' ? 'bg-yellow-500/20 text-yellow-300' :
            'bg-red-500/20 text-red-300'
          }`}>
            {userProfile.current_level.charAt(0).toUpperCase() + userProfile.current_level.slice(1)}
          </span>
        </div>
        <div className="flex items-center justify-between text-sm mt-2">
          <span className="text-gray-400">Known Concepts:</span>
          <span className="text-blue-300">{userProfile.known_concepts.length}</span>
        </div>
      </div>
    </div>
  )
}
