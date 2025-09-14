"""
Extraordinary Profile Service
Deep research service for generating comprehensive company profiles
"""

import asyncio
import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from pathlib import Path
import uuid
import re
import os
from urllib.parse import urlparse
import requests
from dataclasses import asdict

from models.extraordinary_profile import (
    ExtraordinaryProfile, NotableArticle, Recognition, ExtraordinaryFeat,
    CompanyStats, ResearchSource, ProfileGenerationRequest, ProfileSearchQuery,
    ArticleType, RecognitionType, FeatType
)

logger = logging.getLogger(__name__)

class ExtraordinaryProfileService:
    def __init__(self, exa_api_key: str = None):
        self.exa_api_key = exa_api_key
        self.profiles_dir = Path(__file__).parent.parent / "data" / "extraordinary_profiles"
        self.profiles_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize Exa client
        self.exa_client = None
        if exa_api_key:
            try:
                from exa_py import Exa
                self.exa_client = Exa(api_key=exa_api_key)
                logger.info("Exa API client initialized for deep research")
            except ImportError:
                logger.warning("Exa API not available. Install with: pip install exa_py")
        
        # Initialize Claude client for AI analysis
        self.claude_client = None
        claude_api_key = os.getenv("ANTHROPIC_API_KEY")
        if claude_api_key:
            try:
                import anthropic
                self.claude_client = anthropic.Anthropic(api_key=claude_api_key)
                logger.info("Claude AI client initialized for content analysis")
            except ImportError:
                logger.warning("Anthropic client not available. Install with: pip install anthropic")
        
        # Research configuration
        self.max_articles_per_query = 8
        self.max_total_articles = 25
        self.quality_threshold = 0.4
        self.research_timeout = 300  # 5 minutes max per company
    
    async def generate_extraordinary_profile(self, request: ProfileGenerationRequest) -> ExtraordinaryProfile:
        """Generate a comprehensive extraordinary profile for a company"""
        logger.info(f"🔍 Generating extraordinary profile for {request.company_name}")
        
        # Check if profile already exists and not forcing regeneration
        existing_profile = await self.load_profile(request.company_id)
        if existing_profile and not request.force_regenerate:
            # Update existing profile with new data
            return await self.update_existing_profile(existing_profile, request)
        
        # Create new profile
        profile = ExtraordinaryProfile(
            company_id=request.company_id,
            company_name=request.company_name,
            industry=request.industry or "Unknown",
            profile_id=str(uuid.uuid4())
        )
        
        # Perform deep research
        await self._conduct_deep_research(profile, request)
        
        # Calculate scores
        profile.calculate_profile_scores()
        
        # Save profile
        await self.save_profile(profile)
        
        logger.info(f"✅ Generated extraordinary profile for {request.company_name}")
        logger.info(f"   Articles: {len(profile.notable_articles)}")
        logger.info(f"   Recognitions: {len(profile.recognitions)}")
        logger.info(f"   Feats: {len(profile.extraordinary_feats)}")
        logger.info(f"   Overall Score: {profile.overall_profile_score:.2f}")
        
        return profile
    
    async def _conduct_deep_research(self, profile: ExtraordinaryProfile, request: ProfileGenerationRequest):
        """Conduct comprehensive research using multiple sources"""
        company_name = profile.company_name
        industry = profile.industry
        
        # Define research queries based on depth level
        research_queries = self._generate_research_queries(company_name, industry, request.research_depth)
        
        # Track research progress
        profile.research_queries_performed = research_queries
        
        # Perform research in parallel
        research_tasks = []
        
        # 1. Notable Articles Research
        if not request.focus_areas or "articles" in request.focus_areas:
            research_tasks.append(self._research_notable_articles(profile, research_queries))
        
        # 2. Recognitions Research
        if not request.focus_areas or "recognitions" in request.focus_areas:
            research_tasks.append(self._research_recognitions(profile, research_queries))
        
        # 3. Extraordinary Feats Research
        if not request.focus_areas or "feats" in request.focus_areas:
            research_tasks.append(self._research_extraordinary_feats(profile, research_queries))
        
        # 4. Company Stats Research
        if not request.focus_areas or "stats" in request.focus_areas:
            research_tasks.append(self._research_company_stats(profile, research_queries))
        
        # Execute all research tasks
        await asyncio.gather(*research_tasks, return_exceptions=True)
    
    def _generate_research_queries(self, company_name: str, industry: str, depth: str) -> List[str]:
        """Generate comprehensive research queries based on depth level"""
        base_queries = [
            f"{company_name} company profile",
            f"{company_name} achievements milestones",
            f"{company_name} awards recognition",
            f"{company_name} news articles",
            f"{company_name} funding valuation",
        ]
        
        industry_queries = [
            f"{company_name} {industry} innovation",
            f"{company_name} {industry} leadership",
            f"{company_name} {industry} market share",
        ]
        
        deep_queries = [
            f"{company_name} CEO founder interview",
            f"{company_name} technical breakthrough",
            f"{company_name} patent technology",
            f"{company_name} customer success stories",
            f"{company_name} employee growth culture",
            f"{company_name} social impact sustainability",
            f"{company_name} competitive advantage",
            f"{company_name} future roadmap vision",
        ]
        
        comprehensive_queries = [
            f"{company_name} financial performance metrics",
            f"{company_name} user adoption statistics",
            f"{company_name} partnership collaborations",
            f"{company_name} product launches features",
            f"{company_name} market expansion international",
            f"{company_name} research development R&D",
            f"{company_name} thought leadership content",
            f"{company_name} industry analysis reports",
            f"{company_name} customer testimonials reviews",
            f"{company_name} team expertise talent",
        ]
        
        if depth == "basic":
            return base_queries[:3]
        elif depth == "standard":
            return base_queries + industry_queries[:2]
        elif depth == "deep":
            return base_queries + industry_queries + deep_queries[:5]
        else:  # comprehensive
            return base_queries + industry_queries + deep_queries + comprehensive_queries
    
    async def _research_notable_articles(self, profile: ExtraordinaryProfile, queries: List[str]):
        """Research notable articles about the company using advanced Exa API integration"""
        if not self.exa_client:
            logger.warning("Exa client not available for article research")
            return
        
        try:
            articles = []
            profile.total_sources_analyzed = 0
            
            # Enhanced article search queries
            article_queries = [
                f"{profile.company_name} breakthrough innovation achievement",
                f"{profile.company_name} CEO founder interview profile",
                f"{profile.company_name} funding unicorn valuation news",
                f"{profile.company_name} product launch milestone success",
                f"{profile.company_name} industry leader recognition award",
                f"{profile.company_name} technical innovation patent",
                f"{profile.company_name} growth expansion market",
                f"{profile.company_name} thought leadership content",
                f"{profile.company_name} customer success story case study",
                f"{profile.company_name} partnership collaboration deal"
            ]
            
            # Add industry-specific queries
            if profile.industry and profile.industry != "Unknown":
                article_queries.extend([
                    f"{profile.company_name} {profile.industry} disruption",
                    f"{profile.company_name} {profile.industry} innovation leader",
                    f"{profile.company_name} {profile.industry} market share"
                ])
            
            for query in article_queries[:self.max_articles_per_query]:
                try:
                    # Advanced Exa search with multiple strategies
                    search_strategies = [
                        {"type": "neural", "use_autoprompt": True, "num_results": 6},
                        {"type": "keyword", "num_results": 4}
                    ]
                    
                    for strategy in search_strategies:
                        results = self.exa_client.search_and_contents(
                            query=query,
                            **strategy,
                            text=True,
                            highlights=True,
                            start_published_date="2020-01-01",  # Focus on recent content
                            include_domains=["techcrunch.com", "forbes.com", "bloomberg.com", "reuters.com", "wsj.com", "ft.com", "businessinsider.com"],
                            exclude_domains=["reddit.com", "twitter.com", "facebook.com"]
                        )
                        
                        profile.total_sources_analyzed += len(results.results)
                        
                        for result in results.results:
                            article = await self._process_article_result_enhanced(result, profile.company_name)
                            if article and article.relevance_score > self.quality_threshold:
                                # Check for duplicates
                                if not any(existing.url == article.url for existing in articles):
                                    articles.append(article)
                    
                    # Add source tracking
                    source = ResearchSource(
                        name="Exa API - Articles",
                        type="exa_api",
                        url=f"exa.ai/search?q={query}",
                        reliability_score=0.9
                    )
                    profile.sources_used.append(source)
                    
                    # Rate limiting
                    await asyncio.sleep(0.5)
                    
                except Exception as e:
                    logger.error(f"Error searching articles for query '{query}': {e}")
                    continue
            
            # Enhanced article processing with AI analysis
            if self.claude_client and articles:
                articles = await self._enhance_articles_with_ai(articles, profile.company_name)
            
            # Sort by relevance and quality, take top articles
            articles.sort(key=lambda x: (x.relevance_score, len(x.key_quotes), x.word_count or 0), reverse=True)
            profile.notable_articles = articles[:self.max_total_articles]
            
            logger.info(f"Found {len(profile.notable_articles)} notable articles from {profile.total_sources_analyzed} sources")
            
        except Exception as e:
            logger.error(f"Error in article research: {e}")
    
    async def _process_article_result_enhanced(self, result, company_name: str) -> Optional[NotableArticle]:
        """Process a search result into a NotableArticle"""
        try:
            # Extract key information
            title = result.title or "Untitled"
            url = result.url
            text = result.text or ""
            
            # Determine article type based on content and source
            article_type = self._classify_article_type(title, text, url)
            
            # Calculate relevance score
            relevance_score = self._calculate_article_relevance(title, text, company_name)
            
            # Extract summary and key quotes
            summary = self._extract_article_summary(text, company_name)
            key_quotes = self._extract_key_quotes(text, company_name)
            
            # Determine sentiment
            sentiment = self._analyze_sentiment(title, text)
            
            # Extract metadata
            source = self._extract_source_domain(url)
            word_count = len(text.split()) if text else 0
            
            return NotableArticle(
                title=title,
                url=url,
                source=source,
                article_type=article_type,
                summary=summary,
                key_quotes=key_quotes[:3],  # Top 3 quotes
                relevance_score=relevance_score,
                sentiment=sentiment,
                word_count=word_count
            )
            
        except Exception as e:
            logger.error(f"Error processing article result: {e}")
            return None
    
    def _classify_article_type(self, title: str, text: str, url: str) -> ArticleType:
        """Classify the type of article based on content"""
        title_lower = title.lower()
        text_lower = text.lower()
        url_lower = url.lower()
        
        if any(term in title_lower for term in ['interview', 'talks with', 'speaks with']):
            return ArticleType.INTERVIEW
        elif any(term in url_lower for term in ['press', 'pr', 'newsroom']):
            return ArticleType.PRESS_RELEASE
        elif any(term in url_lower for term in ['blog', 'medium', 'substack']):
            return ArticleType.BLOG_POST
        elif any(term in title_lower for term in ['analysis', 'deep dive', 'breakdown']):
            return ArticleType.ANALYSIS
        elif any(term in title_lower for term in ['profile', 'story of', 'inside']):
            return ArticleType.FEATURE
        else:
            return ArticleType.NEWS
    
    def _calculate_article_relevance(self, title: str, text: str, company_name: str) -> float:
        """Calculate how relevant an article is to the company"""
        score = 0.0
        
        # Company name mentions
        company_mentions = title.lower().count(company_name.lower()) + text.lower().count(company_name.lower())
        score += min(0.4, company_mentions * 0.1)
        
        # Quality indicators
        quality_terms = ['breakthrough', 'innovation', 'achievement', 'milestone', 'success', 'growth', 'expansion']
        quality_count = sum(1 for term in quality_terms if term in text.lower())
        score += min(0.3, quality_count * 0.05)
        
        # Source quality (basic heuristic)
        if len(text) > 1000:  # Substantial content
            score += 0.2
        
        # Recency bonus (would need published date)
        score += 0.1  # Default recency bonus
        
        return min(1.0, score)
    
    def _extract_article_summary(self, text: str, company_name: str) -> str:
        """Extract a relevant summary from article text"""
        if not text:
            return "No summary available"
        
        # Find sentences mentioning the company
        sentences = text.split('.')
        relevant_sentences = [s.strip() for s in sentences if company_name.lower() in s.lower()]
        
        if relevant_sentences:
            # Take first 2-3 relevant sentences
            summary = '. '.join(relevant_sentences[:3])
            return summary[:500] + "..." if len(summary) > 500 else summary
        else:
            # Fallback to first paragraph
            paragraphs = text.split('\n\n')
            first_paragraph = paragraphs[0] if paragraphs else text[:300]
            return first_paragraph[:300] + "..." if len(first_paragraph) > 300 else first_paragraph
    
    def _extract_key_quotes(self, text: str, company_name: str) -> List[str]:
        """Extract key quotes from article text"""
        quotes = []
        
        # Look for quoted text
        quote_patterns = [
            r'"([^"]*' + re.escape(company_name) + r'[^"]*)"',
            r'"([^"]{50,200})"'  # General quotes of reasonable length
        ]
        
        for pattern in quote_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            quotes.extend(matches[:2])  # Limit quotes per pattern
        
        # Clean and filter quotes
        cleaned_quotes = []
        for quote in quotes:
            if len(quote) > 20 and len(quote) < 300:  # Reasonable length
                cleaned_quotes.append(quote.strip())
        
        return cleaned_quotes[:5]  # Return top 5 quotes
    
    def _analyze_sentiment(self, title: str, text: str) -> str:
        """Basic sentiment analysis"""
        positive_terms = ['success', 'growth', 'breakthrough', 'achievement', 'innovation', 'expansion', 'milestone']
        negative_terms = ['challenge', 'problem', 'decline', 'loss', 'controversy', 'criticism', 'failure']
        
        content = (title + " " + text).lower()
        
        positive_count = sum(1 for term in positive_terms if term in content)
        negative_count = sum(1 for term in negative_terms if term in content)
        
        if positive_count > negative_count + 1:
            return "positive"
        elif negative_count > positive_count + 1:
            return "negative"
        else:
            return "neutral"
    
    def _extract_source_domain(self, url: str) -> str:
        """Extract domain name from URL"""
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            # Remove www. prefix
            if domain.startswith('www.'):
                domain = domain[4:]
            return domain
        except:
            return "Unknown"
    
    async def _research_recognitions(self, profile: ExtraordinaryProfile, queries: List[str]):
        """Research awards, rankings, and recognitions using comprehensive search"""
        if not self.exa_client:
            logger.warning("Exa client not available for recognition research")
            return
        
        try:
            recognitions = []
            
            # Comprehensive recognition search queries
            recognition_queries = [
                f"{profile.company_name} award winner recognition",
                f"{profile.company_name} top 100 best company list",
                f"{profile.company_name} industry leader ranking",
                f"{profile.company_name} fastest growing company award",
                f"{profile.company_name} innovation award patent recognition",
                f"{profile.company_name} workplace culture award",
                f"{profile.company_name} sustainability award ESG",
                f"{profile.company_name} customer choice award",
                f"{profile.company_name} technology excellence award",
                f"{profile.company_name} unicorn status milestone",
                f"{profile.company_name} IPO listing achievement",
                f"{profile.company_name} Forbes Fortune ranking"
            ]
            
            for query in recognition_queries:
                try:
                    results = self.exa_client.search_and_contents(
                        query=query,
                        type="neural",
                        use_autoprompt=True,
                        num_results=5,
                        text=True,
                        start_published_date="2018-01-01",
                        include_domains=["forbes.com", "fortune.com", "techcrunch.com", "bloomberg.com", "fastcompany.com", "inc.com"]
                    )
                    
                    for result in results.results:
                        recognition = await self._extract_recognition_from_content(result, profile.company_name)
                        if recognition:
                            recognitions.append(recognition)
                    
                    await asyncio.sleep(0.3)  # Rate limiting
                    
                except Exception as e:
                    logger.error(f"Error searching recognitions for query '{query}': {e}")
                    continue
            
            # Remove duplicates and sort by significance
            unique_recognitions = []
            seen_titles = set()
            
            for recognition in recognitions:
                if recognition.title not in seen_titles:
                    unique_recognitions.append(recognition)
                    seen_titles.add(recognition.title)
            
            unique_recognitions.sort(key=lambda x: x.significance_score, reverse=True)
            profile.recognitions = unique_recognitions[:15]  # Top 15 recognitions
            
            logger.info(f"Found {len(profile.recognitions)} recognitions")
            
        except Exception as e:
            logger.error(f"Error in recognition research: {e}")
    
    async def _research_extraordinary_feats(self, profile: ExtraordinaryProfile, queries: List[str]):
        """Research extraordinary achievements and feats using AI-powered analysis"""
        if not self.exa_client:
            logger.warning("Exa client not available for feats research")
            return
        
        try:
            feats = []
            
            # Comprehensive feats search queries
            feats_queries = [
                f"{profile.company_name} breakthrough achievement milestone",
                f"{profile.company_name} record breaking performance",
                f"{profile.company_name} first company to achieve",
                f"{profile.company_name} unprecedented growth scale",
                f"{profile.company_name} revolutionary innovation disruption",
                f"{profile.company_name} fastest company to reach",
                f"{profile.company_name} world record achievement",
                f"{profile.company_name} industry first innovation",
                f"{profile.company_name} remarkable turnaround success",
                f"{profile.company_name} exceptional customer growth",
                f"{profile.company_name} technical breakthrough patent",
                f"{profile.company_name} market domination leadership"
            ]
            
            feat_content = []
            
            for query in feats_queries:
                try:
                    results = self.exa_client.search_and_contents(
                        query=query,
                        type="neural",
                        use_autoprompt=True,
                        num_results=4,
                        text=True,
                        start_published_date="2019-01-01"
                    )
                    
                    for result in results.results:
                        if result.text and len(result.text) > 200:
                            feat_content.append({
                                'title': result.title,
                                'text': result.text,
                                'url': result.url,
                                'query': query
                            })
                    
                    await asyncio.sleep(0.3)
                    
                except Exception as e:
                    logger.error(f"Error searching feats for query '{query}': {e}")
                    continue
            
            # Use AI to analyze and extract extraordinary feats
            if self.claude_client and feat_content:
                feats = await self._extract_feats_with_ai(feat_content, profile.company_name)
            
            # Sort by impressiveness score
            feats.sort(key=lambda x: x.impressiveness_score, reverse=True)
            profile.extraordinary_feats = feats[:10]  # Top 10 feats
            
            logger.info(f"Found {len(profile.extraordinary_feats)} extraordinary feats")
            
        except Exception as e:
            logger.error(f"Error in feats research: {e}")
    
    async def _research_company_stats(self, profile: ExtraordinaryProfile, queries: List[str]):
        """Research comprehensive company statistics from multiple sources"""
        try:
            stats = CompanyStats()
            
            # Search for quantitative data
            if self.exa_client:
                stats_queries = [
                    f"{profile.company_name} valuation funding revenue statistics",
                    f"{profile.company_name} employee count team size growth",
                    f"{profile.company_name} customer base user metrics",
                    f"{profile.company_name} financial performance earnings",
                    f"{profile.company_name} market share competition analysis",
                    f"{profile.company_name} product usage statistics metrics"
                ]
                
                stats_content = []
                
                for query in stats_queries:
                    try:
                        results = self.exa_client.search_and_contents(
                            query=query,
                            type="neural",
                            num_results=3,
                            text=True,
                            include_domains=["crunchbase.com", "pitchbook.com", "bloomberg.com", "reuters.com"]
                        )
                        
                        for result in results.results:
                            if result.text:
                                stats_content.append(result.text)
                        
                        await asyncio.sleep(0.3)
                        
                    except Exception as e:
                        logger.error(f"Error searching stats for query '{query}': {e}")
                        continue
                
                # Extract statistics using AI
                if self.claude_client and stats_content:
                    stats = await self._extract_stats_with_ai(stats_content, profile.company_name)
            
            profile.company_stats = stats
            logger.info("Researched company statistics")
            
        except Exception as e:
            logger.error(f"Error in stats research: {e}")
            profile.company_stats = CompanyStats()
    
    async def update_existing_profile(self, profile: ExtraordinaryProfile, request: ProfileGenerationRequest) -> ExtraordinaryProfile:
        """Update an existing profile with new research"""
        logger.info(f"Updating existing profile for {profile.company_name}")
        
        # Update timestamp
        profile.last_updated = datetime.now()
        
        # Perform incremental research if needed
        if datetime.now() - profile.last_updated > timedelta(days=7):  # Weekly updates
            await self._conduct_deep_research(profile, request)
            profile.calculate_profile_scores()
            await self.save_profile(profile)
        
        return profile
    
    async def load_profile(self, company_id: str) -> Optional[ExtraordinaryProfile]:
        """Load an existing profile from storage"""
        try:
            profile_file = self.profiles_dir / f"{company_id}.json"
            if profile_file.exists():
                with open(profile_file, 'r') as f:
                    data = json.load(f)
                    return ExtraordinaryProfile(**data)
        except Exception as e:
            logger.error(f"Error loading profile for {company_id}: {e}")
        
        return None
    
    async def save_profile(self, profile: ExtraordinaryProfile):
        """Save profile to storage"""
        try:
            profile_file = self.profiles_dir / f"{profile.company_id}.json"
            with open(profile_file, 'w') as f:
                json.dump(profile.dict(), f, indent=2, default=str)
            logger.info(f"Saved profile for {profile.company_name}")
        except Exception as e:
            logger.error(f"Error saving profile: {e}")
    
    async def get_all_profiles(self) -> List[ExtraordinaryProfile]:
        """Get all generated profiles"""
        profiles = []
        try:
            for profile_file in self.profiles_dir.glob("*.json"):
                with open(profile_file, 'r') as f:
                    data = json.load(f)
                    profiles.append(ExtraordinaryProfile(**data))
        except Exception as e:
            logger.error(f"Error loading profiles: {e}")
        
        return profiles
    
    async def search_profiles(self, query: str, min_score: float = 0.0) -> List[ExtraordinaryProfile]:
        """Search profiles based on query"""
        all_profiles = await self.get_all_profiles()
        
        # Simple text-based search
        matching_profiles = []
        for profile in all_profiles:
            if (query.lower() in profile.company_name.lower() or 
                query.lower() in profile.industry.lower() or
                profile.overall_profile_score >= min_score):
                matching_profiles.append(profile)
        
        # Sort by profile score
        matching_profiles.sort(key=lambda x: x.overall_profile_score, reverse=True)
        return matching_profiles
    
    async def _enhance_articles_with_ai(self, articles: List[NotableArticle], company_name: str) -> List[NotableArticle]:
        """Enhance articles with AI-powered analysis"""
        if not self.claude_client:
            return articles
        
        try:
            for article in articles:
                if article.summary and len(article.summary) > 100:
                    # Enhance summary and extract better quotes
                    enhanced_data = await self._analyze_article_with_claude(article, company_name)
                    if enhanced_data:
                        article.summary = enhanced_data.get('enhanced_summary', article.summary)
                        article.key_quotes = enhanced_data.get('key_quotes', article.key_quotes)
                        article.relevance_score = min(1.0, article.relevance_score + enhanced_data.get('relevance_boost', 0))
            
            return articles
        except Exception as e:
            logger.error(f"Error enhancing articles with AI: {e}")
            return articles
    
    async def _analyze_article_with_claude(self, article: NotableArticle, company_name: str) -> Optional[Dict[str, Any]]:
        """Analyze article content with Claude AI"""
        try:
            prompt = f"""
            Analyze this article about {company_name} and provide:
            1. An enhanced summary (2-3 sentences) focusing on what makes this company extraordinary
            2. Extract 2-3 key quotes that highlight achievements, innovations, or impressive metrics
            3. Rate the relevance to extraordinary achievements (0.0-0.3 boost)
            
            Article Title: {article.title}
            Article Content: {article.summary[:1000]}...
            
            Respond in JSON format:
            {{
                "enhanced_summary": "...",
                "key_quotes": ["quote1", "quote2"],
                "relevance_boost": 0.1
            }}
            """
            
            response = self.claude_client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=500,
                messages=[{"role": "user", "content": prompt}]
            )
            
            return json.loads(response.content[0].text)
            
        except Exception as e:
            logger.error(f"Error analyzing article with Claude: {e}")
            return None
    
    async def _extract_recognition_from_content(self, result, company_name: str) -> Optional[Recognition]:
        """Extract recognition information from search results"""
        try:
            title = result.title or ""
            text = result.text or ""
            url = result.url
            
            # Look for recognition patterns
            recognition_patterns = [
                r'(\d{4}).*?award.*?' + re.escape(company_name),
                r'' + re.escape(company_name) + r'.*?ranked.*?(\d+)',
                r'' + re.escape(company_name) + r'.*?winner.*?(\d{4})',
                r'top.*?(\d+).*?' + re.escape(company_name),
            ]
            
            # Extract year and ranking info
            year = 2024  # Default
            rank_position = None
            
            for pattern in recognition_patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                if matches:
                    try:
                        if matches[0].isdigit():
                            potential_year = int(matches[0])
                            if 2015 <= potential_year <= 2024:
                                year = potential_year
                            elif potential_year < 100:  # Likely a ranking
                                rank_position = potential_year
                    except:
                        pass
            
            # Determine recognition type and significance
            recognition_type = RecognitionType.AWARD
            significance_score = 0.5
            
            if any(term in title.lower() for term in ['top', 'best', 'ranking']):
                recognition_type = RecognitionType.RANKING
                significance_score = 0.7
            
            if any(term in title.lower() for term in ['forbes', 'fortune', 'techcrunch']):
                significance_score = min(1.0, significance_score + 0.2)
            
            # Extract organization name
            organization = self._extract_source_domain(url)
            if 'forbes' in organization:
                organization = 'Forbes'
            elif 'fortune' in organization:
                organization = 'Fortune'
            elif 'techcrunch' in organization:
                organization = 'TechCrunch'
            
            return Recognition(
                title=title[:100],  # Truncate long titles
                organization=organization,
                year=year,
                recognition_type=recognition_type,
                description=text[:300] + "..." if len(text) > 300 else text,
                url=url,
                rank_position=rank_position,
                significance_score=significance_score
            )
            
        except Exception as e:
            logger.error(f"Error extracting recognition: {e}")
            return None
    
    async def _extract_feats_with_ai(self, feat_content: List[Dict], company_name: str) -> List[ExtraordinaryFeat]:
        """Extract extraordinary feats using Claude AI analysis"""
        if not self.claude_client:
            return []
        
        try:
            # Combine content for analysis
            combined_content = "\n\n".join([f"Title: {item['title']}\nContent: {item['text'][:800]}" for item in feat_content[:5]])
            
            prompt = f"""
            Analyze the following content about {company_name} and identify extraordinary feats or achievements.
            Look for:
            - Record-breaking performance or growth
            - Industry-first innovations
            - Unprecedented scale or speed
            - Revolutionary breakthroughs
            - Remarkable turnarounds or comebacks
            
            Content:
            {combined_content}
            
            Extract up to 5 extraordinary feats in JSON format:
            {{
                "feats": [
                    {{
                        "title": "Brief feat title",
                        "description": "Detailed description of the achievement",
                        "feat_type": "technical|business|social_impact|innovation|growth|leadership",
                        "impact_description": "Why this is extraordinary and its impact",
                        "impressiveness_score": 0.8,
                        "metrics": {{"key": "value"}}
                    }}
                ]
            }}
            """
            
            response = self.claude_client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=1500,
                messages=[{"role": "user", "content": prompt}]
            )
            
            result = json.loads(response.content[0].text)
            feats = []
            
            for feat_data in result.get('feats', []):
                try:
                    feat_type = FeatType(feat_data.get('feat_type', 'business'))
                except ValueError:
                    feat_type = FeatType.BUSINESS
                
                feat = ExtraordinaryFeat(
                    title=feat_data.get('title', ''),
                    description=feat_data.get('description', ''),
                    feat_type=feat_type,
                    impact_description=feat_data.get('impact_description', ''),
                    impressiveness_score=min(1.0, max(0.0, feat_data.get('impressiveness_score', 0.5))),
                    metrics=feat_data.get('metrics', {}),
                    sources=[item['url'] for item in feat_content[:3]]
                )
                feats.append(feat)
            
            return feats
            
        except Exception as e:
            logger.error(f"Error extracting feats with AI: {e}")
            return []
    
    async def _extract_stats_with_ai(self, stats_content: List[str], company_name: str) -> CompanyStats:
        """Extract company statistics using Claude AI"""
        if not self.claude_client:
            return CompanyStats()
        
        try:
            combined_content = "\n\n".join(stats_content[:3])
            
            prompt = f"""
            Extract quantitative statistics about {company_name} from the following content.
            Look for metrics like valuation, revenue, employee count, user count, growth rates, etc.
            
            Content:
            {combined_content[:2000]}
            
            Extract statistics in JSON format (use null for unknown values):
            {{
                "valuation": 1000000000,
                "revenue": 500000000,
                "employee_count": 1000,
                "user_count": 10000000,
                "funding_raised": 200000000,
                "revenue_growth_rate": 0.5,
                "employee_growth_rate": 0.3
            }}
            """
            
            response = self.claude_client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=500,
                messages=[{"role": "user", "content": prompt}]
            )
            
            stats_data = json.loads(response.content[0].text)
            
            return CompanyStats(
                valuation=stats_data.get('valuation'),
                revenue=stats_data.get('revenue'),
                employee_count=stats_data.get('employee_count'),
                user_count=stats_data.get('user_count'),
                funding_raised=stats_data.get('funding_raised'),
                revenue_growth_rate=stats_data.get('revenue_growth_rate'),
                employee_growth_rate=stats_data.get('employee_growth_rate')
            )
            
        except Exception as e:
            logger.error(f"Error extracting stats with AI: {e}")
            return CompanyStats()
