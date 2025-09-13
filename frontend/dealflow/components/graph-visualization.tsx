"use client"

import { useEffect, useRef, useState } from "react"
import * as d3 from "d3"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import graphData from "@/data/graph-data.json"

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

const INTERACTION_COLORS = {
  partnership: "#10b981", // green
  acquisition: "#ef4444", // red
  investment: "#3b82f6", // blue
  merger: "#f59e0b", // amber
  collaboration: "#8b5cf6", // purple
  default: "#6b7280", // gray
}

export default function GraphVisualization() {
  const svgRef = useRef<SVGSVGElement>(null)
  const [selectedNode, setSelectedNode] = useState<Node | null>(null)
  const [hoveredEdge, setHoveredEdge] = useState<Edge | null>(null)

  useEffect(() => {
    if (!svgRef.current) return

    const svg = d3.select(svgRef.current)
    svg.selectAll("*").remove()

    const width = 1200
    const height = 800
    const margin = { top: 20, right: 20, bottom: 20, left: 20 }

    svg.attr("width", width).attr("height", height)

    const g = svg.append("g")

    // Add zoom behavior
    const zoom = d3
      .zoom<SVGSVGElement, unknown>()
      .scaleExtent([0.1, 4])
      .on("zoom", (event) => {
        g.attr("transform", event.transform)
      })

    svg.call(zoom)

    // Process data
    const nodes: Node[] = graphData.nodes.map((node) => ({
      ...node,
      x: Math.random() * width,
      y: Math.random() * height,
    }))

    const edges: Edge[] = graphData.edges.map((edge) => ({
      ...edge,
      source: edge.source,
      target: edge.target,
    }))

    // Create force simulation
    const simulation = d3
      .forceSimulation<Node>(nodes)
      .force(
        "link",
        d3
          .forceLink<Node, Edge>(edges)
          .id((d) => d.id)
          .distance((d) => 100 + d.weight * 20)
          .strength(0.1),
      )
      .force("charge", d3.forceManyBody().strength(-300))
      .force("center", d3.forceCenter(width / 2, height / 2))
      .force(
        "collision",
        d3.forceCollide().radius((d) => d.size / 2 + 10),
      )

    // Create arrow markers for directed edges
    const defs = g.append("defs")

    Object.entries(INTERACTION_COLORS).forEach(([type, color]) => {
      defs
        .append("marker")
        .attr("id", `arrow-${type}`)
        .attr("viewBox", "0 -5 10 10")
        .attr("refX", 15)
        .attr("refY", 0)
        .attr("markerWidth", 6)
        .attr("markerHeight", 6)
        .attr("orient", "auto")
        .append("path")
        .attr("d", "M0,-5L10,0L0,5")
        .attr("fill", color)
    })

    // Create edges
    const link = g
      .append("g")
      .attr("class", "links")
      .selectAll("line")
      .data(edges)
      .enter()
      .append("line")
      .attr("stroke", (d) => d.color)
      .attr("stroke-width", (d) => Math.sqrt(d.weight) * 2)
      .attr("stroke-opacity", 0.6)
      .attr("marker-end", (d) => {
        const dealType = d.data.deal_type
        return `url(#arrow-${INTERACTION_COLORS[dealType as keyof typeof INTERACTION_COLORS] ? dealType : "default"})`
      })
      .on("mouseover", function (event, d) {
        setHoveredEdge(d)
        d3.select(this)
          .attr("stroke-opacity", 1)
          .attr("stroke-width", Math.sqrt(d.weight) * 3)
      })
      .on("mouseout", function (event, d) {
        setHoveredEdge(null)
        d3.select(this)
          .attr("stroke-opacity", 0.6)
          .attr("stroke-width", Math.sqrt(d.weight) * 2)
      })

    // Create nodes
    const node = g
      .append("g")
      .attr("class", "nodes")
      .selectAll("circle")
      .data(nodes)
      .enter()
      .append("circle")
      .attr("r", (d) => d.size / 4)
      .attr("fill", (d) => d.color)
      .attr("stroke", "#fff")
      .attr("stroke-width", 2)
      .style("cursor", "pointer")
      .on("click", (event, d) => {
        setSelectedNode(d)
      })
      .on("mouseover", function (event, d) {
        d3.select(this).attr("stroke-width", 4)
      })
      .on("mouseout", function (event, d) {
        d3.select(this).attr("stroke-width", 2)
      })
      .call(
        d3
          .drag<SVGCircleElement, Node>()
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
          }),
      )

    // Add labels
    const labels = g
      .append("g")
      .attr("class", "labels")
      .selectAll("text")
      .data(nodes)
      .enter()
      .append("text")
      .text((d) => d.label)
      .attr("font-size", "12px")
      .attr("font-family", "sans-serif")
      .attr("fill", "#333")
      .attr("text-anchor", "middle")
      .attr("dy", ".35em")
      .style("pointer-events", "none")

    // Update positions on simulation tick
    simulation.on("tick", () => {
      link
        .attr("x1", (d) => (d.source as Node).x!)
        .attr("y1", (d) => (d.source as Node).y!)
        .attr("x2", (d) => (d.target as Node).x!)
        .attr("y2", (d) => (d.target as Node).y!)

      node.attr("cx", (d) => d.x!).attr("cy", (d) => d.y!)

      labels.attr("x", (d) => d.x!).attr("y", (d) => d.y! + d.size / 4 + 15)
    })
  }, [])

  const formatCurrency = (value: number) => {
    if (value >= 1e9) return `$${(value / 1e9).toFixed(1)}B`
    if (value >= 1e6) return `$${(value / 1e6).toFixed(1)}M`
    return `$${value.toLocaleString()}`
  }

  return (
    <div className="flex gap-6 h-screen p-4">
      <div className="w-[70%]">
        <Card className="h-full">
          <CardHeader>
            <CardTitle>Network Graph</CardTitle>
            <div className="flex flex-wrap gap-2">
              {Object.entries(INTERACTION_COLORS).map(([type, color]) => (
                <Badge key={type} variant="outline" className="text-xs">
                  <div className="w-3 h-3 rounded-full mr-2" style={{ backgroundColor: color }} />
                  {type}
                </Badge>
              ))}
            </div>
          </CardHeader>
          <CardContent className="h-[calc(100%-120px)]">
            <svg ref={svgRef} className="border rounded-lg bg-white w-full h-full" />
          </CardContent>
        </Card>
      </div>

      <div className="w-[30%] space-y-4 overflow-y-auto">
        {selectedNode && (
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">{selectedNode.data.name}</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div>
                <Badge variant="secondary">{selectedNode.data.industry}</Badge>
                <Badge variant="outline" className="ml-2">
                  {selectedNode.data.batch}
                </Badge>
              </div>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Status:</span>
                  <span className="font-medium">{selectedNode.data.status}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Valuation:</span>
                  <span className="font-medium">{formatCurrency(selectedNode.data.valuation)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Deal Activity:</span>
                  <span className="font-medium">{selectedNode.data.deal_activity_count}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Score:</span>
                  <span className="font-medium">{selectedNode.data.extraordinary_score}</span>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {hoveredEdge && (
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Relationship Details</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div>
                <Badge style={{ backgroundColor: hoveredEdge.color, color: "white" }}>
                  {hoveredEdge.data.deal_type}
                </Badge>
              </div>
              <div className="space-y-2 text-sm">
                <div>
                  <span className="text-muted-foreground">Date:</span>
                  <span className="ml-2 font-medium">{new Date(hoveredEdge.data.deal_date).toLocaleDateString()}</span>
                </div>
                {hoveredEdge.data.deal_value && (
                  <div>
                    <span className="text-muted-foreground">Value:</span>
                    <span className="ml-2 font-medium">{formatCurrency(hoveredEdge.data.deal_value)}</span>
                  </div>
                )}
                <div>
                  <span className="text-muted-foreground">Confidence:</span>
                  <span className="ml-2 font-medium">{(hoveredEdge.data.confidence_score * 100).toFixed(1)}%</span>
                </div>
                <div className="pt-2">
                  <p className="text-xs text-muted-foreground">{hoveredEdge.data.description}</p>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Instructions</CardTitle>
          </CardHeader>
          <CardContent className="text-sm space-y-2">
            <p>• Click nodes to view company details</p>
            <p>• Hover over edges to see relationship info</p>
            <p>• Drag nodes to reposition them</p>
            <p>• Use mouse wheel to zoom in/out</p>
            <p>• Drag background to pan around</p>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
