import React, { useState, useEffect } from 'react';
import { exaService, ExaInsights, EnhancedCompany } from '../services/exa-integration';

interface EnhancedCompanyProfileProps {
  companyName: string;
  onClose?: () => void;
}

export const EnhancedCompanyProfile: React.FC<EnhancedCompanyProfileProps> = ({ 
  companyName, 
  onClose 
}) => {
  const [company, setCompany] = useState<EnhancedCompany | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadCompanyData();
  }, [companyName]);

  const loadCompanyData = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const data = await exaService.getCompanyProfile(companyName);
      if (data) {
        setCompany(data);
      } else {
        setError('Company data not found');
      }
    } catch (err) {
      setError('Failed to load company data');
      console.error('Error loading company:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="enhanced-company-profile loading">
        <div className="loading-spinner">
          <i className="fas fa-spinner fa-spin"></i>
          <p>Loading enhanced company data...</p>
        </div>
      </div>
    );
  }

  if (error || !company) {
    return (
      <div className="enhanced-company-profile error">
        <div className="error-message">
          <i className="fas fa-exclamation-triangle"></i>
          <p>{error || 'Company not found'}</p>
          <button onClick={loadCompanyData} className="retry-btn">
            <i className="fas fa-redo"></i> Retry
          </button>
        </div>
      </div>
    );
  }

  const insights = company.exa_insights;
  const completeness = company.profile_completeness;

  return (
    <div className="enhanced-company-profile">
      {onClose && (
        <button className="close-btn" onClick={onClose}>
          <i className="fas fa-times"></i>
        </button>
      )}
      
      {/* Header */}
      <div className="profile-header">
        <div className="company-basic-info">
          <h2 className="company-name">{company.name}</h2>
          {company.website && (
            <a href={company.website} target="_blank" rel="noopener noreferrer" className="website-link">
              <i className="fas fa-external-link-alt"></i> {company.website}
            </a>
          )}
          {company.batch && (
            <span className="yc-batch">YC {company.batch}</span>
          )}
        </div>
        
        {completeness && (
          <div className="completeness-indicator">
            <div className="completeness-score">
              <span className="score">{completeness.percentage}%</span>
              <span className="label">Complete</span>
            </div>
            <div className={`completeness-level ${completeness.level}`}>
              {completeness.level.toUpperCase()}
            </div>
          </div>
        )}
      </div>

      {/* YC Information */}
      {company.description && (
        <div className="profile-section yc-info">
          <h3><i className="fas fa-info-circle"></i> Company Description</h3>
          <p>{company.description}</p>
          
          {company.founders && company.founders.length > 0 && (
            <div className="founders">
              <strong>Founders:</strong> {company.founders.join(', ')}
            </div>
          )}
          
          {company.location && (
            <div className="location">
              <strong>Location:</strong> {company.location}
            </div>
          )}
        </div>
      )}

      {/* Exa Insights */}
      {insights && (
        <>
          {/* AI Summary */}
          {insights.summary && (
            <div className="profile-section ai-summary">
              <h3>
                <i className="fas fa-robot"></i> AI-Generated Summary
                <span className="data-quality" style={{ color: exaService.getDataQualityColor(insights.data_quality) }}>
                  {insights.data_quality.toUpperCase()}
                </span>
              </h3>
              <p>{insights.summary}</p>
              <div className="last-updated">
                Last updated: {exaService.formatLastUpdated(insights.last_updated)}
              </div>
            </div>
          )}

          {/* Key Highlights */}
          {insights.key_highlights && insights.key_highlights.length > 0 && (
            <div className="profile-section highlights">
              <h3><i className="fas fa-star"></i> Key Highlights</h3>
              <ul className="highlights-list">
                {insights.key_highlights.slice(0, 5).map((highlight, index) => (
                  <li key={index}>{highlight}</li>
                ))}
              </ul>
            </div>
          )}

          {/* Funding Information */}
          {insights.funding_info && insights.funding_info.has_recent_funding && (
            <div className="profile-section funding-info">
              <h3><i className="fas fa-dollar-sign"></i> Recent Funding Activity</h3>
              <p className="funding-summary">
                {exaService.formatFundingInfo(insights.funding_info)}
              </p>
              
              {insights.funding_info.mentions.length > 0 && (
                <div className="funding-mentions">
                  {insights.funding_info.mentions.slice(0, 3).map((mention, index) => (
                    <div key={index} className="funding-mention">
                      <a href={mention.url} target="_blank" rel="noopener noreferrer">
                        <strong>{mention.source}</strong>
                      </a>
                      <p>{mention.excerpt}</p>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Recent News */}
          {insights.news_articles && insights.news_articles.length > 0 && (
            <div className="profile-section recent-news">
              <h3><i className="fas fa-newspaper"></i> Recent News</h3>
              <div className="news-articles">
                {insights.news_articles.slice(0, 5).map((article, index) => (
                  <div key={index} className="news-article">
                    <div className="article-header">
                      <a href={article.url} target="_blank" rel="noopener noreferrer">
                        <h4>{article.title}</h4>
                      </a>
                      {article.published_date && (
                        <span className="publish-date">
                          {new Date(article.published_date).toLocaleDateString()}
                        </span>
                      )}
                    </div>
                    {article.summary && (
                      <p className="article-summary">{article.summary}</p>
                    )}
                    {article.highlights && article.highlights.length > 0 && (
                      <div className="article-highlights">
                        {article.highlights.slice(0, 2).map((highlight, hIndex) => (
                          <span key={hIndex} className="highlight-tag">
                            {highlight}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Activity Summary */}
          {insights.recent_activity && insights.recent_activity.length > 0 && (
            <div className="profile-section activity-summary">
              <h3><i className="fas fa-chart-bar"></i> Activity Summary</h3>
              <div className="activity-stats">
                {insights.recent_activity.map((activity, index) => (
                  <div key={index} className="activity-stat">
                    <span className="stat-number">{activity.count}</span>
                    <span className="stat-label">{activity.type}</span>
                    {activity.latest_date && (
                      <span className="stat-date">
                        Latest: {new Date(activity.latest_date).toLocaleDateString()}
                      </span>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
        </>
      )}

      {/* Actions */}
      <div className="profile-actions">
        <button onClick={loadCompanyData} className="refresh-btn">
          <i className="fas fa-sync-alt"></i> Refresh Data
        </button>
        {company.website && (
          <a href={company.website} target="_blank" rel="noopener noreferrer" className="visit-website-btn">
            <i className="fas fa-external-link-alt"></i> Visit Website
          </a>
        )}
      </div>
    </div>
  );
};
