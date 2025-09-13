'use client'

import { useEffect, useRef, useState } from 'react'
import * as d3 from 'd3'
import { GraphData, GraphNode, GraphEdge } from '@/types'

interface NetworkGraphProps {
  data: GraphData | null
  onNodeClick: (nodeId: string) => void
  showPredictions: boolean
}

export function NetworkGraph({ data, onNodeClick, showPredictions }: NetworkGraphProps) {
  const svgRef = useRef<SVGSVGElement>(null)
  const [tooltip, setTooltip] = useState<{ x: number; y: number; content: string } | null>(null)

  useEffect(() => {
    if (!data || !svgRef.current) return

    const svg = d3.select(svgRef.current)
    svg.selectAll('*').remove()

    const width = svgRef.current.clientWidth
    const height = svgRef.current.clientHeight

    // Filter data based on showPredictions
    const filteredEdges = showPredictions 
      ? data.edges 
      : data.edges.filter(edge => !edge.data.is_predicted)

    // Create simulation
    const simulation = d3.forceSimulation(data.nodes as any)
      .force('link', d3.forceLink(filteredEdges).id((d: any) => d.id).distance(150))
      .force('charge', d3.forceManyBody().strength(-300))
      .force('center', d3.forceCenter(width / 2, height / 2))
      .force('collision', d3.forceCollide().radius(30))

    // Create zoom behavior
    const zoom = d3.zoom()
      .scaleExtent([0.1, 4])
      .on('zoom', (event) => {
        g.attr('transform', event.transform)
      })

    svg.call(zoom as any)

    // Create main group
    const g = svg.append('g')

    // Create links
    const link = g.append('g')
      .selectAll('line')
      .data(filteredEdges)
      .enter().append('line')
      .attr('class', 'link')
      .attr('stroke', d => d.color)
      .attr('stroke-width', d => Math.max(1, d.weight * 2))
      .attr('stroke-opacity', d => d.data.is_predicted ? 0.6 : 0.8)
      .style('stroke-dasharray', d => d.data.is_predicted ? '5,5' : 'none')

    // Create nodes
    const node = g.append('g')
      .selectAll('circle')
      .data(data.nodes)
      .enter().append('circle')
      .attr('class', 'node')
      .attr('r', d => d.size)
      .attr('fill', d => d.color)
      .attr('stroke', '#fff')
      .attr('stroke-width', d => d.data.extraordinary_score > 0.8 ? 4 : 2)
      .style('cursor', 'pointer')
      .call(d3.drag<SVGCircleElement, GraphNode>()
        .on('start', dragstarted)
        .on('drag', dragged)
        .on('end', dragended) as any)

    // Add labels
    const labels = g.append('g')
      .selectAll('text')
      .data(data.nodes)
      .enter().append('text')
      .attr('class', 'node-label')
      .attr('dy', d => d.size + 15)
      .attr('text-anchor', 'middle')
      .style('font-size', '12px')
      .style('font-weight', d => d.data.extraordinary_score > 0.8 ? 'bold' : 'normal')
      .text(d => d.label)

    // Add event listeners
    node
      .on('click', (event, d) => {
        event.stopPropagation()
        onNodeClick(d.id)
      })
      .on('mouseover', (event, d) => {
        const [x, y] = d3.pointer(event, svg.node())
        setTooltip({
          x,
          y,
          content: `${d.label}\nIndustry: ${d.data.industry}\nMarket Cap: $${d.data.market_cap ? (d.data.market_cap / 1e9).toFixed(1) + 'B' : 'N/A'}`
        })
      })
      .on('mouseout', () => {
        setTooltip(null)
      })

    link
      .on('mouseover', (event, d) => {
        const [x, y] = d3.pointer(event, svg.node())
        setTooltip({
          x,
          y,
          content: `${d.label}\nValue: $${d.data.deal_value ? (d.data.deal_value / 1e9).toFixed(1) + 'B' : 'N/A'}\nConfidence: ${d.data.confidence_score ? (d.data.confidence_score * 100).toFixed(0) + '%' : 'N/A'}`
        })
      })
      .on('mouseout', () => {
        setTooltip(null)
      })

    // Update positions on simulation tick
    simulation.on('tick', () => {
      link
        .attr('x1', (d: any) => d.source.x)
        .attr('y1', (d: any) => d.source.y)
        .attr('x2', (d: any) => d.target.x)
        .attr('y2', (d: any) => d.target.y)

      node
        .attr('cx', (d: any) => d.x)
        .attr('cy', (d: any) => d.y)

      labels
        .attr('x', (d: any) => d.x)
        .attr('y', (d: any) => d.y)
    })

    function dragstarted(event: any, d: any) {
      if (!event.active) simulation.alphaTarget(0.3).restart()
      d.fx = d.x
      d.fy = d.y
    }

    function dragged(event: any, d: any) {
      d.fx = event.x
      d.fy = event.y
    }

    function dragended(event: any, d: any) {
      if (!event.active) simulation.alphaTarget(0)
      d.fx = null
      d.fy = null
    }

    return () => {
      simulation.stop()
    }
  }, [data, showPredictions, onNodeClick])

  return (
    <div className="relative w-full h-full">
      <svg
        ref={svgRef}
        className="w-full h-full"
        style={{ background: '#fafafa' }}
      />
      
      {tooltip && (
        <div
          className="tooltip"
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

      {/* Legend */}
      <div className="graph-legend">
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
            <div className="w-4 h-4 rounded-full bg-red-500"></div>
            <span>Social Media</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-0.5 bg-gray-600"></div>
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
