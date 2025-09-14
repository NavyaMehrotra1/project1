# Company News API Integration Guide

## API Endpoints

### Base URL: `http://localhost:8000/api/v1`

## 1. Get Company News
**Endpoint:** `GET /company-news`

**Query Parameters:**
- `companies` (optional): Comma-separated company names
- `days_back` (default: 7): Days to look back for news
- `limit` (default: 50): Max news items to return
- `category` (optional): Filter by M&A, Funding, Partnership, IPO, etc.

**Response Format:**
```json
{
  "success": true,
  "total_companies_searched": 20,
  "total_news_found": 15,
  "days_back": 7,
  "news": [
    {
      "id": "news_12345",
      "title": "Stripe raises $6.5B in Series H funding",
      "description": "Payment processor Stripe has raised $6.5 billion...",
      "source": "TechCrunch",
      "url": "https://techcrunch.com/...",
      "published_date": "2025-09-13T10:30:00Z",
      "time_ago": "2h ago",
      "companies": ["Stripe"],
      "category": "Funding",
      "deal_type": "investment",
      "deal_value": 6500000000,
      "deal_value_formatted": "$6.5B",
      "is_major": true,
      "relevance_score": 0.95
    }
  ]
}
```

## 2. Get News Summary
**Endpoint:** `GET /company-news/summary`

**Response Format:**
```json
{
  "success": true,
  "summary": {
    "total_news_items": 45,
    "total_companies_with_news": 12,
    "total_deal_value": 15600000000,
    "total_deal_value_formatted": "$15.6B",
    "category_breakdown": {
      "M&A": 8,
      "Funding": 15,
      "Partnership": 5,
      "IPO": 2
    },
    "major_deals_count": 6,
    "recent_major_deals": [
      {
        "title": "OpenAI valued at $157B in new funding",
        "companies": ["OpenAI"],
        "value": "$6.6B",
        "type": "investment",
        "date": "2025-09-13T08:00:00Z"
      }
    ],
    "last_updated": "2025-09-13T21:45:00Z"
  }
}
```

## 3. Get Single Company News
**Endpoint:** `GET /company-news/{company_name}`

**Example:** `GET /company-news/Stripe?days_back=30&limit=10`

## 4. Get News Categories
**Endpoint:** `GET /company-news/categories`

**Response Format:**
```json
{
  "success": true,
  "categories": [
    {"id": "ma", "name": "M&A", "description": "Mergers and Acquisitions"},
    {"id": "funding", "name": "Funding", "description": "Investment and Funding Rounds"},
    {"id": "partnership", "name": "Partnership", "description": "Strategic Partnerships"},
    {"id": "ipo", "name": "IPO", "description": "Initial Public Offerings"}
  ]
}
```

## Frontend Integration Examples

### React/Next.js Hook
```typescript
// hooks/useCompanyNews.ts
import { useState, useEffect } from 'react';

interface NewsItem {
  id: string;
  title: string;
  description: string;
  source: string;
  url: string;
  published_date: string;
  time_ago: string;
  companies: string[];
  category: string;
  deal_type?: string;
  deal_value?: number;
  deal_value_formatted?: string;
  is_major: boolean;
  relevance_score: number;
}

export const useCompanyNews = (daysBack = 7, limit = 20) => {
  const [news, setNews] = useState<NewsItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchNews = async () => {
      try {
        setLoading(true);
        const response = await fetch(
          `http://localhost:8000/api/v1/company-news?days_back=${daysBack}&limit=${limit}`
        );
        const data = await response.json();
        
        if (data.success) {
          setNews(data.news);
        } else {
          setError('Failed to fetch news');
        }
      } catch (err) {
        setError('Network error');
      } finally {
        setLoading(false);
      }
    };

    fetchNews();
  }, [daysBack, limit]);

  return { news, loading, error };
};
```

### News Card Component
```typescript
// components/NewsCard.tsx
interface NewsCardProps {
  news: NewsItem;
}

export const NewsCard = ({ news }: NewsCardProps) => {
  const getCategoryColor = (category: string) => {
    const colors = {
      'M&A': 'bg-purple-100 text-purple-800',
      'Funding': 'bg-green-100 text-green-800',
      'Partnership': 'bg-blue-100 text-blue-800',
      'IPO': 'bg-orange-100 text-orange-800',
      'General': 'bg-gray-100 text-gray-800'
    };
    return colors[category] || colors['General'];
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow">
      <div className="flex justify-between items-start mb-3">
        <span className={`px-2 py-1 rounded-full text-xs font-medium ${getCategoryColor(news.category)}`}>
          {news.category}
        </span>
        <span className="text-sm text-gray-500">{news.time_ago}</span>
      </div>
      
      <h3 className="font-semibold text-lg mb-2 line-clamp-2">
        {news.title}
      </h3>
      
      <p className="text-gray-600 text-sm mb-3 line-clamp-3">
        {news.description}
      </p>
      
      <div className="flex justify-between items-center">
        <div className="flex flex-wrap gap-1">
          {news.companies.map((company, idx) => (
            <span key={idx} className="bg-gray-100 text-gray-700 px-2 py-1 rounded text-xs">
              {company}
            </span>
          ))}
        </div>
        
        {news.deal_value_formatted && (
          <span className="font-bold text-green-600">
            {news.deal_value_formatted}
          </span>
        )}
      </div>
      
      <div className="mt-3 flex justify-between items-center">
        <span className="text-xs text-gray-500">{news.source}</span>
        <a 
          href={news.url} 
          target="_blank" 
          rel="noopener noreferrer"
          className="text-blue-600 hover:text-blue-800 text-sm font-medium"
        >
          Read More →
        </a>
      </div>
    </div>
  );
};
```

### Usage in Component
```typescript
// components/CompanyNewsSection.tsx
import { useCompanyNews } from '../hooks/useCompanyNews';
import { NewsCard } from './NewsCard';

export const CompanyNewsSection = () => {
  const { news, loading, error } = useCompanyNews(7, 20);

  if (loading) return <div>Loading news...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <div className="space-y-4">
      <h2 className="text-2xl font-bold">Latest Company News</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {news.map((item) => (
          <NewsCard key={item.id} news={item} />
        ))}
      </div>
    </div>
  );
};
```

## Starting the API Server

```bash
cd /Users/sutharsikakumar/project1-1/backend
pip install fastapi uvicorn
python company_news_server.py
```

The API will be available at:
- **Base URL:** http://localhost:8000
- **Documentation:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/health

## Key Features

1. **Real NewsAPI Integration**: Uses actual NewsAPI with your key
2. **Multi-Source Data**: Combines NewsAPI, Yahoo Finance, Google News
3. **Smart Filtering**: Relevance scoring and category classification
4. **Deal Value Extraction**: Automatically extracts and formats deal amounts
5. **Company Dataset Integration**: Uses your existing company data
6. **UI-Ready Format**: Pre-formatted for card components
7. **CORS Enabled**: Ready for frontend integration
8. **Error Handling**: Comprehensive error responses
9. **Rate Limiting**: Built-in API rate limiting
10. **Caching Ready**: Structured for future caching implementation
