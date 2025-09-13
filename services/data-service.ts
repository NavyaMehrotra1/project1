// Data service for fetching and managing company data
import { exaService, EnhancedCompany } from './exa-integration';

export interface CompanyNode {
  id: string;
  name: string;
  batch?: string;
  description?: string;
  website?: string;
  founders?: string[];
  location?: string;
  category?: string;
  funding_stage?: string;
  exa_insights?: any;
  x?: number;
  y?: number;
  fx?: number | null;
  fy?: number | null;
}

export interface CompanyLink {
  source: string | CompanyNode;
  target: string | CompanyNode;
  type: 'partnership' | 'acquisition' | 'investment' | 'competitor' | 'similar';
  strength: number;
}

export interface GraphData {
  nodes: CompanyNode[];
  links: CompanyLink[];
}

class DataService {
  private baseUrl = 'http://localhost:8000';
  private cachedCompanies: CompanyNode[] = [];
  private lastFetch: number = 0;
  private cacheTimeout = 5 * 60 * 1000; // 5 minutes

  async fetchYCCompanies(): Promise<CompanyNode[]> {
    try {
      const response = await fetch(`${this.baseUrl}/api/companies-with-logos`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      return data.companies.map((company: any) => ({
        id: company.id,
        name: company.name,
        industry: company.industry,
        marketCap: company.market_cap,
        foundedYear: company.founded_year,
        headquarters: company.headquarters,
        description: company.description,
        website: company.website,
        isPublic: company.is_public,
        extraordinaryScore: company.extraordinary_score || 0,
        logoUrl: company.logo_url,
        category: this.categorizeCompany(company.industry, company.name),
        fundingStage: this.determineFundingStage(company.market_cap, company.is_public),
        hasExaData: false
      }));
    } catch (error) {
      console.error('Error fetching YC companies:', error);
      return [];
    }
  }

  private categorizeCompany(industry: string, name: string): string {
    // TO DO: implement categorization logic
    return 'Other';
  }

  private determineFundingStage(marketCap: number, isPublic: boolean): string {
    // TO DO: implement funding stage logic
    return 'Unknown';
  }

  private processCompanyData(rawCompanies: any[]): CompanyNode[] {
    return rawCompanies.map((company, index) => ({
      id: company.id || `company-${index}`,
      name: company.name || `Company ${index + 1}`,
      batch: company.batch,
      description: company.description,
      website: company.website,
      founders: company.founders,
      location: company.location,
      category: company.category || this.inferCategory(company.description || ''),
      funding_stage: company.funding_stage || 'Unknown',
      exa_insights: company.exa_insights
    }));
  }

  private inferCategory(description: string): string {
    const categories = {
      'AI/ML': ['ai', 'artificial intelligence', 'machine learning', 'ml', 'neural', 'deep learning'],
      'Fintech': ['finance', 'fintech', 'payment', 'banking', 'crypto', 'blockchain'],
      'Healthcare': ['health', 'medical', 'healthcare', 'biotech', 'pharma'],
      'E-commerce': ['ecommerce', 'marketplace', 'retail', 'shopping'],
      'SaaS': ['saas', 'software', 'platform', 'tool', 'service'],
      'Consumer': ['consumer', 'social', 'mobile app', 'gaming'],
      'Enterprise': ['enterprise', 'b2b', 'business', 'productivity'],
      'Hardware': ['hardware', 'iot', 'robotics', 'device']
    };

    const lowerDesc = description.toLowerCase();
    for (const [category, keywords] of Object.entries(categories)) {
      if (keywords.some(keyword => lowerDesc.includes(keyword))) {
        return category;
      }
    }
    return 'Other';
  }

  private getMockCompanies(): CompanyNode[] {
    return [
      {
        id: 'openai',
        name: 'OpenAI',
        batch: 'W16',
        description: 'AI research and deployment company',
        website: 'https://openai.com',
        founders: ['Sam Altman', 'Elon Musk', 'Greg Brockman'],
        location: 'San Francisco, CA',
        category: 'AI/ML',
        funding_stage: 'Series C+'
      },
      {
        id: 'stripe',
        name: 'Stripe',
        batch: 'S09',
        description: 'Online payment processing platform',
        website: 'https://stripe.com',
        founders: ['Patrick Collison', 'John Collison'],
        location: 'San Francisco, CA',
        category: 'Fintech',
        funding_stage: 'Series C+'
      },
      {
        id: 'airbnb',
        name: 'Airbnb',
        batch: 'W08',
        description: 'Online marketplace for lodging and tourism experiences',
        website: 'https://airbnb.com',
        founders: ['Brian Chesky', 'Joe Gebbia', 'Nathan Blecharczyk'],
        location: 'San Francisco, CA',
        category: 'Consumer',
        funding_stage: 'Public'
      },
      {
        id: 'dropbox',
        name: 'Dropbox',
        batch: 'S07',
        description: 'Cloud storage and file synchronization service',
        website: 'https://dropbox.com',
        founders: ['Drew Houston', 'Arash Ferdowsi'],
        location: 'San Francisco, CA',
        category: 'SaaS',
        funding_stage: 'Public'
      },
      {
        id: 'coinbase',
        name: 'Coinbase',
        batch: 'S12',
        description: 'Cryptocurrency exchange platform',
        website: 'https://coinbase.com',
        founders: ['Brian Armstrong', 'Fred Ehrsam'],
        location: 'San Francisco, CA',
        category: 'Fintech',
        funding_stage: 'Public'
      },
      {
        id: 'instacart',
        name: 'Instacart',
        batch: 'S12',
        description: 'Grocery delivery and pick-up service',
        website: 'https://instacart.com',
        founders: ['Apoorva Mehta'],
        location: 'San Francisco, CA',
        category: 'Consumer',
        funding_stage: 'Public'
      },
      {
        id: 'reddit',
        name: 'Reddit',
        batch: 'S05',
        description: 'Social news aggregation and discussion platform',
        website: 'https://reddit.com',
        founders: ['Steve Huffman', 'Alexis Ohanian'],
        location: 'San Francisco, CA',
        category: 'Consumer',
        funding_stage: 'Public'
      },
      {
        id: 'twitch',
        name: 'Twitch',
        batch: 'S07',
        description: 'Live streaming platform for gamers',
        website: 'https://twitch.tv',
        founders: ['Emmett Shear', 'Justin Kan'],
        location: 'San Francisco, CA',
        category: 'Consumer',
        funding_stage: 'Acquired'
      }
    ];
  }

  private generateConnections(companies: CompanyNode[]): CompanyLink[] {
    const links: CompanyLink[] = [];
    
    // Generate connections based on categories, batches, and locations
    for (let i = 0; i < companies.length; i++) {
      for (let j = i + 1; j < companies.length; j++) {
        const company1 = companies[i];
        const company2 = companies[j];
        
        let connectionType: CompanyLink['type'] | null = null;
        let strength = 0;
        
        // Same category connections
        if (company1.category === company2.category) {
          connectionType = 'similar';
          strength += 0.3;
        }
        
        // Same batch connections
        if (company1.batch === company2.batch && company1.batch) {
          connectionType = 'partnership';
          strength += 0.4;
        }
        
        // Same location connections
        if (company1.location === company2.location) {
          strength += 0.2;
        }
        
        // Fintech and AI connections (common partnerships)
        if ((company1.category === 'Fintech' && company2.category === 'AI/ML') ||
            (company1.category === 'AI/ML' && company2.category === 'Fintech')) {
          connectionType = 'partnership';
          strength += 0.3;
        }
        
        // Create connection if strength is sufficient
        if (strength > 0.3 && Math.random() > 0.6) { // Add some randomness
          links.push({
            source: company1.id,
            target: company2.id,
            type: connectionType || 'similar',
            strength: Math.min(strength, 1)
          });
        }
      }
    }
    
    return links;
  }

  async getGraphData(): Promise<GraphData> {
    const now = Date.now();
    
    // Use cached data if available and not expired
    if (this.cachedCompanies.length > 0 && (now - this.lastFetch) < this.cacheTimeout) {
      return {
        nodes: this.cachedCompanies,
        links: this.generateConnections(this.cachedCompanies)
      };
    }
    
    // Fetch fresh data
    const companies = await this.fetchYCCompanies();
    this.cachedCompanies = companies;
    this.lastFetch = now;
    
    return {
      nodes: companies,
      links: this.generateConnections(companies)
    };
  }

  async enrichCompaniesWithExa(companies: CompanyNode[]): Promise<CompanyNode[]> {
    const batchSize = 5;
    const enrichedCompanies = [...companies];
    
    for (let i = 0; i < companies.length; i += batchSize) {
      const batch = companies.slice(i, i + batchSize);
      const companyNames = batch.map(c => c.name);
      
      try {
        const exaResults = await exaService.enrichCompanyBatch(companyNames);
        
        batch.forEach((company, index) => {
          const exaData = exaResults[company.name];
          if (exaData) {
            const enrichedIndex = i + index;
            enrichedCompanies[enrichedIndex] = {
              ...company,
              exa_insights: exaData
            };
          }
        });
        
        // Rate limiting
        await new Promise(resolve => setTimeout(resolve, 1000));
        
      } catch (error) {
        console.error('Error enriching batch:', error);
      }
    }
    
    return enrichedCompanies;
  }

  async getEnhancedGraphData(): Promise<GraphData> {
    const graphData = await this.getGraphData();
    
    // Enrich companies with Exa data
    const enrichedNodes = await this.enrichCompaniesWithExa(graphData.nodes);
    
    return {
      nodes: enrichedNodes,
      links: graphData.links
    };
  }

  getCategoryColor(category: string): string {
    const colors: Record<string, string> = {
      'AI/ML': '#00ff88',
      'Fintech': '#4a9eff',
      'Healthcare': '#ff6b35',
      'E-commerce': '#9b59b6',
      'SaaS': '#f39c12',
      'Consumer': '#e74c3c',
      'Enterprise': '#34495e',
      'Hardware': '#95a5a6',
      'Other': '#7f8c8d'
    };
    
    return colors[category] || colors['Other'];
  }

  getFundingStageSize(stage: string): number {
    const sizes: Record<string, number> = {
      'Pre-seed': 8,
      'Seed': 10,
      'Series A': 12,
      'Series B': 14,
      'Series C': 16,
      'Series C+': 18,
      'Public': 20,
      'Acquired': 16,
      'Unknown': 10
    };
    
    return sizes[stage] || sizes['Unknown'];
  }
}

export const dataService = new DataService();
