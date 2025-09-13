'use client'

import { useEffect, useRef, useState } from 'react'
import { GraphData, GraphNode, GraphEdge } from '@/types'

interface SimpleNetworkGraphProps {
  data: GraphData | null
  onNodeClick: (nodeId: string) => void
  showPredictions: boolean
}

export function SimpleNetworkGraph({ data, onNodeClick, showPredictions }: SimpleNetworkGraphProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const [tooltip, setTooltip] = useState<{ x: number; y: number; content: string } | null>(null)
  const [nodes, setNodes] = useState<(GraphNode & { x: number; y: number; vx: number; vy: number })[]>([])
  const [edges, setEdges] = useState<GraphEdge[]>([])

  useEffect(() => {
    if (!data || !canvasRef.current) return

    const canvas = canvasRef.current
    const ctx = canvas.getContext('2d')
    if (!ctx) return

    // Set canvas size
    canvas.width = canvas.offsetWidth
    canvas.height = canvas.offsetHeight

    // Filter edges based on showPredictions
    const filteredEdges = showPredictions 
      ? data.edges 
      : data.edges.filter(edge => !edge.data.is_predicted)

    // Initialize node positions
    const initialNodes = data.nodes.map((node, i) => ({
      ...node,
      x: canvas.width / 2 + Math.cos(i * 2 * Math.PI / data.nodes.length) * 150,
      y: canvas.height / 2 + Math.sin(i * 2 * Math.PI / data.nodes.length) * 150,
      vx: 0,
      vy: 0
    }))

    setNodes(initialNodes)
    setEdges(filteredEdges)

    // Simple force simulation
    let animationId: number
    const simulate = () => {
      setNodes(prevNodes => {
        const newNodes = [...prevNodes]
        
        // Apply forces
        for (let i = 0; i < newNodes.length; i++) {
          const node = newNodes[i]
          
          // Center force
          const centerX = canvas.width / 2
          const centerY = canvas.height / 2
          const centerForce = 0.001
          node.vx += (centerX - node.x) * centerForce
          node.vy += (centerY - node.y) * centerForce
          
          // Repulsion between nodes
          for (let j = 0; j < newNodes.length; j++) {
            if (i === j) continue
            const other = newNodes[j]
            const dx = node.x - other.x
            const dy = node.y - other.y
            const distance = Math.sqrt(dx * dx + dy * dy)
            if (distance > 0 && distance < 100) {
              const force = 50 / (distance * distance)
              node.vx += (dx / distance) * force
              node.vy += (dy / distance) * force
            }
          }
          
          // Apply velocity with damping
          node.vx *= 0.9
          node.vy *= 0.9
          node.x += node.vx
          node.y += node.vy
          
          // Keep nodes in bounds
          node.x = Math.max(node.size, Math.min(canvas.width - node.size, node.x))
          node.y = Math.max(node.size, Math.min(canvas.height - node.size, node.y))
        }
        
        return newNodes
      })
      
      animationId = requestAnimationFrame(simulate)
    }
    
    simulate()

    return () => {
      if (animationId) cancelAnimationFrame(animationId)
    }
  }, [data, showPredictions])

  // Draw function
  useEffect(() => {
    if (!canvasRef.current || nodes.length === 0) return

    const canvas = canvasRef.current
    const ctx = canvas.getContext('2d')
    if (!ctx) return

    const draw = () => {
      // Clear canvas
      ctx.clearRect(0, 0, canvas.width, canvas.height)

      // Draw edges
      edges.forEach(edge => {
        const sourceNode = nodes.find(n => n.id === edge.source)
        const targetNode = nodes.find(n => n.id === edge.target)
        
        if (sourceNode && targetNode) {
          ctx.beginPath()
          ctx.moveTo(sourceNode.x, sourceNode.y)
          ctx.lineTo(targetNode.x, targetNode.y)
          ctx.strokeStyle = edge.color
          ctx.lineWidth = edge.weight
          if (edge.data.is_predicted) {
            ctx.setLineDash([5, 5])
          } else {
            ctx.setLineDash([])
          }
          ctx.stroke()
        }
      })

      // Draw nodes
      nodes.forEach(node => {
        ctx.beginPath()
        ctx.arc(node.x, node.y, node.size, 0, 2 * Math.PI)
        ctx.fillStyle = node.color
        ctx.fill()
        ctx.strokeStyle = '#fff'
        ctx.lineWidth = node.data.extraordinary_score > 0.8 ? 4 : 2
        ctx.stroke()

        // Draw labels
        ctx.fillStyle = '#333'
        ctx.font = '12px Arial'
        ctx.textAlign = 'center'
        ctx.fillText(node.label, node.x, node.y + node.size + 15)
      })

      requestAnimationFrame(draw)
    }

    draw()
  }, [nodes, edges])

  const handleCanvasClick = (event: React.MouseEvent<HTMLCanvasElement>) => {
    const canvas = canvasRef.current
    if (!canvas) return

    const rect = canvas.getBoundingClientRect()
    const x = event.clientX - rect.left
    const y = event.clientY - rect.top

    // Check if click is on a node
    for (const node of nodes) {
      const distance = Math.sqrt((x - node.x) ** 2 + (y - node.y) ** 2)
      if (distance <= node.size) {
        onNodeClick(node.id)
        break
      }
    }
  }

  const handleCanvasMouseMove = (event: React.MouseEvent<HTMLCanvasElement>) => {
    const canvas = canvasRef.current
    if (!canvas) return

    const rect = canvas.getBoundingClientRect()
    const x = event.clientX - rect.left
    const y = event.clientY - rect.top

    // Check if mouse is over a node
    let foundNode = null
    for (const node of nodes) {
      const distance = Math.sqrt((x - node.x) ** 2 + (y - node.y) ** 2)
      if (distance <= node.size) {
        foundNode = node
        break
      }
    }

    if (foundNode) {
      setTooltip({
        x: event.clientX,
        y: event.clientY,
        content: `${foundNode.label}\nIndustry: ${foundNode.data.industry}\nMarket Cap: $${foundNode.data.market_cap ? (foundNode.data.market_cap / 1e9).toFixed(1) + 'B' : 'N/A'}`
      })
    } else {
      setTooltip(null)
    }
  }

  return (
    <div className="relative w-full h-full">
      <canvas
        ref={canvasRef}
        className="w-full h-full cursor-pointer"
        style={{ background: '#fafafa' }}
        onClick={handleCanvasClick}
        onMouseMove={handleCanvasMouseMove}
        onMouseLeave={() => setTooltip(null)}
      />
      
      {tooltip && (
        <div
          className="tooltip fixed pointer-events-none z-50"
          style={{
            left: tooltip.x + 10,
            top: tooltip.y - 10,
          }}
        >
          {tooltip.content.split('\n').map((line, i) => (
            <div key={i}>{line}</div>
          ))}
        </div>
      )}

      {/* Simple Legend */}
      <div className="absolute bottom-4 left-4 bg-white p-4 rounded-lg shadow-lg">
        <h3 className="font-semibold mb-2">Legend</h3>
        <div className="space-y-1 text-sm">
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded-full bg-blue-500"></div>
            <span>Technology</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded-full bg-purple-500"></div>
            <span>AI</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-0.5 bg-green-500"></div>
            <span>Completed Deal</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-0.5 bg-yellow-500 border-dashed border-t-2"></div>
            <span>Predicted Deal</span>
          </div>
        </div>
      </div>
    </div>
  )
}
