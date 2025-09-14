"""
Tandemn Distributed Inference Integration Service
Enhances M&A intelligence platform with distributed AI processing
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import json
import aiohttp
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class TandemnRequest:
    """Request structure for Tandemn API"""
    model: str
    prompt: str
    max_tokens: int = 1000
    temperature: float = 0.7
    request_id: str = None

@dataclass
class TandemnResponse:
    """Response structure from Tandemn API"""
    request_id: str
    model: str
    response: str
    processing_time: float
    confidence: float = None

class TandemnDistributedService:
    """
    Service for leveraging Tandemn's distributed inference backend
    Enables parallel processing of M&A intelligence tasks
    """
    
    def __init__(self, api_key: str, base_url: str = "https://api.tandemn.com"):
        self.api_key = api_key
        self.base_url = base_url
        self.session = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def distributed_document_analysis(self, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Process multiple M&A documents in parallel using distributed inference
        
        Args:
            documents: List of documents with 'content', 'type', 'source' fields
            
        Returns:
            List of structured M&A events extracted from documents
        """
        # Create parallel processing tasks
        tasks = []
        
        for i, doc in enumerate(documents):
            # Create specialized prompts based on document type
            prompt = self._create_extraction_prompt(doc)
            
            request = TandemnRequest(
                model="gpt-4",  # or whatever models Tandemn supports
                prompt=prompt,
                max_tokens=1500,
                temperature=0.3,  # Lower temperature for factual extraction
                request_id=f"doc_analysis_{i}_{datetime.now().timestamp()}"
            )
            
            task = self._send_inference_request(request)
            tasks.append(task)
        
        # Execute all tasks in parallel
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process responses and extract structured data
        extracted_events = []
        for i, response in enumerate(responses):
            if isinstance(response, Exception):
                logger.error(f"Document {i} processing failed: {response}")
                continue
            
            try:
                events = self._parse_extraction_response(response, documents[i])
                extracted_events.extend(events)
            except Exception as e:
                logger.error(f"Failed to parse response for document {i}: {e}")
        
        return extracted_events
    
    async def multi_model_confidence_scoring(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Use multiple models in parallel to assess event confidence from different perspectives
        
        Args:
            event: M&A event to assess
            
        Returns:
            Enhanced event with multi-model confidence scores
        """
        # Create different assessment prompts for various models
        assessment_tasks = [
            # Financial analysis perspective
            self._create_financial_assessment_task(event),
            # Legal/regulatory perspective  
            self._create_legal_assessment_task(event),
            # Market impact perspective
            self._create_market_assessment_task(event),
            # Source credibility perspective
            self._create_credibility_assessment_task(event)
        ]
        
        # Execute assessments in parallel
        responses = await asyncio.gather(*assessment_tasks, return_exceptions=True)
        
        # Combine multi-model assessments
        confidence_scores = {}
        for i, response in enumerate(responses):
            if not isinstance(response, Exception):
                try:
                    score_data = json.loads(response.response)
                    perspective = ["financial", "legal", "market", "credibility"][i]
                    confidence_scores[f"{perspective}_confidence"] = score_data
                except Exception as e:
                    logger.error(f"Failed to parse {i}th assessment: {e}")
        
        # Calculate weighted overall confidence
        overall_confidence = self._calculate_weighted_confidence(confidence_scores)
        
        # Enhance event with multi-model insights
        enhanced_event = event.copy()
        enhanced_event.update({
            'tandemn_multi_model_confidence': overall_confidence,
            'confidence_breakdown': confidence_scores,
            'processing_method': 'distributed_multi_model',
            'processed_at': datetime.now().isoformat()
        })
        
        return enhanced_event
    
    async def vision_document_analysis(self, image_documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Analyze financial charts, graphs, and visual documents using vision models
        
        Args:
            image_documents: List of documents with image data or URLs
            
        Returns:
            Extracted financial data and insights from visual content
        """
        vision_tasks = []
        
        for i, img_doc in enumerate(image_documents):
            # Create vision analysis prompt
            prompt = self._create_vision_analysis_prompt(img_doc)
            
            request = TandemnRequest(
                model="gpt-4-vision",  # or Tandemn's vision model
                prompt=prompt,
                max_tokens=1000,
                request_id=f"vision_analysis_{i}_{datetime.now().timestamp()}"
            )
            
            task = self._send_vision_request(request, img_doc)
            vision_tasks.append(task)
        
        # Process vision analysis in parallel
        responses = await asyncio.gather(*vision_tasks, return_exceptions=True)
        
        # Extract structured insights from visual content
        visual_insights = []
        for i, response in enumerate(responses):
            if not isinstance(response, Exception):
                try:
                    insight = self._parse_vision_response(response, image_documents[i])
                    visual_insights.append(insight)
                except Exception as e:
                    logger.error(f"Failed to parse vision response {i}: {e}")
        
        return visual_insights
    
    async def real_time_sentiment_analysis(self, news_streams: List[str]) -> Dict[str, Any]:
        """
        Perform distributed sentiment analysis on multiple news streams simultaneously
        
        Args:
            news_streams: List of news article texts or social media posts
            
        Returns:
            Aggregated sentiment analysis with market impact predictions
        """
        sentiment_tasks = []
        
        for i, news_text in enumerate(news_streams):
            prompt = f"""
            Analyze the sentiment and market impact of this M&A-related news:
            
            Text: {news_text}
            
            Provide JSON response with:
            - sentiment_score: -1 to 1 (negative to positive)
            - confidence: 0 to 1
            - market_impact: "high", "medium", "low"
            - key_entities: list of companies mentioned
            - impact_reasoning: brief explanation
            """
            
            request = TandemnRequest(
                model="gpt-3.5-turbo",  # Faster model for sentiment
                prompt=prompt,
                max_tokens=500,
                temperature=0.1,
                request_id=f"sentiment_{i}_{datetime.now().timestamp()}"
            )
            
            sentiment_tasks.append(self._send_inference_request(request))
        
        # Execute sentiment analysis in parallel
        responses = await asyncio.gather(*sentiment_tasks, return_exceptions=True)
        
        # Aggregate sentiment insights
        sentiment_data = []
        for response in responses:
            if not isinstance(response, Exception):
                try:
                    sentiment_info = json.loads(response.response)
                    sentiment_data.append(sentiment_info)
                except Exception as e:
                    logger.error(f"Failed to parse sentiment response: {e}")
        
        # Calculate market-wide sentiment trends
        aggregated_sentiment = self._aggregate_sentiment_analysis(sentiment_data)
        
        return aggregated_sentiment
    
    async def _send_inference_request(self, request: TandemnRequest) -> TandemnResponse:
        """Send inference request to Tandemn API"""
        payload = {
            "model": request.model,
            "messages": [{"role": "user", "content": request.prompt}],
            "max_tokens": request.max_tokens,
            "temperature": request.temperature
        }
        
        async with self.session.post(f"{self.base_url}/v1/chat/completions", json=payload) as response:
            if response.status == 200:
                data = await response.json()
                return TandemnResponse(
                    request_id=request.request_id,
                    model=request.model,
                    response=data["choices"][0]["message"]["content"],
                    processing_time=data.get("processing_time", 0)
                )
            else:
                raise Exception(f"Tandemn API error: {response.status}")
    
    async def _send_vision_request(self, request: TandemnRequest, image_doc: Dict[str, Any]) -> TandemnResponse:
        """Send vision analysis request to Tandemn API"""
        # Implementation depends on Tandemn's vision API format
        # This is a placeholder structure
        payload = {
            "model": request.model,
            "messages": [
                {
                    "role": "user", 
                    "content": [
                        {"type": "text", "text": request.prompt},
                        {"type": "image_url", "image_url": {"url": image_doc.get("image_url")}}
                    ]
                }
            ],
            "max_tokens": request.max_tokens
        }
        
        async with self.session.post(f"{self.base_url}/v1/vision/analyze", json=payload) as response:
            if response.status == 200:
                data = await response.json()
                return TandemnResponse(
                    request_id=request.request_id,
                    model=request.model,
                    response=data["analysis"],
                    processing_time=data.get("processing_time", 0)
                )
            else:
                raise Exception(f"Tandemn Vision API error: {response.status}")
    
    def _create_extraction_prompt(self, document: Dict[str, Any]) -> str:
        """Create specialized extraction prompt based on document type"""
        doc_type = document.get('type', 'general')
        content = document.get('content', '')
        
        if doc_type == 'press_release':
            return f"""
            Extract M&A information from this press release:
            
            {content}
            
            Return JSON with:
            - source_company: acquiring/investing company
            - target_company: target/acquired company  
            - deal_type: "acquisition", "merger", "partnership", "funding"
            - deal_value: numeric value in USD (null if not mentioned)
            - deal_date: YYYY-MM-DD format
            - description: brief summary
            - confidence: 0-1 score for extraction quality
            """
        elif doc_type == 'sec_filing':
            return f"""
            Extract M&A transaction details from this SEC filing:
            
            {content}
            
            Focus on: transaction structure, parties involved, financial terms, closing conditions.
            Return structured JSON with high precision.
            """
        else:
            return f"""
            Analyze this document for M&A-related information:
            
            {content}
            
            Extract any deals, partnerships, or corporate transactions mentioned.
            """
    
    def _create_financial_assessment_task(self, event: Dict[str, Any]) -> asyncio.Task:
        """Create financial assessment task"""
        prompt = f"""
        Assess the financial credibility of this M&A event from a financial analysis perspective:
        
        Event: {json.dumps(event, indent=2)}
        
        Consider: deal valuation reasonableness, financial capacity of parties, market conditions.
        Return JSON with financial_confidence (0-1) and reasoning.
        """
        
        request = TandemnRequest(
            model="gpt-4",
            prompt=prompt,
            temperature=0.2,
            request_id=f"financial_assessment_{datetime.now().timestamp()}"
        )
        
        return asyncio.create_task(self._send_inference_request(request))
    
    def _create_legal_assessment_task(self, event: Dict[str, Any]) -> asyncio.Task:
        """Create legal/regulatory assessment task"""
        prompt = f"""
        Assess the legal and regulatory feasibility of this M&A event:
        
        Event: {json.dumps(event, indent=2)}
        
        Consider: regulatory approval likelihood, antitrust issues, legal structure validity.
        Return JSON with legal_confidence (0-1) and regulatory_risks.
        """
        
        request = TandemnRequest(
            model="gpt-4",
            prompt=prompt,
            temperature=0.2,
            request_id=f"legal_assessment_{datetime.now().timestamp()}"
        )
        
        return asyncio.create_task(self._send_inference_request(request))
    
    def _create_market_assessment_task(self, event: Dict[str, Any]) -> asyncio.Task:
        """Create market impact assessment task"""
        prompt = f"""
        Assess the market impact and strategic rationale of this M&A event:
        
        Event: {json.dumps(event, indent=2)}
        
        Consider: strategic fit, market timing, competitive dynamics, synergy potential.
        Return JSON with market_confidence (0-1) and impact_analysis.
        """
        
        request = TandemnRequest(
            model="gpt-4",
            prompt=prompt,
            temperature=0.3,
            request_id=f"market_assessment_{datetime.now().timestamp()}"
        )
        
        return asyncio.create_task(self._send_inference_request(request))
    
    def _create_credibility_assessment_task(self, event: Dict[str, Any]) -> asyncio.Task:
        """Create source credibility assessment task"""
        prompt = f"""
        Assess the source credibility and information quality of this M&A event:
        
        Event: {json.dumps(event, indent=2)}
        
        Consider: source reliability, information completeness, cross-validation potential.
        Return JSON with credibility_confidence (0-1) and quality_factors.
        """
        
        request = TandemnRequest(
            model="gpt-3.5-turbo",
            prompt=prompt,
            temperature=0.1,
            request_id=f"credibility_assessment_{datetime.now().timestamp()}"
        )
        
        return asyncio.create_task(self._send_inference_request(request))
    
    def _create_vision_analysis_prompt(self, image_doc: Dict[str, Any]) -> str:
        """Create prompt for vision model analysis"""
        return """
        Analyze this financial chart/graph/infographic for M&A-related information:
        
        Extract:
        - Financial metrics (revenue, valuation, growth rates)
        - Deal timelines or milestones
        - Company performance indicators
        - Market trends or comparisons
        - Any numerical data relevant to M&A analysis
        
        Return structured JSON with extracted data and confidence scores.
        """
    
    def _parse_extraction_response(self, response: TandemnResponse, original_doc: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parse extraction response into structured events"""
        try:
            extracted_data = json.loads(response.response)
            
            # Ensure it's a list
            if isinstance(extracted_data, dict):
                extracted_data = [extracted_data]
            
            # Add metadata to each event
            for event in extracted_data:
                event.update({
                    'extraction_source': 'tandemn_distributed',
                    'original_document': original_doc.get('source', 'unknown'),
                    'processing_time': response.processing_time,
                    'model_used': response.model
                })
            
            return extracted_data
            
        except json.JSONDecodeError:
            logger.error(f"Failed to parse JSON response: {response.response}")
            return []
    
    def _parse_vision_response(self, response: TandemnResponse, image_doc: Dict[str, Any]) -> Dict[str, Any]:
        """Parse vision analysis response"""
        try:
            vision_data = json.loads(response.response)
            vision_data.update({
                'analysis_source': 'tandemn_vision',
                'image_source': image_doc.get('source', 'unknown'),
                'processing_time': response.processing_time
            })
            return vision_data
        except json.JSONDecodeError:
            logger.error(f"Failed to parse vision response: {response.response}")
            return {}
    
    def _calculate_weighted_confidence(self, confidence_scores: Dict[str, Any]) -> float:
        """Calculate weighted overall confidence from multi-model assessments"""
        weights = {
            'financial_confidence': 0.3,
            'legal_confidence': 0.25,
            'market_confidence': 0.25,
            'credibility_confidence': 0.2
        }
        
        total_confidence = 0.0
        total_weight = 0.0
        
        for perspective, weight in weights.items():
            if perspective in confidence_scores:
                score_data = confidence_scores[perspective]
                if isinstance(score_data, dict) and 'confidence' in score_data:
                    total_confidence += score_data['confidence'] * weight
                    total_weight += weight
        
        return total_confidence / total_weight if total_weight > 0 else 0.5
    
    def _aggregate_sentiment_analysis(self, sentiment_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Aggregate sentiment analysis from multiple sources"""
        if not sentiment_data:
            return {'overall_sentiment': 0.0, 'confidence': 0.0, 'sample_size': 0}
        
        total_sentiment = sum(item.get('sentiment_score', 0) for item in sentiment_data)
        avg_sentiment = total_sentiment / len(sentiment_data)
        
        avg_confidence = sum(item.get('confidence', 0) for item in sentiment_data) / len(sentiment_data)
        
        # Extract most mentioned companies
        all_entities = []
        for item in sentiment_data:
            all_entities.extend(item.get('key_entities', []))
        
        entity_counts = {}
        for entity in all_entities:
            entity_counts[entity] = entity_counts.get(entity, 0) + 1
        
        top_entities = sorted(entity_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            'overall_sentiment': avg_sentiment,
            'confidence': avg_confidence,
            'sample_size': len(sentiment_data),
            'top_mentioned_companies': [entity for entity, count in top_entities],
            'market_impact_distribution': self._calculate_impact_distribution(sentiment_data)
        }
    
    def _calculate_impact_distribution(self, sentiment_data: List[Dict[str, Any]]) -> Dict[str, int]:
        """Calculate distribution of market impact assessments"""
        impact_counts = {'high': 0, 'medium': 0, 'low': 0}
        
        for item in sentiment_data:
            impact = item.get('market_impact', 'low')
            if impact in impact_counts:
                impact_counts[impact] += 1
        
        return impact_counts

# Integration functions for existing system
async def enhance_ma_events_with_tandemn(events: List[Dict[str, Any]], api_key: str) -> List[Dict[str, Any]]:
    """
    Enhance M&A events using Tandemn distributed inference
    """
    async with TandemnDistributedService(api_key) as tandemn_service:
        enhanced_events = []
        
        # Process events in batches for efficiency
        batch_size = 10
        for i in range(0, len(events), batch_size):
            batch = events[i:i + batch_size]
            
            # Create enhancement tasks for this batch
            enhancement_tasks = [
                tandemn_service.multi_model_confidence_scoring(event)
                for event in batch
            ]
            
            # Process batch in parallel
            enhanced_batch = await asyncio.gather(*enhancement_tasks, return_exceptions=True)
            
            # Add successfully enhanced events
            for enhanced_event in enhanced_batch:
                if not isinstance(enhanced_event, Exception):
                    enhanced_events.append(enhanced_event)
                else:
                    logger.error(f"Event enhancement failed: {enhanced_event}")
        
        return enhanced_events

async def process_documents_with_tandemn(documents: List[Dict[str, Any]], api_key: str) -> List[Dict[str, Any]]:
    """
    Process multiple documents using Tandemn distributed inference
    """
    async with TandemnDistributedService(api_key) as tandemn_service:
        # Separate text and image documents
        text_docs = [doc for doc in documents if doc.get('type') != 'image']
        image_docs = [doc for doc in documents if doc.get('type') == 'image']
        
        # Process both types in parallel
        tasks = []
        if text_docs:
            tasks.append(tandemn_service.distributed_document_analysis(text_docs))
        if image_docs:
            tasks.append(tandemn_service.vision_document_analysis(image_docs))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Combine results
        all_extracted_events = []
        for result in results:
            if not isinstance(result, Exception) and isinstance(result, list):
                all_extracted_events.extend(result)
        
        return all_extracted_events
