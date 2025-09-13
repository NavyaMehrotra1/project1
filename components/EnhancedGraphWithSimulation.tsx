'use client';

import React, { useState, useEffect } from 'react';
import ExtraordinaryGraphVisualization from './ExtraordinaryGraphVisualization';
import ImpactSimulationPanel from './ImpactSimulationPanel';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { 
  Zap, 
  RotateCcw, 
  Eye, 
  EyeOff,
  Activity,
  AlertTriangle
} from 'lucide-react';

interface GraphData {
  nodes: any[];
  edges: any[];
  simulation?: {
    scenario: string;
    applied_at: string;
    confidence: number;
    timeline: string;
    market_impact: any;
    reasoning: string;
  };
}

interface SimulationResult {
  scenario: string;
  primary_companies: string[];
  affected_companies: any[];
  new_connections: any[];
  market_impact: any;
  timeline: string;
  confidence: number;
  reasoning: string;
  created_at: string;
}

export default function EnhancedGraphWithSimulation() {
  const [originalGraph, setOriginalGraph] = useState<GraphData | null>(null);
  const [currentGraph, setCurrentGraph] = useState<GraphData | null>(null);
  const [simulationActive, setSimulationActive] = useState(false);
  const [simulationResult, setSimulationResult] = useState<SimulationResult | null>(null);
  const [showSimulationPanel, setShowSimulationPanel] = useState(true);
  const [loading, setLoading] = useState(false);

  // Load initial graph data
  useEffect(() => {
    loadGraphData();
  }, []);

  const loadGraphData = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/graph-data');
      if (response.ok) {
        const data = await response.json();
        setOriginalGraph(data);
        setCurrentGraph(data);
      }
    } catch (error) {
      console.error('Error loading graph data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSimulationComplete = (result: SimulationResult, updatedGraph: GraphData) => {
    setSimulationResult(result);
    setCurrentGraph(updatedGraph);
    setSimulationActive(true);
  };

  const resetToOriginal = () => {
    setCurrentGraph(originalGraph);
    setSimulationActive(false);
    setSimulationResult(null);
  };

  const toggleSimulationPanel = () => {
    setShowSimulationPanel(!showSimulationPanel);
  };

  const getSimulationStats = () => {
    if (!simulationResult) return null;

    const positiveImpacts = simulationResult.affected_companies.filter(c => c.impact_type === 'positive').length;
    const negativeImpacts = simulationResult.affected_companies.filter(c => c.impact_type === 'negative').length;
    const newConnections = simulationResult.new_connections.length;

    return {
      positiveImpacts,
      negativeImpacts,
      newConnections,
      totalAffected: simulationResult.affected_companies.length
    };
  };

  const stats = getSimulationStats();

  return (
    <div className="space-y-6">
      {/* Header with Controls */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center gap-2">
              <Activity className="h-5 w-5" />
              Interactive Impact Simulation
            </CardTitle>
            <div className="flex items-center gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={toggleSimulationPanel}
              >
                {showSimulationPanel ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                {showSimulationPanel ? 'Hide' : 'Show'} Simulation Panel
              </Button>
              {simulationActive && (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={resetToOriginal}
                >
                  <RotateCcw className="h-4 w-4 mr-2" />
                  Reset Graph
                </Button>
              )}
            </div>
          </div>
        </CardHeader>
        
        {/* Simulation Status */}
        {simulationActive && simulationResult && (
          <CardContent>
            <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
              <div className="flex items-start justify-between mb-2">
                <div className="flex items-center gap-2">
                  <Zap className="h-5 w-5 text-blue-600" />
                  <span className="font-semibold text-blue-900">Active Simulation</span>
                  <Badge variant="outline" className="bg-white">
                    {Math.round(simulationResult.confidence * 100)}% confidence
                  </Badge>
                </div>
                <Badge variant="outline" className="bg-white">
                  {simulationResult.timeline}
                </Badge>
              </div>
              
              <p className="text-blue-800 text-sm mb-3">{simulationResult.scenario}</p>
              
              {stats && (
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                  <div className="text-center">
                    <div className="text-lg font-bold text-green-600">{stats.positiveImpacts}</div>
                    <div className="text-gray-600">Positive Impacts</div>
                  </div>
                  <div className="text-center">
                    <div className="text-lg font-bold text-red-600">{stats.negativeImpacts}</div>
                    <div className="text-gray-600">Negative Impacts</div>
                  </div>
                  <div className="text-center">
                    <div className="text-lg font-bold text-purple-600">{stats.newConnections}</div>
                    <div className="text-gray-600">New Connections</div>
                  </div>
                  <div className="text-center">
                    <div className="text-lg font-bold text-blue-600">{stats.totalAffected}</div>
                    <div className="text-gray-600">Total Affected</div>
                  </div>
                </div>
              )}
            </div>
          </CardContent>
        )}
      </Card>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Simulation Panel */}
        {showSimulationPanel && (
          <div className="lg:col-span-1">
            <ImpactSimulationPanel
              onSimulationComplete={handleSimulationComplete}
            />
          </div>
        )}

        {/* Graph Visualization */}
        <div className={showSimulationPanel ? "lg:col-span-2" : "lg:col-span-3"}>
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle>
                  {simulationActive ? 'Simulated Network' : 'Current Network'}
                </CardTitle>
                {simulationActive && (
                  <div className="flex items-center gap-2 text-orange-600">
                    <AlertTriangle className="h-4 w-4" />
                    <span className="text-sm font-medium">Simulation Active</span>
                  </div>
                )}
              </div>
            </CardHeader>
            <CardContent>
              {loading ? (
                <div className="flex items-center justify-center h-96">
                  <div className="text-center">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
                    <p>Loading graph data...</p>
                  </div>
                </div>
              ) : (
                <ExtraordinaryGraphVisualization
                  data={currentGraph}
                  width={showSimulationPanel ? 800 : 1200}
                  height={600}
                />
              )}
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Simulation Legend */}
      {simulationActive && (
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between text-sm">
              <div className="flex items-center gap-4">
                <div className="flex items-center gap-2">
                  <div className="w-4 h-2 bg-red-500 rounded" style={{borderStyle: 'dashed'}}></div>
                  <span>New Simulated Connections</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-4 h-4 rounded-full bg-yellow-500 ring-2 ring-yellow-300"></div>
                  <span>Companies with Changed Scores</span>
                </div>
              </div>
              <div className="text-gray-600">
                Simulation applied at {simulationResult?.created_at ? new Date(simulationResult.created_at).toLocaleTimeString() : 'unknown time'}
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
