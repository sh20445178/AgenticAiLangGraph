"""
Cloud Agnostic Agent State Management

This module defines the state structure for the LangGraph agent that provides
cloud-agnostic solutions for React frontend and Java microservices backend applications.
"""

from typing import TypedDict, List, Optional, Dict, Any, Literal
from dataclasses import dataclass
from enum import Enum


class CloudProvider(Enum):
    """Supported cloud providers."""
    AWS = "aws"
    AZURE = "azure"


class ArchitectureType(Enum):
    """Supported architecture types."""
    MICROSERVICES = "microservices"
    MONOLITH = "monolith"
    SERVERLESS = "serverless"


class DatabaseType(Enum):
    """Supported database types."""
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"
    MONGODB = "mongodb"
    COSMOSDB = "cosmosdb"
    DYNAMODB = "dynamodb"


@dataclass
class UserRequirement:
    """User requirement data structure."""
    requirement_type: str
    description: str
    priority: str  # high, medium, low
    tags: List[str]


@dataclass
class CloudResource:
    """Cloud resource configuration."""
    resource_type: str
    provider: CloudProvider
    configuration: Dict[str, Any]
    estimated_cost: Optional[float] = None


@dataclass
class ApplicationTemplate:
    """Application template structure."""
    name: str
    type: str  # frontend, backend, database
    framework: str  # react, spring-boot, etc.
    cloud_resources: List[CloudResource]
    configuration: Dict[str, Any]


@dataclass
class Recommendation:
    """Agent recommendation structure."""
    recommendation_id: str
    title: str
    description: str
    confidence_score: float
    resources: List[CloudResource]
    implementation_steps: List[str]
    estimated_cost: Optional[float] = None
    feedback_score: Optional[float] = None


class AgentState(TypedDict):
    """
    LangGraph agent state containing all information needed for cloud-agnostic recommendations.
    """
    # User input and context
    user_query: str
    user_requirements: List[UserRequirement]
    preferred_cloud_providers: List[CloudProvider]
    budget_constraints: Optional[float]
    
    # Architecture preferences
    architecture_type: Optional[ArchitectureType]
    frontend_framework: Optional[str]
    backend_framework: Optional[str]
    database_preference: Optional[DatabaseType]
    
    # Agent reasoning and recommendations
    analysis_results: Dict[str, Any]
    recommendations: List[Recommendation]
    selected_recommendation: Optional[Recommendation]
    
    # Generated artifacts
    generated_templates: List[ApplicationTemplate]
    configuration_files: Dict[str, str]
    deployment_scripts: Dict[str, str]
    
    # Learning and feedback
    feedback_history: List[Dict[str, Any]]
    learning_insights: Dict[str, Any]
    
    # Conversation state
    conversation_history: List[Dict[str, str]]
    current_step: str
    next_actions: List[str]
    
    # Error handling
    errors: List[str]
    warnings: List[str]


def create_initial_state(user_query: str) -> AgentState:
    """Create initial agent state from user query."""
    return AgentState(
        user_query=user_query,
        user_requirements=[],
        preferred_cloud_providers=[],
        budget_constraints=None,
        architecture_type=None,
        frontend_framework=None,
        backend_framework=None,
        database_preference=None,
        analysis_results={},
        recommendations=[],
        selected_recommendation=None,
        generated_templates=[],
        configuration_files={},
        deployment_scripts={},
        feedback_history=[],
        learning_insights={},
        conversation_history=[{"role": "user", "content": user_query}],
        current_step="analysis",
        next_actions=["analyze_requirements"],
        errors=[],
        warnings=[]
    )


def update_state_with_feedback(state: AgentState, feedback: Dict[str, Any]) -> AgentState:
    """Update agent state with user feedback."""
    state["feedback_history"].append(feedback)
    
    # Update recommendation scores based on feedback
    if "recommendation_id" in feedback and feedback.get("rating"):
        for rec in state["recommendations"]:
            if rec.recommendation_id == feedback["recommendation_id"]:
                rec.feedback_score = feedback["rating"]
                break
    
    return state