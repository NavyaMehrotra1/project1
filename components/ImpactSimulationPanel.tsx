'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Button } from './ui/button';
import { 
  Zap, 
  Play, 
  RotateCcw, 
  TrendingUp, 
  TrendingDown, 
  Minus,
  Clock,
  Target,
  Brain,
  Sparkles,
  ChevronDown,
  ChevronUp
} from 'lucide-react';

interface AffectedCompany {
  name: string;
  impact_type: 'positive' | 'negative' | 'neutral';
  impact_score: number;
  reasoning: string;
  new_extraordinary_score: number;
  valuation_change: string;
}

interface NewConnection {
  source: string;
  target: string;
  connection_type: string;
  strength: number;
  description: string;
}

interface MarketImpact {
  sector: string;
  overall_sentiment: string;
  market_cap_change: string;
  innovation_acceleration: boolean;
}

interface SimulationResult {
  scenario: string;
  primary_companies: string[];
  affected_companies: AffectedCompany[];
  new_connections: NewConnection[];
  market_impact: MarketImpact;
  timeline: string;
  confidence: number;
  reasoning: string;
  created_at: string;
}

interface ImpactSimulationPanelProps {
  onSimulationComplete?: (result: SimulationResult, updatedGraph: any) => void;
  availableCompanies?: string[];
}

export default function ImpactSimulationPanel({ 
  onSimulationComplete,
  availableCompanies = []
}: ImpactSimulationPanelProps) {
  const [scenario, setScenario] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<SimulationResult | null>(null);
  const [companies, setCompanies] = useState<any[]>([]);
  const [templates, setTemplates] = useState<string[]>([]);
  const [selectedTemplate, setSelectedTemplate] = useState('');
  const [company1, setCompany1] = useState('');
  const [company2, setCompany2] = useState('');
  const [showDetails, setShowDetails] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Load available companies and templates
  useEffect(() => {
    loadCompanies();
    loadTemplates();
  }, []);

  const loadCompanies = async () => {
    try {
      const response = await fetch('/api/impact-simulation/companies');
      if (response.ok) {
        const data = await response.json();
        setCompanies(data.companies || []);
      }
    } catch (error) {
      console.error('Error loading companies:', error);
    }
  };

  const loadTemplates = async () => {
    try {
      const response = await fetch('/api/impact-simulation/templates');
      if (response.ok) {
        const data = await response.json();
        setTemplates(data.templates || []);
      }
    } catch (error) {
      console.error('Error loading templates:', error);
    }
  };

  const runSimulation = async () => {
    if (!scenario.trim()) {
      setError('Please enter a scenario');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await fetch('/api/impact-simulation/simulate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          scenario: scenario.trim(),
          apply_to_graph: true
        }),
      });

      if (!response.ok) {
        throw new Error(`Simulation failed: ${response.statusText}`);
      }

      const data = await response.json();
      const simulationResult = data.simulation;
      
      setResult(simulationResult);
      setShowDetails(true);

      if (onSimulationComplete) {
        onSimulationComplete(simulationResult, data.updated_graph);
      }

    } catch (err) {
      setError(err instanceof Error ? err.message : 'Simulation failed');
    } finally {
      setLoading(false);
    }
  };

  const runQuickSimulation = async () => {
    if (!selectedTemplate || !company1) {
      setError('Please select a template and at least one company');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await fetch('/api/impact-simulation/quick-simulate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          template: selectedTemplate,
          company1,
          company2: company2 || undefined
        }),
      });

      if (!response.ok) {
        throw new Error(`Quick simulation failed: ${response.statusText}`);
      }

      const data = await response.json();
      const simulationResult = data.simulation;
      
      setResult(simulationResult);
      setScenario(data.scenario);
      setShowDetails(true);

      if (onSimulationComplete) {
        onSimulationComplete(simulationResult, data.updated_graph);
      }

    } catch (err) {
      setError(err instanceof Error ? err.message : 'Quick simulation failed');
    } finally {
      setLoading(false);
    }
  };

  const resetSimulation = () => {
    setResult(null);
    setScenario('');
    setSelectedTemplate('');
    setCompany1('');
    setCompany2('');
    setShowDetails(false);
    setError(null);
  };

  const getImpactIcon = (type: string) => {
    switch (type) {
      case 'positive': return <TrendingUp className="h-4 w-4 text-green-600" />;
      case 'negative': return <TrendingDown className="h-4 w-4 text-red-600" />;
      default: return <Minus className="h-4 w-4 text-gray-600" />;
    }
  };

  const getImpactColor = (type: string) => {
    switch (type) {
      case 'positive': return 'bg-green-50 border-green-200 text-green-800';
      case 'negative': return 'bg-red-50 border-red-200 text-red-800';
      default: return 'bg-gray-50 border-gray-200 text-gray-800';
    }
  };

  return (
    <div className="space-y-4">
      {/* Input Panel */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Zap className="h-5 w-5 text-blue-600" />
            Impact Simulation
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Custom Scenario Input */}
          <div>
            <label className="block text-sm font-medium mb-2">
              Custom Scenario
            </label>
            <div className="flex gap-2">
              <input
                type="text"
                value={scenario}
                onChange={(e) => setScenario(e.target.value)}
                placeholder="e.g., What if OpenAI partners with Epic Games?"
                className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                disabled={loading}
              />
              <Button 
                onClick={runSimulation} 
                disabled={loading || !scenario.trim()}
                className="bg-blue-600 hover:bg-blue-700"
              >
                {loading ? (
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white" />
                ) : (
                  <Play className="h-4 w-4" />
                )}
              </Button>
            </div>
          </div>

          {/* Quick Templates */}
          <div className="border-t pt-4">
            <label className="block text-sm font-medium mb-2">
              Quick Templates
            </label>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-2 mb-2">
              <select
                value={selectedTemplate}
                onChange={(e) => setSelectedTemplate(e.target.value)}
                className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                disabled={loading}
              >
                <option value="">Select template...</option>
                {templates.map((template, index) => (
                  <option key={index} value={template}>
                    {template.replace('{company1}', 'Company1').replace('{company2}', 'Company2')}
                  </option>
                ))}
              </select>
              
              <select
                value={company1}
                onChange={(e) => setCompany1(e.target.value)}
                className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                disabled={loading}
              >
                <option value="">Select Company 1...</option>
                {companies.map((company) => (
                  <option key={company.name} value={company.name}>
                    {company.name} ({company.extraordinary_score}/100)
                  </option>
                ))}
              </select>
              
              <select
                value={company2}
                onChange={(e) => setCompany2(e.target.value)}
                className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                disabled={loading}
              >
                <option value="">Select Company 2 (optional)...</option>
                {companies.filter(c => c.name !== company1).map((company) => (
                  <option key={company.name} value={company.name}>
                    {company.name} ({company.extraordinary_score}/100)
                  </option>
                ))}
              </select>
            </div>
            
            <div className="flex gap-2">
              <Button 
                onClick={runQuickSimulation}
                disabled={loading || !selectedTemplate || !company1}
                variant="outline"
                className="flex-1"
              >
                <Sparkles className="h-4 w-4 mr-2" />
                Quick Simulate
              </Button>
              <Button onClick={resetSimulation} variant="outline">
                <RotateCcw className="h-4 w-4" />
              </Button>
            </div>
          </div>

          {error && (
            <div className="p-3 bg-red-50 border border-red-200 rounded-md text-red-800 text-sm">
              {error}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Results Panel */}
      {result && (
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="flex items-center gap-2">
                <Brain className="h-5 w-5 text-purple-600" />
                Simulation Results
              </CardTitle>
              <Button
                variant="outline"
                size="sm"
                onClick={() => setShowDetails(!showDetails)}
              >
                {showDetails ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
              </Button>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* Scenario & Overview */}
            <div className="p-3 bg-blue-50 border border-blue-200 rounded-md">
              <h4 className="font-semibold text-blue-900 mb-1">Scenario</h4>
              <p className="text-blue-800 text-sm">{result.scenario}</p>
            </div>

            {/* Key Metrics */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="text-center">
                <div className="text-2xl font-bold text-purple-600">{Math.round(result.confidence * 100)}%</div>
                <div className="text-sm text-gray-600">Confidence</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-600">{result.affected_companies.length}</div>
                <div className="text-sm text-gray-600">Companies Affected</div>
              </div>
              <div className="text-center">
                <div className="flex items-center justify-center gap-1">
                  <Clock className="h-4 w-4 text-gray-600" />
                  <span className="text-sm font-medium">{result.timeline}</span>
                </div>
                <div className="text-sm text-gray-600">Timeline</div>
              </div>
            </div>

            {showDetails && (
              <>
                {/* Affected Companies */}
                <div>
                  <h4 className="font-semibold mb-2 flex items-center gap-2">
                    <Target className="h-4 w-4" />
                    Affected Companies
                  </h4>
                  <div className="space-y-2">
                    {result.affected_companies.map((company, index) => (
                      <div key={index} className={`p-3 border rounded-md ${getImpactColor(company.impact_type)}`}>
                        <div className="flex items-center justify-between mb-1">
                          <div className="flex items-center gap-2">
                            {getImpactIcon(company.impact_type)}
                            <span className="font-medium">{company.name}</span>
                            <Badge variant="outline" className="text-xs">
                              {company.valuation_change}
                            </Badge>
                          </div>
                          <div className="text-sm">
                            Score: {company.new_extraordinary_score}/100
                          </div>
                        </div>
                        <p className="text-sm">{company.reasoning}</p>
                      </div>
                    ))}
                  </div>
                </div>

                {/* New Connections */}
                {result.new_connections.length > 0 && (
                  <div>
                    <h4 className="font-semibold mb-2">New Relationships</h4>
                    <div className="space-y-2">
                      {result.new_connections.map((connection, index) => (
                        <div key={index} className="p-3 bg-gray-50 border border-gray-200 rounded-md">
                          <div className="flex items-center justify-between mb-1">
                            <span className="font-medium">
                              {connection.source} ↔ {connection.target}
                            </span>
                            <Badge variant="outline" className="text-xs">
                              {connection.connection_type}
                            </Badge>
                          </div>
                          <p className="text-sm text-gray-600">{connection.description}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Market Impact */}
                <div className="p-3 bg-gray-50 border border-gray-200 rounded-md">
                  <h4 className="font-semibold mb-2">Market Impact</h4>
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <span className="font-medium">Sector:</span> {result.market_impact.sector}
                    </div>
                    <div>
                      <span className="font-medium">Sentiment:</span> {result.market_impact.overall_sentiment}
                    </div>
                    <div>
                      <span className="font-medium">Market Cap:</span> {result.market_impact.market_cap_change}
                    </div>
                    <div>
                      <span className="font-medium">Innovation:</span> {result.market_impact.innovation_acceleration ? 'Accelerated' : 'Stable'}
                    </div>
                  </div>
                </div>

                {/* Reasoning */}
                <div className="p-3 bg-yellow-50 border border-yellow-200 rounded-md">
                  <h4 className="font-semibold text-yellow-900 mb-1">Analysis</h4>
                  <p className="text-yellow-800 text-sm">{result.reasoning}</p>
                </div>
              </>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
}
