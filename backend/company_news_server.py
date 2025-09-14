#!/usr/bin/env python3
"""
Company News API Server
FastAPI server for company news endpoints
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import sys
from pathlib import Path

# Add API routes
sys.path.append('/Users/sutharsikakumar/project1-1/backend')
from api.company_news_routes import router as news_router

app = FastAPI(
    title="Company News API",
    description="API for fetching latest company news using NewsAPI and multi-source data",
    version="1.0.0"
)

# Add CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include news routes
app.include_router(news_router, prefix="/api/v1", tags=["Company News"])

@app.get("/")
async def root():
    return {
        "message": "Company News API",
        "version": "1.0.0",
        "endpoints": {
            "company_news": "/api/v1/company-news",
            "news_summary": "/api/v1/company-news/summary", 
            "single_company": "/api/v1/company-news/{company_name}",
            "categories": "/api/v1/company-news/categories"
        }
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "company-news-api"}

if __name__ == "__main__":
    print("🚀 Starting Company News API Server...")
    print("📰 NewsAPI integration enabled")
    print("🌐 Server will be available at: http://localhost:8000")
    print("📋 API Documentation: http://localhost:8000/docs")
    print("-" * 60)
    
    uvicorn.run(
        "company_news_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
