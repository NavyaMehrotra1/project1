"use client"

import { useEffect, useRef, useState } from "react"
import * as d3 from "d3"
import { Search, Filter, Zap, BookOpen, Play, Pause } from "lucide-react"
import dataService from '@/src/api/dataService'

interface Node extends d3.SimulationNodeDatum {
  id: string
  label: string
  size: number
  color: string
  data: {
    name: string
    industry: string
    batch: string
    status: string
    valuation: number
    deal_activity_count: number
    extraordinary_score: number
    logo_url?: string
  }
}

interface Edge {
  id: string
  source: string | Node
  target: string | Node
  label: string
  weight: number
  color: string
  data: {
    deal_type: string
    deal_value: number | null
    deal_date: string
    description: string
    confidence_score: number
  }
}

const SECTOR_COLORS = {
  'Technology': '#3B82F6',
  'Healthcare': '#10B981', 
  'Finance': '#F59E0B',
  'Energy': '#EF4444',
  'Consumer': '#8B5CF6',
  'Industrial': '#6B7280',
  'Real Estate': '#EC4899',
  'Materials': '#84CC16',
  'Utilities': '#06B6D4',
  'Telecommunications': '#F97316',
  'AI/ML': '#3B82F6',
  'Fintech': '#F59E0B'
}

const DEAL_TYPE_COLORS = {
  merger: '#EF4444',
  acquisition: '#EF4444', 
  partnership: '#10B981',
  investment: '#3B82F6',
  ipo: '#8B5CF6',
  collaboration: '#10B981',
  competition: '#F59E0B',
  default: '#6B7280'
}

export default function GraphVisualization() {
  const svgRef = useRef<SVGSVGElement>(null)
  const [selectedNode, setSelectedNode] = useState<Node | null>(null)
  const [hoveredEdge, setHoveredEdge] = useState<Edge | null>(null)
  const [graphData, setGraphData] = useState<{nodes: Node[], edges: Edge[]}>({nodes: [], edges: []})
  const [showPredictions, setShowPredictions] = useState(true)
  const [searchTerm, setSearchTerm] = useState("")
  const [selectedIndustry, setSelectedIndustry] = useState("all")
  const [isSimulating, setIsSimulating] = useState(false)
  const [teachingQuestion, setTeachingQuestion] = useState("")
  const [teachingResponse, setTeachingResponse] = useState("")

  // Load graph data
  useEffect(() => {
    const loadData = async () => {
      try {
        const data = await dataService.fetchGraphData()
        setGraphData(data)
      } catch (error) {
        console.error('Failed to load graph data:', error)
        // Fallback to mock data
        setGraphData({
          nodes: [
            {
              id: "openai",
              label: "OpenAI", 
              size: 80,
              color: SECTOR_COLORS['AI/ML'],
              data: {
                name: "OpenAI",
                industry: "AI/ML",
                batch: "N/A",
                status: "Private",
                valuation: 80000000000,
                deal_activity_count: 15,
                extraordinary_score: 95
              }
            },
            {
              id: "stripe",
              label: "Stripe",
              size: 90, 
              color: SECTOR_COLORS['Fintech'],
              data: {
                name: "Stripe",
                industry: "Fintech",
                batch: "S09",
                status: "Private", 
                valuation: 95000000000,
                deal_activity_count: 12,
                extraordinary_score: 92
              }
            },
            {
              id: "anthropic",
              label: "Anthropic",
              size: 75,
              color: SECTOR_COLORS['AI/ML'],
              data: {
                name: "Anthropic",
                industry: "AI/ML", 
                batch: "N/A",
                status: "Private",
                valuation: 15000000000,
                deal_activity_count: 8,
                extraordinary_score: 88
              }
            }
          ],
          edges: [
            {
              id: "edge1",
              source: "openai",
              target: "stripe", 
              label: "Partnership",
              weight: 5,
              color: DEAL_TYPE_COLORS.partnership,
              data: {
                deal_type: "partnership",
                deal_value: 1000000000,
                deal_date: "2024-01-15",
                description: "Strategic AI integration partnership",
                confidence_score: 0.85
              }
            },
            {
              id: "edge2", 
              source: "anthropic",
              target: "openai",
              label: "Competition",
              weight: 3,
              color: DEAL_TYPE_COLORS.competition,
              data: {
                deal_type: "competition",
                deal_value: null,
                deal_date: "2024-02-01", 
                description: "AI model competition and talent acquisition",
                confidence_score: 0.92
              }
            }
          ]
        })
      }
    }
    loadData()
  }, [])

  // D3 Force Simulation
  useEffect(() => {
    if (!svgRef.current || graphData.nodes.length === 0) return

    const svg = d3.select(svgRef.current)
    const width = 800
    const height = 600

    // Clear previous content
    svg.selectAll("*").remove()

    // Create simulation
    const simulation = d3.forceSimulation(graphData.nodes)
      .force("link", d3.forceLink(graphData.edges).id((d: any) => d.id).distance(100))
      .force("charge", d3.forceManyBody().strength(-300))
      .force("center", d3.forceCenter(width / 2, height / 2))

    // Create links
    const link = svg.append("g")
      .selectAll("line")
      .data(graphData.edges)
      .enter().append("line")
      .attr("stroke", d => d.color)
      .attr("stroke-width", d => Math.sqrt(d.weight))
      .attr("stroke-opacity", 0.6)

    // Create nodes
    const node = svg.append("g")
      .selectAll("circle")
      .data(graphData.nodes)
      .enter().append("circle")
      .attr("r", d => d.size / 4)
      .attr("fill", d => d.color)
      .attr("stroke", "#fff")
      .attr("stroke-width", 2)
      .style("cursor", "pointer")
      .call(d3.drag<SVGCircleElement, Node>()
        .on("start", (event, d) => {
          if (!event.active) simulation.alphaTarget(0.3).restart()
          d.fx = d.x
          d.fy = d.y
        })
        .on("drag", (event, d) => {
          d.fx = event.x
          d.fy = event.y
        })
        .on("end", (event, d) => {
          if (!event.active) simulation.alphaTarget(0)
          d.fx = null
          d.fy = null
        }))

    // Add labels
    const labels = svg.append("g")
      .selectAll("text")
      .data(graphData.nodes)
      .enter().append("text")
      .text(d => d.label)
      .attr("font-size", 12)
      .attr("text-anchor", "middle")
      .attr("dy", d => d.size / 4 + 15)
      .style("pointer-events", "none")

    // Node click handler
    node.on("click", (event, d) => {
      setSelectedNode(d)
    })

    // Update positions on simulation tick
    simulation.on("tick", () => {
      link
        .attr("x1", (d: any) => d.source.x)
        .attr("y1", (d: any) => d.source.y)
        .attr("x2", (d: any) => d.target.x)
        .attr("y2", (d: any) => d.target.y)

      node
        .attr("cx", d => d.x!)
        .attr("cy", d => d.y!)

      labels
        .attr("x", d => d.x!)
        .attr("y", d => d.y!)
    })

  }, [graphData])

  // Handle teaching assistant questions
  const handleTeachingQuestion = async () => {
    if (!teachingQuestion.trim()) return
    
    try {
      const response = await dataService.askTeachingAssistant(teachingQuestion, {
        selectedNode: selectedNode?.data,
        graphContext: graphData
      })
      setTeachingResponse(response)
    } catch (error) {
      console.error('Teaching assistant error:', error)
      setTeachingResponse("Sorry, I couldn't process your question right now.")
    }
  }

  // Handle what-if simulation
  const handleSimulation = async () => {
    if (!selectedNode) return
    
    setIsSimulating(true)
    try {
      const result = await dataService.simulateImpact(
        selectedNode.id,
        "market",
        "acquisition"
      )
      console.log('Simulation result:', result)
    } catch (error) {
      console.error('Simulation error:', error)
    } finally {
      setIsSimulating(false)
    }
  }

  const formatCurrency = (value: number) => {
    if (value >= 1e9) return `$${(value / 1e9).toFixed(1)}B`
    if (value >= 1e6) return `$${(value / 1e6).toFixed(1)}M`
    return `$${value.toLocaleString()}`
  }

  const filteredNodes = graphData.nodes.filter(node => {
    const matchesSearch = node.label.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesIndustry = selectedIndustry === "all" || node.data.industry === selectedIndustry
    return matchesSearch && matchesIndustry
  })

  const industries = Array.from(new Set(graphData.nodes.map(node => node.data.industry)))

  return (
    <div className="flex gap-6 h-screen p-4 bg-gray-50">
      {/* Main Graph Area */}
      <div className="w-[70%]">
        <div className="bg-white rounded-lg shadow-lg h-full">
          {/* Header with Controls */}
          <div className="p-4 border-b">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-bold">M&A Intelligence Network Graph</h2>
              <div className="flex gap-2">
                <button
                  onClick={() => setShowPredictions(!showPredictions)}
                  className={`px-3 py-1 rounded text-sm flex items-center gap-1 ${
                    showPredictions ? 'bg-blue-500 text-white' : 'bg-gray-200'
                  }`}
                >
                  <Zap size={14} />
                  Predictions
                </button>
                <button
                  onClick={handleSimulation}
                  disabled={!selectedNode || isSimulating}
                  className="px-3 py-1 rounded text-sm bg-purple-500 text-white disabled:opacity-50 flex items-center gap-1"
                >
                  {isSimulating ? <Pause size={14} /> : <Play size={14} />}
                  Simulate
                </button>
              </div>
            </div>
            
            {/* Search and Filter */}
            <div className="flex gap-4 mb-4">
              <div className="flex-1 relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={16} />
                <input
                  type="text"
                  placeholder="Search companies..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 border rounded-lg text-sm"
                />
              </div>
              <div className="relative">
                <Filter className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={16} />
                <select
                  value={selectedIndustry}
                  onChange={(e) => setSelectedIndustry(e.target.value)}
                  className="pl-10 pr-8 py-2 border rounded-lg text-sm appearance-none bg-white"
                >
                  <option value="all">All Industries</option>
                  {industries.map(industry => (
                    <option key={industry} value={industry}>{industry}</option>
                  ))}
                </select>
              </div>
            </div>

            {/* Legend */}
            <div className="flex flex-wrap gap-2">
              {Object.entries(DEAL_TYPE_COLORS).map(([type, color]) => (
                <div key={type} className="flex items-center gap-1 text-xs">
                  <div className="w-3 h-3 rounded-full" style={{ backgroundColor: color }} />
                  <span className="capitalize">{type}</span>
                </div>
              ))}
            </div>
          </div>
          
          {/* SVG Graph */}
          <div className="p-4 h-[calc(100%-200px)]">
            <svg
              ref={svgRef}
              width="100%"
              height="100%"
              className="border rounded-lg bg-white"
              viewBox="0 0 800 600"
            />
          </div>
        </div>
      </div>

      <div className="w-[30%] space-y-4 overflow-y-auto">
        {selectedNode && (
          <div className="bg-white rounded-lg shadow-lg p-4">
            <h3 className="text-lg font-bold mb-2">{selectedNode.data.name}</h3>
            <div className="space-y-2">
              <div className="flex gap-2">
                <span className="px-2 py-1 bg-blue-100 text-blue-800 rounded text-xs">
                  {selectedNode.data.industry}
                </span>
                <span className="px-2 py-1 bg-gray-100 text-gray-800 rounded text-xs">
                  {selectedNode.data.batch}
                </span>
              </div>
              <div className="space-y-1 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-600">Status:</span>
                  <span className="font-medium">{selectedNode.data.status}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Valuation:</span>
                  <span className="font-medium">{formatCurrency(selectedNode.data.valuation)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Deal Activity:</span>
                  <span className="font-medium">{selectedNode.data.deal_activity_count}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Score:</span>
                  <span className="font-medium">{selectedNode.data.extraordinary_score}</span>
                </div>
              </div>
            </div>
          </div>
        )}

        {hoveredEdge && (
          <div className="bg-white rounded-lg shadow-lg p-4">
            <h3 className="text-lg font-bold mb-2">Relationship Details</h3>
            <div className="space-y-2">
              <span 
                className="px-2 py-1 rounded text-xs text-white"
                style={{ backgroundColor: hoveredEdge.color }}
              >
                {hoveredEdge.data.deal_type}
              </span>
              <div className="space-y-1 text-sm">
                <div>
                  <span className="text-gray-600">Date:</span>
                  <span className="ml-2 font-medium">
                    {new Date(hoveredEdge.data.deal_date).toLocaleDateString()}
                  </span>
                </div>
                {hoveredEdge.data.deal_value && (
                  <div>
                    <span className="text-gray-600">Value:</span>
                    <span className="ml-2 font-medium">
                      {formatCurrency(hoveredEdge.data.deal_value)}
                    </span>
                  </div>
                )}
                <div>
                  <span className="text-gray-600">Confidence:</span>
                  <span className="ml-2 font-medium">
                    {(hoveredEdge.data.confidence_score * 100).toFixed(1)}%
                  </span>
                </div>
                <div className="pt-2">
                  <p className="text-xs text-gray-600">{hoveredEdge.data.description}</p>
                </div>
              </div>
            </div>
          </div>
        )}

        <div className="bg-white rounded-lg shadow-lg p-4">
          <h3 className="text-lg font-bold mb-2">Instructions</h3>
          <div className="text-sm space-y-1">
            <p>• Click nodes to view company details</p>
            <p>• Hover over edges to see relationship info</p>
            <p>• Data sourced from NewsAPI, Exa, and other APIs</p>
            <p>• Predictions powered by ChromaDB + LLM pipeline</p>
          </div>
        </div>

        {/* Teaching Tool Placeholder */}
        <div className="bg-white rounded-lg shadow-lg p-4">
          <h3 className="text-lg font-bold mb-2">AI Teaching Assistant</h3>
          <div className="text-sm text-gray-600">
            <p>Ask questions about M&A deals, company relationships, or market trends.</p>
            <div className="mt-2 p-2 bg-gray-50 rounded">
              <p className="text-xs">Example: "Explain the OpenAI-Stripe partnership impact"</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}