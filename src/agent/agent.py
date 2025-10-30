"""
Main LangGraph Agent

This module implements the core LangGraph agent that orchestrates cloud-agnostic
architecture recommendations using Google Gemini LLM.
"""

import asyncio
import logging
from typing import Dict, Any, List
from datetime import datetime
import uuid

from langgraph import StateGraph, END
from langgraph.graph import Graph

from .state import AgentState, create_initial_state, update_state_with_feedback
from .state import UserRequirement, CloudResource, Recommendation, ApplicationTemplate
from .gemini_integration import GeminiLLMIntegration, create_gemini_integration
from ..cloud_adapters.aws_adapter import AWSAdapter
from ..cloud_adapters.azure_adapter import AzureAdapter
from ..learning.feedback_processor import FeedbackProcessor

import structlog

logger = structlog.get_logger(__name__)


class CloudAgnosticAgent:
    """
    LangGraph-based agent for cloud-agnostic architecture recommendations.
    """
    
    def __init__(self, gemini_api_key: str, aws_config: Dict[str, Any] = None, 
                 azure_config: Dict[str, Any] = None):
        self.gemini_integration = create_gemini_integration(gemini_api_key)
        self.aws_adapter = AWSAdapter(aws_config or {})
        self.azure_adapter = AzureAdapter(azure_config or {})
        self.feedback_processor = FeedbackProcessor()
        
        # Build the LangGraph workflow
        self.workflow = self._build_workflow()
        self.app = self.workflow.compile()
        
        logger.info("CloudAgnosticAgent initialized successfully")
    
    def _build_workflow(self) -> StateGraph:
        """Build the LangGraph workflow for the agent."""
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("analyze_requirements", self._analyze_requirements_node)
        workflow.add_node("generate_recommendations", self._generate_recommendations_node)
        workflow.add_node("select_recommendation", self._select_recommendation_node)
        workflow.add_node("generate_implementation", self._generate_implementation_node)
        workflow.add_node("process_feedback", self._process_feedback_node)
        workflow.add_node("generate_templates", self._generate_templates_node)
        
        # Set entry point
        workflow.set_entry_point("analyze_requirements")
        
        # Add edges
        workflow.add_edge("analyze_requirements", "generate_recommendations")
        workflow.add_edge("generate_recommendations", "select_recommendation")
        workflow.add_edge("select_recommendation", "generate_implementation")
        workflow.add_edge("generate_implementation", "generate_templates")
        workflow.add_edge("generate_templates", END)
        workflow.add_edge("process_feedback", "analyze_requirements")
        
        return workflow
    
    async def process_query(self, user_query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Process a user query and generate cloud-agnostic recommendations.
        """
        try:
            # Initialize state
            initial_state = create_initial_state(user_query)
            if context:
                initial_state.update(context)
            
            # Run the workflow
            result = await self.app.ainvoke(initial_state)
            
            logger.info("Query processed successfully", 
                       query=user_query, 
                       recommendations_count=len(result.get("recommendations", [])))
            
            return result
            
        except Exception as e:
            logger.error("Failed to process query", error=str(e), query=user_query)
            raise
    
    async def provide_feedback(self, session_id: str, feedback: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process user feedback and update the agent's learning.
        """
        try:
            # Load the session state (in a real implementation, you'd load from storage)
            state = self._load_session_state(session_id)
            
            # Update state with feedback
            updated_state = update_state_with_feedback(state, feedback)
            
            # Process feedback for learning
            result = await self.app.ainvoke(updated_state, {"start_from": "process_feedback"})
            
            logger.info("Feedback processed successfully", 
                       session_id=session_id, 
                       feedback_type=feedback.get("type"))
            
            return result
            
        except Exception as e:
            logger.error("Failed to process feedback", error=str(e), session_id=session_id)
            raise
    
    async def _analyze_requirements_node(self, state: AgentState) -> AgentState:
        """Analyze user requirements and extract key information."""
        try:
            logger.info("Analyzing requirements", query=state["user_query"])
            
            context = {
                "preferred_providers": state.get("preferred_cloud_providers", []),
                "budget": state.get("budget_constraints"),
                "architecture_type": state.get("architecture_type")
            }
            
            analysis = await self.gemini_integration.analyze_requirements(
                state["user_query"], context
            )
            
            state["analysis_results"] = analysis
            state["current_step"] = "requirements_analyzed"
            state["next_actions"] = ["generate_recommendations"]
            
            # Extract structured requirements
            requirements = self._extract_requirements_from_analysis(analysis)
            state["user_requirements"] = requirements
            
            return state
            
        except Exception as e:
            logger.error("Failed to analyze requirements", error=str(e))
            state["errors"].append(f"Requirements analysis failed: {str(e)}")
            return state
    
    async def _generate_recommendations_node(self, state: AgentState) -> AgentState:
        """Generate architecture recommendations based on analysis."""
        try:
            logger.info("Generating recommendations")
            
            recommendations_data = await self.gemini_integration.generate_architecture_recommendations(
                state["analysis_results"]
            )
            
            recommendations = []
            for rec_data in recommendations_data:
                recommendation = Recommendation(
                    recommendation_id=str(uuid.uuid4()),
                    title=rec_data.get("title", "Architecture Recommendation"),
                    description=rec_data.get("description", ""),
                    confidence_score=rec_data.get("confidence_score", 0.7),
                    resources=[],  # Will be populated by cloud adapters
                    implementation_steps=rec_data.get("implementation_steps", [])
                )
                recommendations.append(recommendation)
            
            # Enhance recommendations with cloud-specific resources
            for recommendation in recommendations:
                # Get AWS resources
                aws_resources = await self.aws_adapter.get_recommended_resources(
                    state["analysis_results"], recommendation
                )
                
                # Get Azure resources
                azure_resources = await self.azure_adapter.get_recommended_resources(
                    state["analysis_results"], recommendation
                )
                
                recommendation.resources.extend(aws_resources + azure_resources)
            
            state["recommendations"] = recommendations
            state["current_step"] = "recommendations_generated"
            state["next_actions"] = ["select_recommendation"]
            
            return state
            
        except Exception as e:
            logger.error("Failed to generate recommendations", error=str(e))
            state["errors"].append(f"Recommendation generation failed: {str(e)}")
            return state
    
    async def _select_recommendation_node(self, state: AgentState) -> AgentState:
        """Select the best recommendation based on criteria."""
        try:
            logger.info("Selecting best recommendation")
            
            recommendations = state["recommendations"]
            
            if not recommendations:
                state["warnings"].append("No recommendations generated")
                return state
            
            # Simple selection logic - choose highest confidence score
            # In a real implementation, this could be more sophisticated
            selected = max(recommendations, key=lambda r: r.confidence_score)
            
            state["selected_recommendation"] = selected
            state["current_step"] = "recommendation_selected"
            state["next_actions"] = ["generate_implementation"]
            
            return state
            
        except Exception as e:
            logger.error("Failed to select recommendation", error=str(e))
            state["errors"].append(f"Recommendation selection failed: {str(e)}")
            return state
    
    async def _generate_implementation_node(self, state: AgentState) -> AgentState:
        """Generate implementation code and configurations."""
        try:
            logger.info("Generating implementation")
            
            selected_rec = state["selected_recommendation"]
            if not selected_rec:
                state["warnings"].append("No recommendation selected for implementation")
                return state
            
            # Generate implementation for both AWS and Azure
            aws_implementation = await self.gemini_integration.generate_implementation_code(
                selected_rec.__dict__, "aws"
            )
            
            azure_implementation = await self.gemini_integration.generate_implementation_code(
                selected_rec.__dict__, "azure"
            )
            
            state["configuration_files"] = {
                "aws": aws_implementation,
                "azure": azure_implementation
            }
            
            state["current_step"] = "implementation_generated"
            state["next_actions"] = ["generate_templates"]
            
            return state
            
        except Exception as e:
            logger.error("Failed to generate implementation", error=str(e))
            state["errors"].append(f"Implementation generation failed: {str(e)}")
            return state
    
    async def _generate_templates_node(self, state: AgentState) -> AgentState:
        """Generate application templates and deployment scripts."""
        try:
            logger.info("Generating templates")
            
            selected_rec = state["selected_recommendation"]
            if not selected_rec:
                return state
            
            templates = []
            
            # Generate React frontend template
            frontend_template = ApplicationTemplate(
                name="react-frontend",
                type="frontend",
                framework="react",
                cloud_resources=[r for r in selected_rec.resources if "frontend" in r.resource_type.lower()],
                configuration=state["configuration_files"]
            )
            templates.append(frontend_template)
            
            # Generate Java microservices template
            backend_template = ApplicationTemplate(
                name="java-microservices",
                type="backend",
                framework="spring-boot",
                cloud_resources=[r for r in selected_rec.resources if "backend" in r.resource_type.lower()],
                configuration=state["configuration_files"]
            )
            templates.append(backend_template)
            
            state["generated_templates"] = templates
            state["current_step"] = "completed"
            state["next_actions"] = []
            
            return state
            
        except Exception as e:
            logger.error("Failed to generate templates", error=str(e))
            state["errors"].append(f"Template generation failed: {str(e)}")
            return state
    
    async def _process_feedback_node(self, state: AgentState) -> AgentState:
        """Process user feedback for learning."""
        try:
            logger.info("Processing feedback")
            
            if not state["feedback_history"]:
                return state
            
            latest_feedback = state["feedback_history"][-1]
            
            # Use Gemini to process feedback
            learning_insights = await self.gemini_integration.learn_from_feedback(
                latest_feedback, state["analysis_results"]
            )
            
            state["learning_insights"] = learning_insights
            
            # Process with feedback processor for systematic learning
            self.feedback_processor.process_feedback(latest_feedback, state)
            
            state["current_step"] = "feedback_processed"
            
            return state
            
        except Exception as e:
            logger.error("Failed to process feedback", error=str(e))
            state["errors"].append(f"Feedback processing failed: {str(e)}")
            return state
    
    def _extract_requirements_from_analysis(self, analysis: Dict[str, Any]) -> List[UserRequirement]:
        """Extract structured requirements from analysis."""
        # This would parse the LLM analysis and extract structured requirements
        return [
            UserRequirement(
                requirement_type="scalability",
                description="Application needs to scale based on user load",
                priority="high",
                tags=["performance", "scalability"]
            )
        ]
    
    def _load_session_state(self, session_id: str) -> AgentState:
        """Load session state (placeholder for persistent storage)."""
        # In a real implementation, this would load from a database
        return create_initial_state("Previous session query")
    
    async def get_status(self, session_id: str) -> Dict[str, Any]:
        """Get the current status of a processing session."""
        # In a real implementation, this would check session status
        return {
            "session_id": session_id,
            "status": "completed",
            "current_step": "ready",
            "timestamp": datetime.now().isoformat()
        }


# Factory function for creating the agent
def create_agent(gemini_api_key: str, **kwargs) -> CloudAgnosticAgent:
    """Create a CloudAgnosticAgent instance."""
    return CloudAgnosticAgent(gemini_api_key, **kwargs)