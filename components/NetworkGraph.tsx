'use client'

import { useEffect, useRef, useState } from 'react'
import * as d3 from 'd3'
import { dataService, CompanyNode, CompanyLink, GraphData } from '../services/data-service'
import { EnhancedCompanyProfile } from './EnhancedCompanyProfile'

interface NetworkGraphProps {
  onNodeClick?: (nodeId: string) => void
  showEnhancedData?: boolean
}

export function NetworkGraph({ onNodeClick, showEnhancedData = true }: NetworkGraphProps) {
  const svgRef = useRef<SVGSVGElement>(null)
  const [tooltip, setTooltip] = useState<{ x: number; y: number; content: string } | null>(null)
  const [data, setData] = useState<GraphData | null>(null)
  const [loading, setLoading] = useState(true)
  const [selectedCompany, setSelectedCompany] = useState<string | null>(null)

  // Load data on component mount
  useEffect(() => {
    const loadData = async () => {
      setLoading(true)
      try {
        const graphData = showEnhancedData 
          ? await dataService.getEnhancedGraphData()
          : await dataService.getGraphData()
        setData(graphData)
      } catch (error) {
        console.error('Error loading graph data:', error)
      } finally {
        setLoading(false)
      }
    }

    loadData()
  }, [showEnhancedData])

  // D3 visualization effect
  useEffect(() => {
    if (!data || !svgRef.current || loading) return

    const svg = d3.select(svgRef.current)
    svg.selectAll('*').remove()

    const width = svgRef.current.clientWidth
    const height = svgRef.current.clientHeight

    // Create simulation
    const simulation = d3.forceSimulation(data.nodes as any)
      .force('link', d3.forceLink(data.links).id((d: any) => d.id).distance(150))
      .force('charge', d3.forceManyBody().strength(-300))
      .force('center', d3.forceCenter(width / 2, height / 2))
      .force('collision', d3.forceCollide().radius(40))

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
      .data(data.links)
      .enter().append('line')
      .attr('class', 'link')
      .attr('stroke', (d: CompanyLink) => {
        const colors = {
          'partnership': '#4a9eff',
          'acquisition': '#ff6b35',
          'investment': '#00ff88',
          'competitor': '#e74c3c',
          'similar': '#95a5a6'
        }
        return colors[d.type] || '#95a5a6'
      })
      .attr('stroke-width', (d: CompanyLink) => Math.max(1, d.strength * 3))
      .attr('stroke-opacity', 0.6)

    // Create nodes
    const node = g.append('g')
      .selectAll('circle')
      .data(data.nodes)
      .enter().append('circle')
      .attr('class', 'node')
      .attr('r', (d: CompanyNode) => dataService.getFundingStageSize(d.funding_stage || 'Unknown'))
      .attr('fill', (d: CompanyNode) => dataService.getCategoryColor(d.category || 'Other'))
      .attr('stroke', '#fff')
      .attr('stroke-width', (d: CompanyNode) => d.exa_insights ? 3 : 2)
      .style('cursor', 'pointer')
      .call(d3.drag<SVGCircleElement, CompanyNode>()
        .on('start', dragstarted)
        .on('drag', dragged)
        .on('end', dragended) as any)

    // Add labels
    const labels = g.append('g')
      .selectAll('text')
      .data(data.nodes)
      .enter().append('text')
      .attr('class', 'node-label')
      .attr('dy', (d: CompanyNode) => dataService.getFundingStageSize(d.funding_stage || 'Unknown') + 15)
      .attr('text-anchor', 'middle')
      .style('font-size', '12px')
      .style('font-weight', (d: CompanyNode) => d.exa_insights ? 'bold' : 'normal')
      .style('fill', '#fff')
      .text((d: CompanyNode) => d.name)

    // Add event listeners
    node
      .on('click', (event, d: CompanyNode) => {
        event.stopPropagation()
        setSelectedCompany(d.name)
        onNodeClick?.(d.id)
      })
      .on('mouseover', (event, d: CompanyNode) => {
        const [x, y] = d3.pointer(event, svg.node())
        setTooltip({
          x,
          y,
          content: `${d.name}\nCategory: ${d.category || 'Unknown'}\nBatch: ${d.batch || 'N/A'}\nLocation: ${d.location || 'N/A'}`
        })
      })
      .on('mouseout', () => {
        setTooltip(null)
      })

    link
      .on('mouseover', (event, d: CompanyLink) => {
        const [x, y] = d3.pointer(event, svg.node())
        setTooltip({
          x,
          y,
          content: `Connection: ${d.type}\nStrength: ${(d.strength * 100).toFixed(0)}%`
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
  }, [data, loading, onNodeClick])

  if (loading) {
    return (
      <div className="flex items-center justify-center w-full h-full">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-[#00ff88] mx-auto mb-4"></div>
          <p className="text-gray-400">Loading company network...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="relative w-full h-full">
      <svg
        ref={svgRef}
        className="w-full h-full"
        style={{ background: 'transparent' }}
      />
      
      {tooltip && (
        <div
          className="absolute bg-black bg-opacity-90 text-white p-2 rounded text-sm pointer-events-none z-10"
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

      {/* Enhanced Company Profile Modal */}
      {selectedCompany && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="max-w-4xl max-h-[90vh] overflow-y-auto">
            <EnhancedCompanyProfile 
              companyName={selectedCompany}
              onClose={() => setSelectedCompany(null)}
            />
          </div>
        </div>
      )}

      {/* Legend */}
      <div className="absolute top-4 right-4 bg-black bg-opacity-80 p-4 rounded-lg text-white">
        <h3 className="font-semibold mb-2 text-[#00ff88]">Legend</h3>
        <div className="space-y-2 text-sm">
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded-full" style={{ backgroundColor: dataService.getCategoryColor('AI/ML') }}></div>
            <span>AI/ML</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded-full" style={{ backgroundColor: dataService.getCategoryColor('Fintech') }}></div>
            <span>Fintech</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded-full" style={{ backgroundColor: dataService.getCategoryColor('Consumer') }}></div>
            <span>Consumer</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded-full" style={{ backgroundColor: dataService.getCategoryColor('SaaS') }}></div>
            <span>SaaS</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-0.5 bg-blue-500"></div>
            <span>Partnership</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-0.5 bg-orange-500"></div>
            <span>Acquisition</span>
          </div>
        </div>
      </div>

      {/* Controls */}
      <div className="absolute bottom-4 left-4 bg-black bg-opacity-80 p-4 rounded-lg text-white">
        <div className="flex flex-col gap-2">
          <button
            onClick={() => window.location.reload()}
            className="px-4 py-2 bg-[#00ff88] text-black rounded hover:bg-[#00dd77] transition-colors"
          >
            Refresh Data
          </button>
          <label className="flex items-center gap-2 text-sm">
            <input
              type="checkbox"
              checked={showEnhancedData}
              onChange={(e) => {
                // This would trigger a re-render with enhanced data
                console.log('Enhanced data toggle:', e.target.checked)
              }}
              className="rounded"
            />
            Show Exa Insights
          </label>
        </div>
      </div>
    </div>
  )
}
