'use client';

import React, { useEffect, useRef, useState } from 'react';
import * as d3 from 'd3';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Button } from './ui/button';
import { 
  Crown, 
  Trophy, 
  Star, 
  TrendingUp, 
  Filter,
  ZoomIn,
  ZoomOut,
  RotateCcw,
  ExternalLink
} from 'lucide-react';

interface Node {
  id: string;
  label: string;
  size: number;
  color: string;
  data: {
    name: string;
    industry?: string;
    batch?: string;
    status?: string;
    valuation?: number;
    extraordinary_score?: number;
    logo_url?: string;
    deal_activity_count?: number;
  };
}

interface Edge {
  source: string;
  target: string;
  type: string;
  weight?: number;
}

interface GraphData {
  nodes: Node[];
  edges: Edge[];
}

interface ExtraordinaryGraphVisualizationProps {
  data?: GraphData;
  width?: number;
  height?: number;
  onNodeClick?: (node: Node) => void;
}

export default function ExtraordinaryGraphVisualization({
  data,
  width = 1200,
  height = 800,
  onNodeClick
}: ExtraordinaryGraphVisualizationProps) {
  const svgRef = useRef<SVGSVGElement>(null);
  const [graphData, setGraphData] = useState<GraphData | null>(null);
  const [loading, setLoading] = useState(false);
  const [filter, setFilter] = useState<'all' | 'exceptional' | 'high' | 'medium'>('all');
  const [zoomLevel, setZoomLevel] = useState(1);

  // Load graph data
  useEffect(() => {
    if (data) {
      setGraphData(data);
    } else {
      loadGraphData();
    }
  }, [data]);

  const loadGraphData = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/graph-data');
      if (response.ok) {
        const data = await response.json();
        setGraphData(data);
      }
    } catch (error) {
      console.error('Error loading graph data:', error);
    } finally {
      setLoading(false);
    }
  };

  // Filter nodes based on extraordinary score
  const getFilteredNodes = (nodes: Node[]) => {
    if (filter === 'all') return nodes;
    
    return nodes.filter(node => {
      const score = node.data.extraordinary_score || 0;
      if (filter === 'exceptional') return score >= 80;
      if (filter === 'high') return score >= 60 && score < 80;
      if (filter === 'medium') return score >= 40 && score < 60;
      return true;
    });
  };

  // Get score-based styling
  const getScoreColor = (score: number) => {
    if (score >= 80) return '#ffd700'; // Gold
    if (score >= 60) return '#ff6b6b'; // Red
    if (score >= 40) return '#4ecdc4'; // Teal
    return '#95a5a6'; // Gray
  };

  const getScoreIcon = (score: number) => {
    if (score >= 80) return '👑';
    if (score >= 60) return '🏆';
    if (score >= 40) return '⭐';
    return '📊';
  };

  // Create D3 visualization
  useEffect(() => {
    if (!graphData || !svgRef.current) return;

    const svg = d3.select(svgRef.current);
    svg.selectAll('*').remove();

    const filteredNodes = getFilteredNodes(graphData.nodes);
    const filteredEdges = graphData.edges.filter(edge => 
      filteredNodes.some(n => n.id === edge.source) && 
      filteredNodes.some(n => n.id === edge.target)
    );

    // Create zoom behavior
    const zoom = d3.zoom()
      .scaleExtent([0.1, 4])
      .on('zoom', (event) => {
        container.attr('transform', event.transform);
        setZoomLevel(event.transform.k);
      });

    svg.call(zoom);

    const container = svg.append('g');

    // Create simulation
    const simulation = d3.forceSimulation(filteredNodes)
      .force('link', d3.forceLink(filteredEdges).id((d: any) => d.id).distance(100))
      .force('charge', d3.forceManyBody().strength(-300))
      .force('center', d3.forceCenter(width / 2, height / 2))
      .force('collision', d3.forceCollide().radius(40));

    // Create edges
    const links = container.append('g')
      .selectAll('line')
      .data(filteredEdges)
      .enter()
      .append('line')
      .attr('stroke', '#999')
      .attr('stroke-opacity', 0.6)
      .attr('stroke-width', 2);

    // Create node groups
    const nodeGroups = container.append('g')
      .selectAll('g')
      .data(filteredNodes)
      .enter()
      .append('g')
      .attr('class', 'node-group')
      .style('cursor', 'pointer')
      .call(d3.drag()
        .on('start', (event, d: any) => {
          if (!event.active) simulation.alphaTarget(0.3).restart();
          d.fx = d.x;
          d.fy = d.y;
        })
        .on('drag', (event, d: any) => {
          d.fx = event.x;
          d.fy = event.y;
        })
        .on('end', (event, d: any) => {
          if (!event.active) simulation.alphaTarget(0);
          d.fx = null;
          d.fy = null;
        }));

    // Add node circles with extraordinary score colors
    nodeGroups.append('circle')
      .attr('r', (d: any) => Math.max(20, (d.data.extraordinary_score || 20) / 2))
      .attr('fill', (d: any) => getScoreColor(d.data.extraordinary_score || 0))
      .attr('stroke', '#fff')
      .attr('stroke-width', 3)
      .style('filter', (d: any) => {
        const score = d.data.extraordinary_score || 0;
        if (score >= 80) return 'drop-shadow(0 0 10px #ffd700)';
        if (score >= 60) return 'drop-shadow(0 0 8px #ff6b6b)';
        return 'none';
      });

    // Add company logos
    nodeGroups.append('image')
      .attr('href', (d: any) => d.data.logo_url || '')
      .attr('x', (d: any) => -(Math.max(16, (d.data.extraordinary_score || 20) / 3)))
      .attr('y', (d: any) => -(Math.max(16, (d.data.extraordinary_score || 20) / 3)))
      .attr('width', (d: any) => Math.max(32, (d.data.extraordinary_score || 20) / 1.5))
      .attr('height', (d: any) => Math.max(32, (d.data.extraordinary_score || 20) / 1.5))
      .style('border-radius', '50%')
      .on('error', function() {
        // Fallback if logo fails to load
        d3.select(this).remove();
      });

    // Add company names
    nodeGroups.append('text')
      .text((d: any) => d.data.name)
      .attr('text-anchor', 'middle')
      .attr('dy', (d: any) => Math.max(35, (d.data.extraordinary_score || 20) / 2) + 15)
      .attr('font-size', '12px')
      .attr('font-weight', 'bold')
      .attr('fill', '#333')
      .style('pointer-events', 'none');

    // Add extraordinary score badges
    nodeGroups.append('text')
      .text((d: any) => {
        const score = d.data.extraordinary_score || 0;
        return score > 0 ? `${getScoreIcon(score)} ${score}` : '';
      })
      .attr('text-anchor', 'middle')
      .attr('dy', (d: any) => -(Math.max(25, (d.data.extraordinary_score || 20) / 2) + 5))
      .attr('font-size', '10px')
      .attr('font-weight', 'bold')
      .attr('fill', '#fff')
      .attr('stroke', '#000')
      .attr('stroke-width', 0.5)
      .style('pointer-events', 'none');

    // Add click handlers
    nodeGroups.on('click', (event, d: any) => {
      if (onNodeClick) {
        onNodeClick(d);
      } else {
        // Default behavior - open extraordinary profile
        window.open(`/extraordinary/${encodeURIComponent(d.data.name)}`, '_blank');
      }
    });

    // Add hover effects
    nodeGroups.on('mouseover', function(event, d: any) {
      d3.select(this).select('circle')
        .transition()
        .duration(200)
        .attr('r', (d: any) => Math.max(25, (d.data.extraordinary_score || 20) / 2) + 5);
      
      // Show tooltip
      const tooltip = d3.select('body').append('div')
        .attr('class', 'graph-tooltip')
        .style('position', 'absolute')
        .style('background', 'rgba(0, 0, 0, 0.8)')
        .style('color', 'white')
        .style('padding', '8px')
        .style('border-radius', '4px')
        .style('font-size', '12px')
        .style('pointer-events', 'none')
        .style('z-index', 1000)
        .html(`
          <strong>${d.data.name}</strong><br/>
          Industry: ${d.data.industry || 'N/A'}<br/>
          Extraordinary Score: ${d.data.extraordinary_score || 0}/100<br/>
          Batch: ${d.data.batch || 'N/A'}
        `)
        .style('left', (event.pageX + 10) + 'px')
        .style('top', (event.pageY - 10) + 'px');
    })
    .on('mouseout', function(event, d: any) {
      d3.select(this).select('circle')
        .transition()
        .duration(200)
        .attr('r', (d: any) => Math.max(20, (d.data.extraordinary_score || 20) / 2));
      
      // Remove tooltip
      d3.selectAll('.graph-tooltip').remove();
    });

    // Update positions on simulation tick
    simulation.on('tick', () => {
      links
        .attr('x1', (d: any) => d.source.x)
        .attr('y1', (d: any) => d.source.y)
        .attr('x2', (d: any) => d.target.x)
        .attr('y2', (d: any) => d.target.y);

      nodeGroups
        .attr('transform', (d: any) => `translate(${d.x},${d.y})`);
    });

    return () => {
      simulation.stop();
    };
  }, [graphData, filter, width, height, onNodeClick]);

  const handleZoomIn = () => {
    const svg = d3.select(svgRef.current);
    svg.transition().call(
      d3.zoom().scaleBy as any, 1.5
    );
  };

  const handleZoomOut = () => {
    const svg = d3.select(svgRef.current);
    svg.transition().call(
      d3.zoom().scaleBy as any, 0.67
    );
  };

  const handleReset = () => {
    const svg = d3.select(svgRef.current);
    svg.transition().call(
      d3.zoom().transform as any,
      d3.zoomIdentity
    );
  };

  if (loading) {
    return (
      <Card>
        <CardContent className="p-6">
          <div className="flex items-center justify-center h-96">
            <div className="text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
              <p>Loading extraordinary graph visualization...</p>
            </div>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (!graphData) {
    return (
      <Card>
        <CardContent className="p-6">
          <div className="text-center">
            <p className="text-gray-600">No graph data available</p>
            <Button onClick={loadGraphData} className="mt-4">
              Reload Graph Data
            </Button>
          </div>
        </CardContent>
      </Card>
    );
  }

  const filteredNodes = getFilteredNodes(graphData.nodes);
  const totalNodes = graphData.nodes.length;

  return (
    <div className="space-y-4">
      {/* Controls */}
      <Card>
        <CardContent className="p-4">
          <div className="flex items-center justify-between flex-wrap gap-4">
            {/* Filters */}
            <div className="flex items-center gap-2">
              <Filter className="h-4 w-4 text-gray-600" />
              <span className="text-sm font-medium">Filter by score:</span>
              <Button
                variant={filter === 'all' ? 'default' : 'outline'}
                size="sm"
                onClick={() => setFilter('all')}
              >
                All ({totalNodes})
              </Button>
              <Button
                variant={filter === 'exceptional' ? 'default' : 'outline'}
                size="sm"
                onClick={() => setFilter('exceptional')}
                className="bg-yellow-100 text-yellow-800 hover:bg-yellow-200"
              >
                <Crown className="h-3 w-3 mr-1" />
                Exceptional (80+)
              </Button>
              <Button
                variant={filter === 'high' ? 'default' : 'outline'}
                size="sm"
                onClick={() => setFilter('high')}
                className="bg-red-100 text-red-800 hover:bg-red-200"
              >
                <Trophy className="h-3 w-3 mr-1" />
                High (60-79)
              </Button>
              <Button
                variant={filter === 'medium' ? 'default' : 'outline'}
                size="sm"
                onClick={() => setFilter('medium')}
                className="bg-blue-100 text-blue-800 hover:bg-blue-200"
              >
                <Star className="h-3 w-3 mr-1" />
                Medium (40-59)
              </Button>
            </div>

            {/* Zoom Controls */}
            <div className="flex items-center gap-2">
              <span className="text-sm text-gray-600">Zoom: {Math.round(zoomLevel * 100)}%</span>
              <Button variant="outline" size="sm" onClick={handleZoomIn}>
                <ZoomIn className="h-4 w-4" />
              </Button>
              <Button variant="outline" size="sm" onClick={handleZoomOut}>
                <ZoomOut className="h-4 w-4" />
              </Button>
              <Button variant="outline" size="sm" onClick={handleReset}>
                <RotateCcw className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Graph */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <TrendingUp className="h-5 w-5" />
            Extraordinary Companies Network
            <Badge variant="outline">
              Showing {filteredNodes.length} of {totalNodes} companies
            </Badge>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="relative">
            <svg
              ref={svgRef}
              width={width}
              height={height}
              className="border border-gray-200 rounded-lg bg-gray-50"
            />
            
            {/* Legend */}
            <div className="absolute top-4 right-4 bg-white p-3 rounded-lg shadow-lg border">
              <h4 className="font-semibold text-sm mb-2">Extraordinary Score Legend</h4>
              <div className="space-y-1 text-xs">
                <div className="flex items-center gap-2">
                  <div className="w-4 h-4 rounded-full bg-yellow-500"></div>
                  <span>👑 Exceptional (80+)</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-4 h-4 rounded-full bg-red-500"></div>
                  <span>🏆 High (60-79)</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-4 h-4 rounded-full bg-teal-500"></div>
                  <span>⭐ Medium (40-59)</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-4 h-4 rounded-full bg-gray-400"></div>
                  <span>📊 Standard (&lt;40)</span>
                </div>
              </div>
              <div className="mt-2 pt-2 border-t text-xs text-gray-600">
                Click any company to view extraordinary profile
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
