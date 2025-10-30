#!/usr/bin/env python3
"""
Basic Example: Using the Cloud-Agnostic Agent

This example demonstrates how to use the LangGraph agent to get
cloud-agnostic architecture recommendations for a React + Java microservices application.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the src directory to the Python path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from agent.agent import create_agent


async def basic_example():
    """Basic example of using the cloud-agnostic agent."""
    
    # Initialize the agent with Gemini API key
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if not gemini_api_key:
        print("Error: GEMINI_API_KEY environment variable is required")
        return
    
    print("🤖 Initializing Cloud-Agnostic Agent...")
    agent = create_agent(gemini_api_key)
    
    # Example user query
    user_query = """
    I need to build a scalable e-commerce application with the following requirements:
    - React frontend for customer interface
    - Java Spring Boot microservices for backend (user service, product service, order service)
    - PostgreSQL database for transactional data
    - Redis for caching
    - File storage for product images
    - Authentication and authorization
    - Monitoring and logging
    - Should be deployable on both AWS and Azure
    - Budget-conscious but performance is important
    """
    
    print(f"📝 Processing query: {user_query[:100]}...")
    
    try:
        # Process the query
        result = await agent.process_query(user_query)
        
        print("\\n✅ Processing completed!")
        print(f"Current step: {result.get('current_step', 'unknown')}")
        print(f"Recommendations generated: {len(result.get('recommendations', []))}")
        
        # Display recommendations
        recommendations = result.get("recommendations", [])
        if recommendations:
            print("\\n🎯 Top Recommendations:")
            for i, rec in enumerate(recommendations[:3], 1):
                print(f"\\n{i}. {rec.title}")
                print(f"   Description: {rec.description[:200]}...")
                print(f"   Confidence Score: {rec.confidence_score:.2f}")
                print(f"   Resources: {len(rec.resources)} cloud resources")
        
        # Display generated templates
        templates = result.get("generated_templates", [])
        if templates:
            print(f"\\n📦 Generated Templates: {len(templates)}")
            for template in templates:
                print(f"   - {template.name} ({template.type})")
        
        # Display configuration files
        config_files = result.get("configuration_files", {})
        if config_files:
            print(f"\\n⚙️  Configuration Files Generated:")
            for cloud_provider, files in config_files.items():
                print(f"   {cloud_provider.upper()}: {len(files) if isinstance(files, dict) else 1} files")
        
        return result
        
    except Exception as e:
        print(f"❌ Error processing query: {str(e)}")
        return None


async def feedback_example(agent, session_result):
    """Example of providing feedback to the agent."""
    
    if not session_result or not session_result.get("recommendations"):
        print("No recommendations available for feedback")
        return
    
    print("\\n📊 Providing feedback to improve future recommendations...")
    
    # Simulate user feedback
    feedback = {
        "session_id": "example_session_1",
        "recommendation_id": session_result["recommendations"][0].recommendation_id,
        "rating": 4.5,
        "text": "Great recommendation! I especially liked the focus on cost optimization and the detailed AWS/Azure comparison.",
        "preferences": {
            "cost_importance": "high",
            "performance_importance": "medium",
            "preferred_cloud": "aws"
        }
    }
    
    try:
        feedback_result = await agent.provide_feedback("example_session_1", feedback)
        
        print("✅ Feedback processed successfully!")
        print(f"Insights generated: {feedback_result.get('insights_generated', 0)}")
        
        # Get learning summary
        learning_summary = agent.feedback_processor.get_learning_summary()
        print(f"Total feedback entries: {learning_summary.get('total_feedback_entries', 0)}")
        
    except Exception as e:
        print(f"❌ Error processing feedback: {str(e)}")


async def multi_query_example():
    """Example with multiple queries to demonstrate learning."""
    
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if not gemini_api_key:
        print("Error: GEMINI_API_KEY environment variable is required")
        return
    
    agent = create_agent(gemini_api_key)
    
    queries = [
        {
            "query": "Simple blog application with React frontend and Java backend, minimal cost",
            "feedback": {"rating": 4.0, "preferences": {"cost_importance": "very_high"}}
        },
        {
            "query": "High-performance trading platform with React dashboard and Java microservices",
            "feedback": {"rating": 3.5, "preferences": {"performance_importance": "very_high"}}
        },
        {
            "query": "Enterprise CRM system with React frontend, Java backend, need high security",
            "feedback": {"rating": 4.5, "preferences": {"security_importance": "very_high"}}
        }
    ]
    
    print("🔄 Processing multiple queries to demonstrate learning...")
    
    for i, item in enumerate(queries, 1):
        print(f"\\n--- Query {i} ---")
        result = await agent.process_query(item["query"])
        
        if result and result.get("recommendations"):
            print(f"Generated {len(result['recommendations'])} recommendations")
            
            # Provide feedback
            feedback = {
                "session_id": f"session_{i}",
                "recommendation_id": result["recommendations"][0].recommendation_id,
                "rating": item["feedback"]["rating"],
                "preferences": item["feedback"]["preferences"]
            }
            
            await agent.provide_feedback(f"session_{i}", feedback)
    
    # Show learning summary
    learning_summary = agent.feedback_processor.get_learning_summary()
    print("\\n📈 Learning Summary:")
    print(f"Total feedback: {learning_summary.get('total_feedback_entries', 0)}")
    print(f"Average rating: {learning_summary.get('feedback_statistics', {}).get('average_rating', 0):.2f}")
    print(f"Top insights: {len(learning_summary.get('top_insights', []))}")


def main():
    """Main function to run examples."""
    print("🚀 Cloud-Agnostic Agent Examples")
    print("=================================\\n")
    
    # Check environment
    if not os.getenv("GEMINI_API_KEY"):
        print("⚠️  Please set GEMINI_API_KEY environment variable")
        print("   You can get an API key from: https://makersuite.google.com/app/apikey")
        return
    
    print("Select an example to run:")
    print("1. Basic Example - Single query with recommendations")
    print("2. Feedback Example - Single query with feedback loop")
    print("3. Multi-Query Example - Multiple queries with learning")
    
    choice = input("\\nEnter your choice (1-3): ").strip()
    
    if choice == "1":
        asyncio.run(basic_example())
    elif choice == "2":
        async def run_feedback_example():
            result = await basic_example()
            if result:
                gemini_api_key = os.getenv("GEMINI_API_KEY")
                agent = create_agent(gemini_api_key)
                await feedback_example(agent, result)
        asyncio.run(run_feedback_example())
    elif choice == "3":
        asyncio.run(multi_query_example())
    else:
        print("Invalid choice. Please run the script again and select 1, 2, or 3.")


if __name__ == "__main__":
    main()