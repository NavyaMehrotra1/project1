'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Button } from './ui/button';
import { 
  Trophy, 
  Star, 
  Crown, 
  TrendingUp, 
  ExternalLink,
  RefreshCw,
  Filter
} from 'lucide-react';

interface ExtraordinaryCompany {
  name: string;
  extraordinary_score: number;
  industry?: string;
  valuation?: string;
  batch?: string;
  status?: string;
  metrics?: {
    valuation: string;
    funding_raised: string;
    employee_count: number;
    unicorn_status: boolean;
    ipo_status: boolean;
    awards_count: number;
  };
}

interface LeaderboardData {
  leaderboard: ExtraordinaryCompany[];
  total_companies: number;
  average_score: number;
  top_score: number;
}

export default function ExtraordinaryLeaderboard() {
  const [leaderboard, setLeaderboard] = useState<LeaderboardData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [filter, setFilter] = useState<'all' | 'exceptional' | 'high' | 'medium'>('all');

  const fetchLeaderboard = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch('/api/extraordinary/leaderboard');
      
      if (!response.ok) {
        throw new Error(`Failed to fetch leaderboard: ${response.statusText}`);
      }
      
      const data = await response.json();
      setLeaderboard(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load leaderboard');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLeaderboard();
  }, []);

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-yellow-600 bg-yellow-50 border-yellow-200';
    if (score >= 60) return 'text-red-600 bg-red-50 border-red-200';
    if (score >= 40) return 'text-blue-600 bg-blue-50 border-blue-200';
    return 'text-gray-600 bg-gray-50 border-gray-200';
  };

  const getScoreLabel = (score: number) => {
    if (score >= 80) return 'Exceptional';
    if (score >= 60) return 'High';
    if (score >= 40) return 'Medium';
    return 'Standard';
  };

  const getScoreIcon = (score: number) => {
    if (score >= 80) return <Crown className="h-4 w-4" />;
    if (score >= 60) return <Trophy className="h-4 w-4" />;
    if (score >= 40) return <Star className="h-4 w-4" />;
    return <TrendingUp className="h-4 w-4" />;
  };

  const filteredCompanies = leaderboard?.leaderboard.filter(company => {
    if (filter === 'all') return true;
    if (filter === 'exceptional') return company.extraordinary_score >= 80;
    if (filter === 'high') return company.extraordinary_score >= 60 && company.extraordinary_score < 80;
    if (filter === 'medium') return company.extraordinary_score >= 40 && company.extraordinary_score < 60;
    return true;
  }) || [];

  if (loading) {
    return (
      <Card>
        <CardContent className="p-6">
          <div className="flex items-center justify-center">
            <RefreshCw className="h-6 w-6 animate-spin text-blue-600 mr-2" />
            <span>Loading extraordinary leaderboard...</span>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card className="border-red-200">
        <CardContent className="p-6">
          <div className="text-center">
            <div className="text-red-600 mb-2">❌ Error</div>
            <p className="text-gray-600 mb-4">{error}</p>
            <Button onClick={fetchLeaderboard} variant="outline">
              <RefreshCw className="h-4 w-4 mr-2" />
              Retry
            </Button>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (!leaderboard) {
    return (
      <Card>
        <CardContent className="p-6 text-center">
          <p className="text-gray-600">No leaderboard data available</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header with Stats */}
      <Card className="border-2 border-yellow-200 bg-gradient-to-r from-yellow-50 to-orange-50">
        <CardHeader>
          <CardTitle className="text-2xl flex items-center gap-2">
            <Crown className="h-6 w-6 text-yellow-600" />
            Extraordinary Companies Leaderboard
          </CardTitle>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-yellow-600">{leaderboard.total_companies}</div>
              <div className="text-sm text-gray-600">Total Companies</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">{Math.round(leaderboard.average_score)}</div>
              <div className="text-sm text-gray-600">Average Score</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-red-600">{leaderboard.top_score}</div>
              <div className="text-sm text-gray-600">Top Score</div>
            </div>
          </div>
        </CardHeader>
      </Card>

      {/* Filters */}
      <Card>
        <CardContent className="p-4">
          <div className="flex items-center gap-2 flex-wrap">
            <Filter className="h-4 w-4 text-gray-600" />
            <span className="text-sm font-medium text-gray-700">Filter by score:</span>
            <Button
              variant={filter === 'all' ? 'default' : 'outline'}
              size="sm"
              onClick={() => setFilter('all')}
            >
              All ({leaderboard.leaderboard.length})
            </Button>
            <Button
              variant={filter === 'exceptional' ? 'default' : 'outline'}
              size="sm"
              onClick={() => setFilter('exceptional')}
              className="bg-yellow-100 text-yellow-800 hover:bg-yellow-200"
            >
              Exceptional (80+)
            </Button>
            <Button
              variant={filter === 'high' ? 'default' : 'outline'}
              size="sm"
              onClick={() => setFilter('high')}
              className="bg-red-100 text-red-800 hover:bg-red-200"
            >
              High (60-79)
            </Button>
            <Button
              variant={filter === 'medium' ? 'default' : 'outline'}
              size="sm"
              onClick={() => setFilter('medium')}
              className="bg-blue-100 text-blue-800 hover:bg-blue-200"
            >
              Medium (40-59)
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Leaderboard */}
      <div className="space-y-3">
        {filteredCompanies.map((company, index) => (
          <Card key={company.name} className={`border ${getScoreColor(company.extraordinary_score)}`}>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="flex items-center gap-2">
                    <div className="text-2xl font-bold text-gray-400">
                      #{leaderboard.leaderboard.findIndex(c => c.name === company.name) + 1}
                    </div>
                    {getScoreIcon(company.extraordinary_score)}
                  </div>
                  
                  <div>
                    <h3 className="font-semibold text-lg">{company.name}</h3>
                    <div className="flex items-center gap-2 mt-1">
                      {company.industry && (
                        <Badge variant="outline" className="text-xs">
                          {company.industry}
                        </Badge>
                      )}
                      {company.batch && (
                        <Badge variant="outline" className="text-xs bg-blue-50">
                          {company.batch}
                        </Badge>
                      )}
                      {company.metrics?.unicorn_status && (
                        <Badge className="text-xs bg-purple-100 text-purple-800">
                          🦄 Unicorn
                        </Badge>
                      )}
                      {company.metrics?.ipo_status && (
                        <Badge className="text-xs bg-green-100 text-green-800">
                          📈 Public
                        </Badge>
                      )}
                    </div>
                  </div>
                </div>
                
                <div className="text-right">
                  <div className={`inline-flex items-center px-3 py-1 rounded-full border ${getScoreColor(company.extraordinary_score)}`}>
                    <span className="font-bold text-lg">{company.extraordinary_score}</span>
                    <span className="text-sm ml-1">/100</span>
                  </div>
                  <p className="text-xs text-gray-600 mt-1">{getScoreLabel(company.extraordinary_score)}</p>
                </div>
              </div>
              
              {(company.valuation || company.metrics?.funding_raised) && (
                <div className="mt-3 pt-3 border-t border-gray-100">
                  <div className="flex items-center gap-4 text-sm text-gray-600">
                    {company.valuation && (
                      <div>
                        <span className="font-medium">Valuation:</span> {company.valuation}
                      </div>
                    )}
                    {company.metrics?.funding_raised && (
                      <div>
                        <span className="font-medium">Funding:</span> {company.metrics.funding_raised}
                      </div>
                    )}
                    {company.metrics?.employee_count && (
                      <div>
                        <span className="font-medium">Employees:</span> {company.metrics.employee_count.toLocaleString()}
                      </div>
                    )}
                  </div>
                </div>
              )}
              
              <div className="mt-3 flex justify-end">
                <Button 
                  variant="outline" 
                  size="sm"
                  onClick={() => window.open(`/extraordinary/${encodeURIComponent(company.name)}`, '_blank')}
                >
                  <ExternalLink className="h-3 w-3 mr-1" />
                  View Profile
                </Button>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {filteredCompanies.length === 0 && (
        <Card>
          <CardContent className="p-6 text-center">
            <p className="text-gray-600">No companies found for the selected filter</p>
          </CardContent>
        </Card>
      )}

      {/* Footer */}
      <Card className="bg-gray-50">
        <CardContent className="p-4">
          <div className="flex items-center justify-between text-sm text-gray-600">
            <span>Showing {filteredCompanies.length} of {leaderboard.leaderboard.length} companies</span>
            <Button onClick={fetchLeaderboard} variant="outline" size="sm">
              <RefreshCw className="h-4 w-4 mr-2" />
              Refresh
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
