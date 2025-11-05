#!/usr/bin/env python3
"""
Advanced Example: FastAPI Web Service with the Cloud-Agnostic Agent

This example demonstrates how to create a web service using FastAPI
that exposes the cloud-agnostic agent capabilities via REST API.
"""

import asyncio
import os
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

# Add the src directory to the Python path
sys.path.append(str(Path(__file__).parent.parent / "src"))

try:
    from fastapi import FastAPI, HTTPException, BackgroundTasks
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import JSONResponse
    from pydantic import BaseModel, Field
    import uvicorn
except ImportError:
    print("Please install FastAPI and uvicorn: pip install fastapi uvicorn")
    sys.exit(1)

from agent.agent import create_agent


# Pydantic models for request/response
class QueryRequest(BaseModel):
    query: str = Field(..., description="User query for architecture recommendations")
    context: Optional[Dict[str, Any]] = Field(default={}, description="Additional context")
    preferred_cloud_providers: Optional[List[str]] = Field(default=[], description="Preferred cloud providers")
    budget_constraints: Optional[float] = Field(default=None, description="Budget constraints in USD")


class FeedbackRequest(BaseModel):
    session_id: str = Field(..., description="Session identifier")
    recommendation_id: str = Field(..., description="Recommendation identifier")
    rating: float = Field(..., ge=1.0, le=5.0, description="Rating from 1.0 to 5.0")
    feedback_text: Optional[str] = Field(default=None, description="Optional feedback text")
    preferences: Optional[Dict[str, Any]] = Field(default={}, description="User preferences")


class RecommendationResponse(BaseModel):
    session_id: str
    status: str
    current_step: str
    recommendations_count: int
    recommendations: List[Dict[str, Any]]
    templates_count: int
    configuration_files: Dict[str, Any]
    processing_time: float
    timestamp: str


class FeedbackResponse(BaseModel):
    processed: bool
    feedback_id: str
    insights_generated: int
    learning_summary: Dict[str, Any]
    timestamp: str


# Global agent instance
agent = None


def initialize_agent():
    """Initialize the global agent instance."""
    global agent
    
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if not gemini_api_key:
        raise ValueError("GEMINI_API_KEY environment variable is required")
    
    aws_config = {
        "region": os.getenv("AWS_REGION", "us-east-1")
    }
    
    azure_config = {
        "subscription_id": os.getenv("AZURE_SUBSCRIPTION_ID"),
        "location": os.getenv("AZURE_LOCATION", "eastus")
    }
    
    agent = create_agent(gemini_api_key, aws_config=aws_config, azure_config=azure_config)
    print("✅ Cloud-Agnostic Agent initialized successfully")


# FastAPI app
app = FastAPI(
    title="Cloud-Agnostic Architecture Agent API",
    description="AI-powered agent for generating cloud-agnostic architecture recommendations",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Initialize the agent on startup."""
    try:
        initialize_agent()
    except Exception as e:
        print(f"❌ Failed to initialize agent: {str(e)}")
        raise


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Cloud-Agnostic Architecture Agent API",
        "version": "1.0.0",
        "description": "AI-powered agent for generating cloud-agnostic architecture recommendations",
        "endpoints": {
            "recommendations": "/recommendations",
            "feedback": "/feedback",
            "learning": "/learning",
            "health": "/health",
            "docs": "/docs"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    global agent
    
    return {
        "status": "healthy" if agent is not None else "unhealthy",
        "timestamp": datetime.now().isoformat(),
        "agent_initialized": agent is not None,
        "version": "1.0.0"
    }


@app.post("/recommendations", response_model=RecommendationResponse)
async def get_recommendations(request: QueryRequest, background_tasks: BackgroundTasks):
    """
    Generate architecture recommendations based on user query.
    """
    global agent
    
    if agent is None:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    start_time = datetime.now()
    session_id = f"session_{int(start_time.timestamp())}"
    
    try:
        # Prepare context
        context = request.context.copy()
        if request.preferred_cloud_providers:
            context["preferred_cloud_providers"] = request.preferred_cloud_providers
        if request.budget_constraints:
            context["budget_constraints"] = request.budget_constraints
        
        # Process query
        result = await agent.process_query(request.query, context)
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        # Prepare response
        recommendations = []
        for rec in result.get("recommendations", []):
            recommendations.append({
                "id": rec.recommendation_id,
                "title": rec.title,
                "description": rec.description,
                "confidence_score": rec.confidence_score,
                "resources_count": len(rec.resources),
                "implementation_steps": rec.implementation_steps,
                "estimated_cost": rec.estimated_cost
            })
        
        response = RecommendationResponse(
            session_id=session_id,
            status="completed",
            current_step=result.get("current_step", "completed"),
            recommendations_count=len(recommendations),
            recommendations=recommendations,
            templates_count=len(result.get("generated_templates", [])),
            configuration_files=result.get("configuration_files", {}),
            processing_time=processing_time,
            timestamp=datetime.now().isoformat()
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process query: {str(e)}")


@app.post("/feedback", response_model=FeedbackResponse)
async def submit_feedback(request: FeedbackRequest):
    """
    Submit feedback for a recommendation to improve future suggestions.
    """
    global agent
    
    if agent is None:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    try:
        feedback_data = {
            "session_id": request.session_id,
            "recommendation_id": request.recommendation_id,
            "rating": request.rating,
            "text": request.feedback_text,
            "preferences": request.preferences
        }
        
        result = await agent.provide_feedback(request.session_id, feedback_data)
        
        # Get learning summary
        learning_summary = agent.feedback_processor.get_learning_summary()
        
        response = FeedbackResponse(
            processed=result.get("processed", False),
            feedback_id=result.get("feedback_id", ""),
            insights_generated=result.get("insights_generated", 0),
            learning_summary=learning_summary,
            timestamp=datetime.now().isoformat()
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process feedback: {str(e)}")


@app.get("/learning")
async def get_learning_summary():
    """
    Get the current learning summary and insights.
    """
    global agent
    
    if agent is None:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    try:
        learning_summary = agent.feedback_processor.get_learning_summary()
        return {
            "learning_summary": learning_summary,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get learning summary: {str(e)}")


@app.get("/templates/{template_type}")
async def get_template_info(template_type: str):
    """
    Get information about available templates.
    """
    available_templates = {
        "react": {
            "name": "React Frontend Template",
            "description": "Cloud-agnostic React application template with TypeScript, Material-UI, and authentication",
            "features": ["TypeScript", "Material-UI", "PWA", "Testing", "Cloud Authentication"],
            "cloud_providers": ["AWS", "Azure"]
        },
        "java": {
            "name": "Java Spring Boot Microservices Template",
            "description": "Cloud-agnostic Spring Boot microservices template with JPA, Security, and Monitoring",
            "features": ["Spring Boot 3.x", "JPA", "Security", "Caching", "Monitoring", "Docker"],
            "cloud_providers": ["AWS", "Azure"]
        }
    }
    
    if template_type not in available_templates:
        raise HTTPException(status_code=404, detail="Template type not found")
    
    return available_templates[template_type]


@app.get("/status/{session_id}")
async def get_session_status(session_id: str):
    """
    Get the status of a processing session.
    """
    global agent
    
    if agent is None:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    try:
        status = await agent.get_status(session_id)
        return status
        
    except Exception as e:
        return JSONResponse(
            status_code=404,
            content={"detail": f"Session not found: {str(e)}"}
        )


def main():
    """Main function to run the FastAPI server."""
    print("🚀 Starting Cloud-Agnostic Agent API Server")
    print("==========================================\\n")
    
    # Check environment
    if not os.getenv("GEMINI_API_KEY"):
        print("⚠️  Please set GEMINI_API_KEY environment variable")
        print("   You can get an API key from: https://makersuite.google.com/app/apikey")
        return
    
    # Configuration
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8000"))
    debug = os.getenv("DEBUG", "false").lower() == "true"
    
    print(f"🌐 Server will be available at: http://{host}:{port}")
    print(f"📖 API Documentation: http://{host}:{port}/docs")
    print(f"🔧 ReDoc Documentation: http://{host}:{port}/redoc")
    print()
    
    # Run server
    uvicorn.run(
        "advanced_api:app",
        host=host,
        port=port,
        reload=debug,
        log_level="info" if not debug else "debug"
    )


if __name__ == "__main__":
    main()