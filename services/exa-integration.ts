// Frontend service for Exa API integration
export interface ExaInsights {
  summary: string;
  news_articles: Array<{
    title: string;
    url: string;
    published_date: string;
    summary: string;
    highlights: string[];
  }>;
  key_highlights: string[];
  funding_info: {
    mentions: Array<{
      source: string;
      url: string;
      excerpt: string;
    }>;
    has_recent_funding: boolean;
  };
  recent_activity: Array<{
    type: string;
    count: number;
    latest_date: string;
  }>;
  last_updated: string;
  data_quality: 'high' | 'medium' | 'low';
}

export interface EnhancedCompany {
  name: string;
  description?: string;
  website?: string;
  batch?: string;
  founders?: string[];
  location?: string;
  exa_insights?: ExaInsights;
  profile_completeness?: {
    score: number;
    max_score: number;
    percentage: number;
    level: 'high' | 'medium' | 'low';
  };
}

class ExaIntegrationService {
  private baseUrl = '/api/exa';

  async enrichCompany(companyName: string): Promise<ExaInsights | null> {
    try {
      const response = await fetch(`${this.baseUrl}/enrich-company`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          company_name: companyName,
          num_results: 10
        })
      });

      if (!response.ok) {
        console.error(`Failed to enrich ${companyName}: ${response.statusText}`);
        return null;
      }

      const data = await response.json();
      return data.exa_data;
    } catch (error) {
      console.error(`Error enriching company ${companyName}:`, error);
      return null;
    }
  }

  async enrichCompanyBatch(companies: string[]): Promise<Record<string, ExaInsights>> {
    try {
      const response = await fetch(`${this.baseUrl}/enrich-batch`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          companies: companies.slice(0, 50), // Limit to 50 companies
          max_concurrent: 5
        })
      });

      if (!response.ok) {
        console.error(`Batch enrichment failed: ${response.statusText}`);
        return {};
      }

      const data = await response.json();
      const results: Record<string, ExaInsights> = {};

      data.results?.forEach((result: any) => {
        if (result.status === 'success') {
          results[result.company_name] = result.exa_data;
        }
      });

      return results;
    } catch (error) {
      console.error('Error in batch enrichment:', error);
      return {};
    }
  }

  async getCompanyProfile(companyName: string): Promise<EnhancedCompany | null> {
    try {
      const response = await fetch(`${this.baseUrl}/company/${encodeURIComponent(companyName)}`);
      
      if (!response.ok) {
        console.error(`Failed to get profile for ${companyName}: ${response.statusText}`);
        return null;
      }

      return await response.json();
    } catch (error) {
      console.error(`Error getting profile for ${companyName}:`, error);
      return null;
    }
  }

  async checkServiceHealth(): Promise<boolean> {
    try {
      const response = await fetch(`${this.baseUrl}/health`);
      const data = await response.json();
      return data.status === 'healthy';
    } catch (error) {
      console.error('Exa service health check failed:', error);
      return false;
    }
  }

  // Utility methods for data processing
  formatFundingInfo(fundingInfo: ExaInsights['funding_info']): string {
    if (!fundingInfo.has_recent_funding) {
      return 'No recent funding information found';
    }

    const mentionsCount = fundingInfo.mentions.length;
    return `${mentionsCount} recent funding mention${mentionsCount > 1 ? 's' : ''} found`;
  }

  getDataQualityColor(quality: ExaInsights['data_quality']): string {
    switch (quality) {
      case 'high': return '#00ff88';
      case 'medium': return '#ffaa00';
      case 'low': return '#ff6b35';
      default: return '#888';
    }
  }

  formatLastUpdated(lastUpdated: string): string {
    try {
      const date = new Date(lastUpdated);
      const now = new Date();
      const diffMs = now.getTime() - date.getTime();
      const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
      
      if (diffHours < 1) return 'Just updated';
      if (diffHours < 24) return `${diffHours}h ago`;
      
      const diffDays = Math.floor(diffHours / 24);
      return `${diffDays}d ago`;
    } catch {
      return 'Unknown';
    }
  }
}

export const exaService = new ExaIntegrationService();
