'use client'

import React, { useEffect, useRef, useState, useCallback } from 'react'
import cytoscape from 'cytoscape'
import dagre from 'cytoscape-dagre'
import coseBilkent from 'cytoscape-cose-bilkent'
import { GraphData, GraphNode, GraphEdge } from '@/types'
import { motion, AnimatePresence } from 'framer-motion'
import { ZoomIn, ZoomOut, RotateCcw, Download, Settings } from 'lucide-react'

// Register cytoscape extensions
cytoscape.use(dagre)
cytoscape.use(coseBilkent)

interface GraphVisualizationProps {
  data: GraphData | null
  onNodeClick: (nodeId: string) => void
  onEdgeClick?: (edgeId: string) => void
  showPredictions: boolean
  selectedNode?: string | null
  className?: string
}

// Modern gradient color scheme
const SECTOR_COLORS = {
  'Technology': '#6366F1', // Indigo
  'Healthcare': '#06B6D4', // Cyan
  'Finance': '#F59E0B', // Amber
  'Energy': '#EF4444', // Red
  'Consumer': '#8B5CF6', // Violet
  'Industrial': '#64748B', // Slate
  'Real Estate': '#EC4899', // Pink
  'Materials': '#10B981', // Emerald
  'Utilities': '#0EA5E9', // Sky
  'Telecommunications': '#F97316', // Orange
  'Automotive': '#DC2626', // Red-600
  'E-commerce': '#7C3AED', // Violet-600
  'default': '#6B7280'
}

// Gradient backgrounds for nodes
const SECTOR_GRADIENTS = {
  'Technology': 'linear-gradient(135deg, #6366F1 0%, #8B5CF6 100%)',
  'Healthcare': 'linear-gradient(135deg, #06B6D4 0%, #10B981 100%)',
  'Finance': 'linear-gradient(135deg, #F59E0B 0%, #F97316 100%)',
  'Energy': 'linear-gradient(135deg, #EF4444 0%, #DC2626 100%)',
  'Consumer': 'linear-gradient(135deg, #8B5CF6 0%, #EC4899 100%)',
  'Industrial': 'linear-gradient(135deg, #64748B 0%, #475569 100%)',
  'Real Estate': 'linear-gradient(135deg, #EC4899 0%, #BE185D 100%)',
  'Materials': 'linear-gradient(135deg, #10B981 0%, #059669 100%)',
  'Utilities': 'linear-gradient(135deg, #0EA5E9 0%, #0284C7 100%)',
  'Telecommunications': 'linear-gradient(135deg, #F97316 0%, #EA580C 100%)',
  'Automotive': 'linear-gradient(135deg, #DC2626 0%, #B91C1C 100%)',
  'E-commerce': 'linear-gradient(135deg, #7C3AED 0%, #6D28D9 100%)',
  'default': 'linear-gradient(135deg, #6B7280 0%, #4B5563 100%)'
}

export const GraphVisualization: React.FC<GraphVisualizationProps> = ({
  data,
  onNodeClick,
  onEdgeClick,
  showPredictions,
  selectedNode,
  className = ''
}) => {
  const cyRef = useRef<HTMLDivElement>(null)
  const cyInstance = useRef<cytoscape.Core | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [layoutType, setLayoutType] = useState<'dagre' | 'cose-bilkent' | 'circle'>('dagre')
  const [showControls, setShowControls] = useState(false)

  // Initialize Cytoscape
  const initializeCytoscape = useCallback(() => {
    if (!cyRef.current || !data) return

    // Destroy existing instance
    if (cyInstance.current) {
      cyInstance.current.destroy()
    }

    // Prepare nodes with modern styling
    const nodes = data.nodes.map((node: GraphNode) => {
      const degree = data.edges.filter(e => e.source === node.id || e.target === node.id).length
      const sector = node.data?.sector || node.data?.industry || 'default'
      const baseSize = 24 // Smaller base size
      const sizeMultiplier = Math.min(2, degree * 0.3) // More controlled sizing
      
      return {
        data: {
          id: node.id,
          label: node.label,
          ...node.data,
          degree
        },
        style: {
          'background-color': SECTOR_COLORS[sector as keyof typeof SECTOR_COLORS] || SECTOR_COLORS.default,
          'background-gradient': 'radial-gradient',
          'background-gradient-stop-colors': `${SECTOR_COLORS[sector as keyof typeof SECTOR_COLORS] || SECTOR_COLORS.default} rgba(255,255,255,0.3)`,
          'background-gradient-stop-positions': '0% 70%',
          'width': baseSize + sizeMultiplier * 8,
          'height': baseSize + sizeMultiplier * 8,
          'label': node.label,
          'font-size': Math.max(9, Math.min(12, 8 + sizeMultiplier)),
          'font-family': 'Inter, system-ui, sans-serif',
          'font-weight': '600',
          'text-valign': 'center',
          'text-halign': 'center',
          'color': '#ffffff',
          'text-outline-width': 1.5,
          'text-outline-color': 'rgba(0,0,0,0.8)',
          'text-outline-opacity': 0.8,
          'border-width': selectedNode === node.id ? 3 : 1.5,
          'border-color': selectedNode === node.id ? '#FBBF24' : 'rgba(255,255,255,0.4)',
          'border-opacity': selectedNode === node.id ? 1 : 0.6,
          'shadow-blur': 8,
          'shadow-color': 'rgba(0,0,0,0.3)',
          'shadow-offset-x': 0,
          'shadow-offset-y': 2,
          'transition-property': 'all',
          'transition-duration': '0.2s'
        }
      }
    })

    // Prepare edges with modern styling
    const edges = data.edges.map((edge: GraphEdge) => {
      const isPredicted = edge.data?.is_predicted || false
      const dealType = edge.data?.deal_type || 'unknown'
      const weight = edge.weight || 1
      
      // Enhanced color scheme for edges
      let color = '#64748B'
      let glowColor = 'rgba(100, 116, 139, 0.3)'
      
      if (isPredicted) {
        color = showPredictions ? '#FBBF24' : 'transparent'
        glowColor = 'rgba(251, 191, 36, 0.4)'
      } else {
        switch (dealType) {
          case 'merger':
          case 'acquisition':
            color = '#EF4444'
            glowColor = 'rgba(239, 68, 68, 0.3)'
            break
          case 'partnership':
          case 'joint_venture':
            color = '#10B981'
            glowColor = 'rgba(16, 185, 129, 0.3)'
            break
          case 'investment':
            color = '#6366F1'
            glowColor = 'rgba(99, 102, 241, 0.3)'
            break
          case 'ipo':
            color = '#8B5CF6'
            glowColor = 'rgba(139, 92, 246, 0.3)'
            break
          default:
            color = '#64748B'
            glowColor = 'rgba(100, 116, 139, 0.3)'
        }
      }

      return {
        data: {
          id: edge.id,
          source: edge.source,
          target: edge.target,
          label: edge.label,
          ...edge.data,
          weight,
          color
        },
        style: {
          'curve-style': 'unbundled-bezier',
          'control-point-distances': [20, -20],
          'control-point-weights': [0.25, 0.75],
          width: (ele: any) => Math.max(2, ele.data('weight') || 2),
          'line-color': (ele: any) => ele.data('color') || '#64748b',
          opacity: 0.8,
          'text-opacity': 0.9,
          label: (ele: any) => ele.data('label') || '',
          'font-size': '10px',
          'font-weight': 'bold',
          color: '#ffffff',
          'text-outline-width': 2,
          'text-outline-color': '#000000',
          'text-margin-y': -10,
          'edge-text-rotation': 'autorotate'
        }
      }
    })

    // Initialize Cytoscape
    const cy = cytoscape({
      container: cyRef.current,
      elements: [...nodes, ...edges],
      style: [
        {
          selector: 'node',
          style: {
            'transition-property': 'background-color, border-color, width, height',
            'transition-duration': '0.3s'
          }
        },
        {
          selector: 'edge',
          style: {
            'transition-property': 'line-color, width, opacity',
            'transition-duration': '0.3s'
          }
        },
        {
          selector: 'node:hover',
          style: {
            'border-width': 3,
            'border-color': '#FFD700'
          }
        },
        {
          selector: 'edge:hover',
          style: {
            'width': 'data(weight) * 3',
            'opacity': 1
          }
        }
      ],
      layout: getLayoutConfig(layoutType),
      minZoom: 0.1,
      maxZoom: 3,
      wheelSensitivity: 0.2
    })

    // Event handlers
    cy.on('tap', 'node', (evt) => {
      const node = evt.target
      onNodeClick(node.id())
    })

    cy.on('tap', 'edge', (evt) => {
      const edge = evt.target
      if (onEdgeClick) {
        onEdgeClick(edge.id())
      }
    })

    // Store instance
    cyInstance.current = cy
    setIsLoading(false)
  }, [data, showPredictions, selectedNode, layoutType, onNodeClick, onEdgeClick])

  // Layout configuration
  const getLayoutConfig = (type: string) => {
    switch (type) {
      case 'dagre':
        return {
          name: 'dagre',
          rankDir: 'TB',
          nodeSep: 50,
          edgeSep: 10,
          rankSep: 100,
          animate: true,
          animationDuration: 1000
        }
      case 'cose-bilkent':
        return {
          name: 'cose-bilkent',
          animate: true,
          animationDuration: 1000,
          nodeRepulsion: 4500,
          idealEdgeLength: 50,
          edgeElasticity: 0.45
        }
      case 'circle':
        return {
          name: 'circle',
          animate: true,
          animationDuration: 1000
        }
      default:
        return { name: 'random' }
    }
  }

  // Control functions
  const zoomIn = () => cyInstance.current?.zoom(cyInstance.current.zoom() * 1.2)
  const zoomOut = () => cyInstance.current?.zoom(cyInstance.current.zoom() * 0.8)
  const resetView = () => cyInstance.current?.fit()
  const changeLayout = (newLayout: typeof layoutType) => {
    setLayoutType(newLayout)
    if (cyInstance.current) {
      cyInstance.current.layout(getLayoutConfig(newLayout)).run()
    }
  }

  const exportGraph = () => {
    if (cyInstance.current) {
      const png = cyInstance.current.png({ scale: 2, full: true })
      const link = document.createElement('a')
      link.download = 'graph-visualization.png'
      link.href = png
      link.click()
    }
  }

  useEffect(() => {
    initializeCytoscape()
  }, [initializeCytoscape])

  useEffect(() => {
    // Update prediction visibility
    if (cyInstance.current) {
      cyInstance.current.edges().forEach(edge => {
        const isPredicted = edge.data('is_predicted')
        if (isPredicted) {
          edge.style('opacity', showPredictions ? 0.8 : 0)
        }
      })
    }
  }, [showPredictions])

  return (
    <div className={`relative w-full h-full bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 rounded-xl overflow-hidden ${className}`}>
      {/* Graph Container */}
      <div ref={cyRef} className="w-full h-full" />
      
      {/* Loading Overlay */}
      <AnimatePresence>
        {isLoading && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="absolute inset-0 bg-gray-900 bg-opacity-75 flex items-center justify-center"
          >
            <div className="text-white text-lg">Loading graph...</div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Controls */}
      <div className="absolute top-4 right-4 flex flex-col gap-2">
        <button
          onClick={() => setShowControls(!showControls)}
          className="p-3 bg-black/30 backdrop-blur-md text-white rounded-xl hover:bg-black/40 transition-all duration-200 border border-white/10 shadow-lg"
        >
          <Settings size={18} />
        </button>
        
        <AnimatePresence>
          {showControls && (
            <motion.div
              initial={{ opacity: 0, y: -10, scale: 0.95 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              exit={{ opacity: 0, y: -10, scale: 0.95 }}
              className="flex flex-col gap-2 bg-black/30 backdrop-blur-md p-3 rounded-xl border border-white/10 shadow-xl"
            >
              <button
                onClick={zoomIn}
                className="p-2 text-white hover:bg-white/10 rounded-lg transition-all duration-200"
                title="Zoom In"
              >
                <ZoomIn size={16} />
              </button>
              
              <button
                onClick={zoomOut}
                className="p-2 text-white hover:bg-white/10 rounded-lg transition-all duration-200"
                title="Zoom Out"
              >
                <ZoomOut size={16} />
              </button>
              
              <button
                onClick={resetView}
                className="p-2 text-white hover:bg-white/10 rounded-lg transition-all duration-200"
                title="Reset View"
              >
                <RotateCcw size={16} />
              </button>
              
              <button
                onClick={exportGraph}
                className="p-2 text-white hover:bg-white/10 rounded-lg transition-all duration-200"
                title="Export PNG"
              >
                <Download size={16} />
              </button>
              
              <select
                value={layoutType}
                onChange={(e) => changeLayout(e.target.value as typeof layoutType)}
                className="p-2 bg-white/10 backdrop-blur-sm text-white text-sm rounded-lg border border-white/20 focus:border-white/40 focus:outline-none"
              >
                <option value="dagre" className="bg-gray-800">Hierarchical</option>
                <option value="cose-bilkent" className="bg-gray-800">Force-directed</option>
                <option value="circle" className="bg-gray-800">Circular</option>
              </select>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Modern Legend */}
      <div className="absolute bottom-4 left-4 bg-black/30 backdrop-blur-md p-4 rounded-xl border border-white/10 shadow-xl">
        <div className="font-semibold mb-3 text-white text-sm">Deal Types</div>
        <div className="space-y-2">
          <div className="flex items-center gap-3">
            <div className="w-3 h-3 bg-gradient-to-r from-red-500 to-red-600 rounded-full shadow-sm"></div>
            <span className="text-gray-200 text-xs">Mergers & Acquisitions</span>
          </div>
          <div className="flex items-center gap-3">
            <div className="w-3 h-3 bg-gradient-to-r from-emerald-500 to-emerald-600 rounded-full shadow-sm"></div>
            <span className="text-gray-200 text-xs">Partnerships</span>
          </div>
          <div className="flex items-center gap-3">
            <div className="w-3 h-3 bg-gradient-to-r from-indigo-500 to-indigo-600 rounded-full shadow-sm"></div>
            <span className="text-gray-200 text-xs">Investments</span>
          </div>
          <div className="flex items-center gap-3">
            <div className="w-3 h-0.5 bg-gradient-to-r from-amber-400 to-amber-500 border-dashed"></div>
            <span className="text-gray-200 text-xs">AI Predictions</span>
          </div>
        </div>
      </div>
    </div>
  )
}
