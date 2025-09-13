'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Button } from './ui/button';
import { 
  Trophy, 
  Star, 
  TrendingUp, 
  Users, 
  DollarSign, 
  Award, 
  Newspaper, 
  Lightbulb,
  Target,
  Crown,
  Calendar,
  ExternalLink,
  RefreshCw
} from 'lucide-react';

interface ExtraordinaryMetrics {
  valuation: string;
  funding_raised: string;
  employee_count: number;
  revenue: string;
  unicorn_status: boolean;
  ipo_status: boolean;
  years_in_business: number;
  awards_count: number;
  media_mentions: number;
}

interface ExtraordinaryProfile {
  name: string;
  type: string;
  extraordinary_score: number;
  key_stats: string[];
  notable_achievements: string[];
  awards_recognitions: string[];
  media_coverage: string[];
  innovation_highlights: string[];
  competitive_advantages: string[];
  leadership_team: string[];
  funding_history: string[];
  metrics: ExtraordinaryMetrics;
  created_at: string;
}

interface ExtraordinaryProfileProps {
  entityName: string;
  entityType?: string;
}

export default function ExtraordinaryProfile({ entityName, entityType = 'company' }: ExtraordinaryProfileProps) {
  const [profile, setProfile] = useState<ExtraordinaryProfile | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchProfile = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`/api/extraordinary/research/${encodeURIComponent(entityName)}?entity_type=${entityType}`, {
        method: 'POST'
      });
      
      if (!response.ok) {
        throw new Error(`Failed to fetch profile: ${response.statusText}`);
      }
      
      const data = await response.json();
      setProfile(data.profile);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load profile');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (entityName) {
      fetchProfile();
    }
  }, [entityName, entityType]);

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-yellow-600 bg-yellow-50';
    if (score >= 60) return 'text-red-600 bg-red-50';
    if (score >= 40) return 'text-blue-600 bg-blue-50';
    return 'text-gray-600 bg-gray-50';
  };

  const getScoreLabel = (score: number) => {
    if (score >= 80) return 'Exceptional';
    if (score >= 60) return 'High';
    if (score >= 40) return 'Medium';
    return 'Standard';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <RefreshCw className="h-8 w-8 animate-spin text-blue-600" />
        <span className="ml-2 text-lg">Researching extraordinary profile...</span>
      </div>
    );
  }

  if (error) {
    return (
      <Card className="border-red-200">
        <CardContent className="p-6">
          <div className="text-center">
            <div className="text-red-600 mb-2">❌ Error</div>
            <p className="text-gray-600 mb-4">{error}</p>
            <Button onClick={fetchProfile} variant="outline">
              <RefreshCw className="h-4 w-4 mr-2" />
              Retry
            </Button>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (!profile) {
    return (
      <Card>
        <CardContent className="p-6 text-center">
          <p className="text-gray-600">No profile data available</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <Card className="border-2 border-blue-200">
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="text-2xl flex items-center gap-2">
                <Crown className="h-6 w-6 text-yellow-600" />
                {profile.name}
              </CardTitle>
              <p className="text-gray-600 capitalize">{profile.type}</p>
            </div>
            <div className="text-right">
              <div className={`inline-flex items-center px-4 py-2 rounded-full ${getScoreColor(profile.extraordinary_score)}`}>
                <Star className="h-5 w-5 mr-2" />
                <span className="font-bold text-lg">{profile.extraordinary_score}/100</span>
              </div>
              <p className="text-sm text-gray-600 mt-1">{getScoreLabel(profile.extraordinary_score)}</p>
            </div>
          </div>
        </CardHeader>
      </Card>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-2">
              <DollarSign className="h-5 w-5 text-green-600" />
              <div>
                <p className="text-sm text-gray-600">Valuation</p>
                <p className="font-semibold">{profile.metrics.valuation || 'N/A'}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-2">
              <TrendingUp className="h-5 w-5 text-blue-600" />
              <div>
                <p className="text-sm text-gray-600">Funding Raised</p>
                <p className="font-semibold">{profile.metrics.funding_raised || 'N/A'}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-2">
              <Users className="h-5 w-5 text-purple-600" />
              <div>
                <p className="text-sm text-gray-600">Employees</p>
                <p className="font-semibold">{profile.metrics.employee_count?.toLocaleString() || 'N/A'}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-2">
              <Award className="h-5 w-5 text-orange-600" />
              <div>
                <p className="text-sm text-gray-600">Awards</p>
                <p className="font-semibold">{profile.metrics.awards_count || 0}</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Status Badges */}
      <div className="flex gap-2 flex-wrap">
        {profile.metrics.unicorn_status && (
          <Badge className="bg-purple-100 text-purple-800">
            🦄 Unicorn
          </Badge>
        )}
        {profile.metrics.ipo_status && (
          <Badge className="bg-green-100 text-green-800">
            📈 Public Company
          </Badge>
        )}
        <Badge className="bg-blue-100 text-blue-800">
          <Calendar className="h-3 w-3 mr-1" />
          {profile.metrics.years_in_business} years
        </Badge>
      </div>

      {/* Key Stats */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <TrendingUp className="h-5 w-5" />
            Key Statistics
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {profile.key_stats.map((stat, index) => (
              <div key={index} className="flex items-start gap-2">
                <div className="w-2 h-2 bg-blue-600 rounded-full mt-2 flex-shrink-0"></div>
                <p className="text-sm">{stat}</p>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Notable Achievements */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Trophy className="h-5 w-5 text-yellow-600" />
            Notable Achievements
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {profile.notable_achievements.map((achievement, index) => (
              <div key={index} className="flex items-start gap-2">
                <Trophy className="h-4 w-4 text-yellow-600 mt-1 flex-shrink-0" />
                <p className="text-sm">{achievement}</p>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Innovation & Competitive Advantages */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Lightbulb className="h-5 w-5 text-yellow-500" />
              Innovation Highlights
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {profile.innovation_highlights.map((innovation, index) => (
                <div key={index} className="flex items-start gap-2">
                  <Lightbulb className="h-4 w-4 text-yellow-500 mt-1 flex-shrink-0" />
                  <p className="text-sm">{innovation}</p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Target className="h-5 w-5 text-red-600" />
              Competitive Advantages
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {profile.competitive_advantages.map((advantage, index) => (
                <div key={index} className="flex items-start gap-2">
                  <Target className="h-4 w-4 text-red-600 mt-1 flex-shrink-0" />
                  <p className="text-sm">{advantage}</p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Awards & Media Coverage */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Award className="h-5 w-5 text-orange-600" />
              Awards & Recognition
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {profile.awards_recognitions.map((award, index) => (
                <div key={index} className="flex items-start gap-2">
                  <Award className="h-4 w-4 text-orange-600 mt-1 flex-shrink-0" />
                  <p className="text-sm">{award}</p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Newspaper className="h-5 w-5 text-blue-600" />
              Media Coverage
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {profile.media_coverage.map((media, index) => (
                <div key={index} className="flex items-start gap-2">
                  <Newspaper className="h-4 w-4 text-blue-600 mt-1 flex-shrink-0" />
                  <p className="text-sm">{media}</p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Leadership & Funding */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Users className="h-5 w-5 text-purple-600" />
              Leadership Team
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {profile.leadership_team.map((leader, index) => (
                <div key={index} className="flex items-start gap-2">
                  <Users className="h-4 w-4 text-purple-600 mt-1 flex-shrink-0" />
                  <p className="text-sm">{leader}</p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <DollarSign className="h-5 w-5 text-green-600" />
              Funding History
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {profile.funding_history.map((funding, index) => (
                <div key={index} className="flex items-start gap-2">
                  <DollarSign className="h-4 w-4 text-green-600 mt-1 flex-shrink-0" />
                  <p className="text-sm">{funding}</p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Footer */}
      <Card className="bg-gray-50">
        <CardContent className="p-4">
          <div className="flex items-center justify-between text-sm text-gray-600">
            <span>Profile generated: {new Date(profile.created_at).toLocaleString()}</span>
            <Button onClick={fetchProfile} variant="outline" size="sm">
              <RefreshCw className="h-4 w-4 mr-2" />
              Refresh
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
