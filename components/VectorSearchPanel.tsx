'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Button } from './ui/button';
import { 
  Search, 
  Building2, 
  Network, 
  Sparkles, 
  TrendingUp,
  Users,
  ChevronDown,
  ChevronUp,
  Database,
  Zap
} from 'lucide-react';

interface SearchResult {
  content: string;
  metadata: {
    company_id?: string;
    company_name?: string;
    industry?: string;
    batch?: string;
    status?: string;
    valuation?: number;
    extraordinary_score?: number;
    deal_activity_count?: number;
    type: string;
    source?: string;
    target?: string;
    relationship_type?: string;
  };
  score?: number;
}

interface SearchResponse {
  results: SearchResult[];
  query: string;
  total_results: number;
  search_type: string;
}

export default function VectorSearchPanel() {
  const [query, setQuery] = useState('');
  const [searchType, setSearchType] = useState<'all' | 'company' | 'relationship'>('all');
  const [results, setResults] = useState<SearchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showDetails, setShowDetails] = useState<{[key: number]: boolean}>({});
  const [dbStats, setDbStats] = useState<any>(null);
  const [examples, setExamples] = useState<any>(null);

  // Load database stats and examples on mount
  useEffect(() => {
    loadDbStats();
    loadExamples();
  }, []);

  const loadDbStats = async () => {
    try {
      const response = await fetch('/api/vector-search/stats');
      if (response.ok) {
        const stats = await response.json();
        setDbStats(stats);
      }
    } catch (error) {
      console.error('Error loading database stats:', error);
    }
  };

  const loadExamples = async () => {
    try {
      const response = await fetch('/api/vector-search/examples');
      if (response.ok) {
        const data = await response.json();
        setExamples(data);
      }
    } catch (error) {
      console.error('Error loading examples:', error);
    }
  };

  const performSearch = async () => {
    if (!query.trim()) {
      setError('Please enter a search query');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const endpoint = searchType === 'all' 
        ? '/api/vector-search/search'
        : `/api/vector-search/${searchType === 'company' ? 'companies' : 'relationships'}/search`;

      const response = await fetch(endpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: query.trim(),
          k: 10
        }),
      });

      if (!response.ok) {
        throw new Error(`Search failed: ${response.statusText}`);
      }

      const data: SearchResponse = await response.json();
      setResults(data.results);

    } catch (err) {
      setError(err instanceof Error ? err.message : 'Search failed');
      setResults([]);
    } finally {
      setLoading(false);
    }
  };

  const findSimilarCompanies = async (companyName: string) => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`/api/vector-search/companies/similar/${encodeURIComponent(companyName)}?k=5`);

      if (!response.ok) {
        throw new Error(`Similar search failed: ${response.statusText}`);
      }

      const data = await response.json();
      setResults(data.similar_companies);
      setQuery(`Companies similar to ${companyName}`);

    } catch (err) {
      setError(err instanceof Error ? err.message : 'Similar search failed');
      setResults([]);
    } finally {
      setLoading(false);
    }
  };

  const toggleDetails = (index: number) => {
    setShowDetails(prev => ({
      ...prev,
      [index]: !prev[index]
    }));
  };

  const formatValuation = (valuation: number) => {
    if (valuation >= 1_000_000_000) {
      return `$${(valuation / 1_000_000_000).toFixed(1)}B`;
    } else if (valuation >= 1_000_000) {
      return `$${(valuation / 1_000_000).toFixed(1)}M`;
    }
    return `$${valuation.toLocaleString()}`;
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'company': return <Building2 className="h-4 w-4" />;
      case 'relationship': return <Network className="h-4 w-4" />;
      default: return <Search className="h-4 w-4" />;
    }
  };

  const getTypeColor = (type: string) => {
    switch (type) {
      case 'company': return 'bg-blue-50 border-blue-200 text-blue-800';
      case 'relationship': return 'bg-purple-50 border-purple-200 text-purple-800';
      default: return 'bg-gray-50 border-gray-200 text-gray-800';
    }
  };

  return (
    <div className="space-y-6">
      {/* Header with Stats */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center gap-2">
              <Database className="h-5 w-5 text-green-600" />
              Vector Search
            </CardTitle>
            {dbStats && (
              <div className="flex items-center gap-4 text-sm text-gray-600">
                <span>{dbStats.total_documents} documents</span>
                <Badge variant="outline">{dbStats.embedding_model}</Badge>
              </div>
            )}
          </div>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {/* Search Input */}
            <div className="flex gap-2">
              <div className="flex-1">
                <input
                  type="text"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  placeholder="Search companies, industries, relationships..."
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  disabled={loading}
                  onKeyPress={(e) => e.key === 'Enter' && performSearch()}
                />
              </div>
              <select
                value={searchType}
                onChange={(e) => setSearchType(e.target.value as any)}
                className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                disabled={loading}
              >
                <option value="all">All</option>
                <option value="company">Companies</option>
                <option value="relationship">Relationships</option>
              </select>
              <Button 
                onClick={performSearch} 
                disabled={loading || !query.trim()}
                className="bg-blue-600 hover:bg-blue-700"
              >
                {loading ? (
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white" />
                ) : (
                  <Search className="h-4 w-4" />
                )}
              </Button>
            </div>

            {/* Example Queries */}
            {examples && (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                <div>
                  <h4 className="font-medium mb-2">Example Company Searches:</h4>
                  <div className="space-y-1">
                    {examples.company_searches?.slice(0, 3).map((example: string, index: number) => (
                      <button
                        key={index}
                        onClick={() => setQuery(example)}
                        className="block text-left text-blue-600 hover:text-blue-800 hover:underline"
                      >
                        "{example}"
                      </button>
                    ))}
                  </div>
                </div>
                <div>
                  <h4 className="font-medium mb-2">Find Similar Companies:</h4>
                  <div className="space-y-1">
                    {examples.similarity_searches?.slice(0, 3).map((company: string, index: number) => (
                      <button
                        key={index}
                        onClick={() => findSimilarCompanies(company)}
                        className="block text-left text-purple-600 hover:text-purple-800 hover:underline"
                      >
                        Similar to {company}
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {error && (
              <div className="p-3 bg-red-50 border border-red-200 rounded-md text-red-800 text-sm">
                {error}
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Search Results */}
      {results.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Sparkles className="h-5 w-5 text-purple-600" />
              Search Results ({results.length})
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {results.map((result, index) => (
                <div key={index} className={`p-4 border rounded-lg ${getTypeColor(result.metadata.type)}`}>
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex items-center gap-2">
                      {getTypeIcon(result.metadata.type)}
                      <Badge variant="outline" className="bg-white">
                        {result.metadata.type}
                      </Badge>
                      {result.metadata.company_name && (
                        <span className="font-semibold">{result.metadata.company_name}</span>
                      )}
                    </div>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => toggleDetails(index)}
                    >
                      {showDetails[index] ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
                    </Button>
                  </div>

                  {/* Quick Info */}
                  <div className="mb-2">
                    {result.metadata.type === 'company' && (
                      <div className="flex items-center gap-4 text-sm">
                        {result.metadata.industry && (
                          <span>{result.metadata.industry}</span>
                        )}
                        {result.metadata.batch && (
                          <Badge variant="outline" className="bg-white text-xs">
                            {result.metadata.batch}
                          </Badge>
                        )}
                        {result.metadata.extraordinary_score && (
                          <div className="flex items-center gap-1">
                            <TrendingUp className="h-3 w-3" />
                            <span>{result.metadata.extraordinary_score}/100</span>
                          </div>
                        )}
                        {result.metadata.valuation && (
                          <span className="font-medium">
                            {formatValuation(result.metadata.valuation)}
                          </span>
                        )}
                      </div>
                    )}
                    {result.metadata.type === 'relationship' && (
                      <div className="text-sm">
                        <span className="font-medium">{result.metadata.source}</span>
                        {' → '}
                        <span className="font-medium">{result.metadata.target}</span>
                        {result.metadata.relationship_type && (
                          <Badge variant="outline" className="bg-white text-xs ml-2">
                            {result.metadata.relationship_type}
                          </Badge>
                        )}
                      </div>
                    )}
                  </div>

                  {/* Content Preview */}
                  <p className="text-sm">
                    {showDetails[index] 
                      ? result.content 
                      : `${result.content.substring(0, 150)}${result.content.length > 150 ? '...' : ''}`
                    }
                  </p>

                  {/* Additional Details */}
                  {showDetails[index] && result.metadata.type === 'company' && (
                    <div className="mt-3 pt-3 border-t border-white/50">
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                        {result.metadata.status && (
                          <div>
                            <span className="font-medium">Status:</span> {result.metadata.status}
                          </div>
                        )}
                        {result.metadata.deal_activity_count && (
                          <div>
                            <span className="font-medium">Deals:</span> {result.metadata.deal_activity_count}
                          </div>
                        )}
                        <div>
                          <span className="font-medium">ID:</span> {result.metadata.company_id}
                        </div>
                      </div>
                    </div>
                  )}

                  {/* Similar Companies Button */}
                  {result.metadata.type === 'company' && result.metadata.company_name && (
                    <div className="mt-3 pt-3 border-t border-white/50">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => findSimilarCompanies(result.metadata.company_name!)}
                        className="bg-white"
                      >
                        <Users className="h-3 w-3 mr-1" />
                        Find Similar
                      </Button>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
