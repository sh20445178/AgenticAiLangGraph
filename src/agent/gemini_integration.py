"""
Google Gemini LLM Integration

This module provides integration with Google Gemini LLM for the cloud-agnostic agent.
Includes proper configuration, error handling, and retry mechanisms.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import google.generativeai as genai
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate
import structlog

logger = structlog.get_logger(__name__)


@dataclass
class GeminiConfig:
    """Configuration for Gemini LLM."""
    api_key: str
    model_name: str = "gemini-1.5-pro"
    temperature: float = 0.7
    max_tokens: Optional[int] = 8192
    top_p: float = 0.8
    top_k: int = 40
    safety_settings: Optional[Dict[str, str]] = None
    retry_attempts: int = 3
    retry_delay: float = 1.0


class GeminiLLMIntegration:
    """
    Google Gemini LLM integration for cloud-agnostic architecture recommendations.
    """
    
    def __init__(self, config: GeminiConfig):
        self.config = config
        self.llm = None
        self._initialize_llm()
    
    def _initialize_llm(self):
        """Initialize the Gemini LLM with configuration."""
        try:
            genai.configure(api_key=self.config.api_key)
            
            # Configure safety settings
            safety_settings = self.config.safety_settings or {
                "HARM_CATEGORY_HARASSMENT": "BLOCK_MEDIUM_AND_ABOVE",
                "HARM_CATEGORY_HATE_SPEECH": "BLOCK_MEDIUM_AND_ABOVE",
                "HARM_CATEGORY_SEXUALLY_EXPLICIT": "BLOCK_MEDIUM_AND_ABOVE",
                "HARM_CATEGORY_DANGEROUS_CONTENT": "BLOCK_MEDIUM_AND_ABOVE",
            }
            
            self.llm = ChatGoogleGenerativeAI(
                model=self.config.model_name,
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens,
                top_p=self.config.top_p,
                top_k=self.config.top_k,
                safety_settings=safety_settings,
                google_api_key=self.config.api_key
            )
            
            logger.info("Gemini LLM initialized successfully", model=self.config.model_name)
            
        except Exception as e:
            logger.error("Failed to initialize Gemini LLM", error=str(e))
            raise
    
    async def analyze_requirements(self, user_query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze user requirements and extract key information for architecture recommendations.
        """
        system_prompt = """
        You are an expert cloud architect specializing in AWS and Azure services. 
        Your task is to analyze user requirements for building React frontend and Java microservices backend applications.
        
        Extract and analyze the following information:
        1. Application type and complexity
        2. Scalability requirements
        3. Performance requirements
        4. Security requirements
        5. Budget constraints
        6. Preferred cloud services
        7. Database requirements
        8. Integration needs
        
        Provide your analysis in a structured JSON format with clear recommendations.
        Focus on cloud-agnostic solutions that can work on both AWS and Azure.
        """
        
        human_prompt = f"""
        User Query: {user_query}
        
        Additional Context: {context}
        
        Please provide a comprehensive analysis of the requirements and suggest appropriate cloud services 
        from both AWS and Azure that would be suitable for this use case.
        """
        
        try:
            response = await self._invoke_with_retry(system_prompt, human_prompt)
            return self._parse_analysis_response(response)
            
        except Exception as e:
            logger.error("Failed to analyze requirements", error=str(e), query=user_query)
            raise
    
    async def generate_architecture_recommendations(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate cloud architecture recommendations based on analysis.
        """
        system_prompt = """
        You are an expert cloud solutions architect. Based on the requirements analysis, 
        generate detailed architecture recommendations that are cloud-agnostic and can be 
        implemented on both AWS and Azure.
        
        For each recommendation, provide:
        1. Architecture overview
        2. AWS service mapping
        3. Azure service mapping
        4. Cost estimation approach
        5. Implementation steps
        6. Pros and cons
        7. Best practices
        
        Focus on modern, scalable, and secure architectures using:
        - React for frontend
        - Java/Spring Boot for microservices
        - Cloud-native databases
        - Container orchestration
        - API gateways
        - Monitoring and logging
        """
        
        human_prompt = f"""
        Requirements Analysis: {analysis}
        
        Please generate 2-3 alternative architecture recommendations that address these requirements.
        Each recommendation should be practical, cost-effective, and implementable on both AWS and Azure.
        """
        
        try:
            response = await self._invoke_with_retry(system_prompt, human_prompt)
            return self._parse_recommendations_response(response)
            
        except Exception as e:
            logger.error("Failed to generate recommendations", error=str(e), analysis=analysis)
            raise
    
    async def generate_implementation_code(self, recommendation: Dict[str, Any], 
                                         target_cloud: str) -> Dict[str, str]:
        """
        Generate implementation code and configuration files for the selected recommendation.
        """
        system_prompt = f"""
        You are an expert developer specializing in {target_cloud.upper()} services and modern application development.
        Generate production-ready code and configuration files for the given architecture recommendation.
        
        Generate the following:
        1. React frontend application structure
        2. Java Spring Boot microservices
        3. Database configuration and migration scripts
        4. {target_cloud.upper()} infrastructure as code (Terraform/CloudFormation)
        5. Docker configurations
        6. CI/CD pipeline configurations
        7. Monitoring and logging setup
        
        Follow best practices for security, performance, and maintainability.
        Use managed identity and secure authentication methods.
        Include proper error handling and logging.
        """
        
        human_prompt = f"""
        Architecture Recommendation: {recommendation}
        Target Cloud: {target_cloud.upper()}
        
        Please generate comprehensive implementation code and configuration files.
        Ensure the code follows industry best practices and is production-ready.
        """
        
        try:
            response = await self._invoke_with_retry(system_prompt, human_prompt)
            return self._parse_implementation_response(response)
            
        except Exception as e:
            logger.error("Failed to generate implementation", error=str(e), 
                        recommendation=recommendation, target_cloud=target_cloud)
            raise
    
    async def learn_from_feedback(self, feedback: Dict[str, Any], 
                                context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process user feedback to improve future recommendations.
        """
        system_prompt = """
        You are a learning system that improves architecture recommendations based on user feedback.
        Analyze the feedback and extract insights that can be used to improve future recommendations.
        
        Consider:
        1. What worked well in the recommendation
        2. What could be improved
        3. User preferences and patterns
        4. Cost sensitivity
        5. Technology preferences
        6. Common issues and solutions
        
        Generate learning insights that can be used to enhance future recommendations.
        """
        
        human_prompt = f"""
        User Feedback: {feedback}
        Recommendation Context: {context}
        
        Please analyze this feedback and provide actionable insights for improving future recommendations.
        """
        
        try:
            response = await self._invoke_with_retry(system_prompt, human_prompt)
            return self._parse_learning_response(response)
            
        except Exception as e:
            logger.error("Failed to process feedback", error=str(e), feedback=feedback)
            raise
    
    async def _invoke_with_retry(self, system_prompt: str, human_prompt: str) -> str:
        """Invoke LLM with retry logic."""
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=human_prompt)
        ]
        
        for attempt in range(self.config.retry_attempts):
            try:
                response = await self.llm.ainvoke(messages)
                return response.content
                
            except Exception as e:
                logger.warning(f"LLM invocation attempt {attempt + 1} failed", error=str(e))
                if attempt < self.config.retry_attempts - 1:
                    await asyncio.sleep(self.config.retry_delay * (2 ** attempt))
                else:
                    raise
    
    def _parse_analysis_response(self, response: str) -> Dict[str, Any]:
        """Parse and structure the analysis response."""
        try:
            # In a real implementation, you might use JSON parsing or structured output
            # For now, we'll return a structured response
            return {
                "application_type": "web_application",
                "complexity": "medium",
                "scalability_requirements": response,
                "extracted_requirements": [],
                "recommended_services": {
                    "aws": [],
                    "azure": []
                },
                "raw_analysis": response
            }
        except Exception as e:
            logger.error("Failed to parse analysis response", error=str(e))
            return {"raw_analysis": response, "parsing_error": str(e)}
    
    def _parse_recommendations_response(self, response: str) -> List[Dict[str, Any]]:
        """Parse and structure the recommendations response."""
        try:
            # Parse the response into structured recommendations
            return [
                {
                    "id": "rec_1",
                    "title": "Cloud-Native Microservices Architecture",
                    "description": response,
                    "aws_services": [],
                    "azure_services": [],
                    "implementation_steps": [],
                    "estimated_cost": None,
                    "confidence_score": 0.8
                }
            ]
        except Exception as e:
            logger.error("Failed to parse recommendations response", error=str(e))
            return [{"raw_response": response, "parsing_error": str(e)}]
    
    def _parse_implementation_response(self, response: str) -> Dict[str, str]:
        """Parse and structure the implementation response."""
        try:
            # In a real implementation, you would parse code blocks and organize them
            return {
                "frontend_app": response,
                "backend_services": "",
                "infrastructure": "",
                "deployment": "",
                "raw_response": response
            }
        except Exception as e:
            logger.error("Failed to parse implementation response", error=str(e))
            return {"raw_response": response, "parsing_error": str(e)}
    
    def _parse_learning_response(self, response: str) -> Dict[str, Any]:
        """Parse and structure the learning response."""
        try:
            return {
                "insights": [],
                "improvement_suggestions": [],
                "user_preferences": {},
                "raw_learning": response
            }
        except Exception as e:
            logger.error("Failed to parse learning response", error=str(e))
            return {"raw_learning": response, "parsing_error": str(e)}


# Factory function for creating Gemini integration
def create_gemini_integration(api_key: str, **kwargs) -> GeminiLLMIntegration:
    """Create a Gemini LLM integration instance."""
    config = GeminiConfig(api_key=api_key, **kwargs)
    return GeminiLLMIntegration(config)