"""
Feedback Processing System

This module implements the self-training mechanism for the agent to learn from
user feedback and improve recommendations over time.
"""

import asyncio
import json
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
from collections import defaultdict

import structlog

logger = structlog.get_logger(__name__)


@dataclass
class FeedbackEntry:
    """Structure for storing user feedback."""
    feedback_id: str
    session_id: str
    recommendation_id: str
    user_rating: float  # 1-5 scale
    feedback_text: Optional[str]
    feedback_type: str  # positive, negative, neutral
    timestamp: datetime
    user_preferences: Dict[str, Any]
    context: Dict[str, Any]


@dataclass
class LearningInsight:
    """Structure for storing learning insights."""
    insight_id: str
    category: str
    description: str
    confidence_score: float
    supporting_evidence: List[str]
    created_at: datetime
    applied_count: int = 0


class FeedbackProcessor:
    """
    Processes user feedback to generate learning insights and improve recommendations.
    """
    
    def __init__(self, storage_path: str = "learning_data.json"):
        self.storage_path = storage_path
        self.feedback_history: List[FeedbackEntry] = []
        self.learning_insights: List[LearningInsight] = []
        self.preference_patterns: Dict[str, Any] = defaultdict(dict)
        self.load_learning_data()
    
    def process_feedback(self, feedback: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process new user feedback and update learning insights.
        """
        try:
            # Create feedback entry
            feedback_entry = FeedbackEntry(
                feedback_id=feedback.get("feedback_id", self._generate_id()),
                session_id=feedback.get("session_id", ""),
                recommendation_id=feedback.get("recommendation_id", ""),
                user_rating=float(feedback.get("rating", 3.0)),
                feedback_text=feedback.get("text"),
                feedback_type=self._classify_feedback_type(feedback.get("rating", 3.0)),
                timestamp=datetime.now(),
                user_preferences=feedback.get("preferences", {}),
                context=context
            )
            
            # Store feedback
            self.feedback_history.append(feedback_entry)
            
            # Analyze feedback patterns
            insights = self._analyze_feedback_patterns()
            
            # Update preference patterns
            self._update_preference_patterns(feedback_entry)
            
            # Generate new learning insights
            new_insights = self._generate_learning_insights(feedback_entry)
            self.learning_insights.extend(new_insights)
            
            # Save learning data
            self.save_learning_data()
            
            logger.info("Feedback processed successfully", 
                       feedback_id=feedback_entry.feedback_id,
                       rating=feedback_entry.user_rating,
                       new_insights_count=len(new_insights))
            
            return {
                "processed": True,
                "feedback_id": feedback_entry.feedback_id,
                "insights_generated": len(new_insights),
                "learning_summary": insights
            }
            
        except Exception as e:
            logger.error("Failed to process feedback", error=str(e))
            return {"processed": False, "error": str(e)}
    
    def get_recommendations_adjustments(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get recommendation adjustments based on learned patterns.
        """
        try:
            adjustments = {
                "preference_weights": self._get_preference_weights(context),
                "service_priorities": self._get_service_priorities(context),
                "cost_sensitivity": self._get_cost_sensitivity(context),
                "technology_preferences": self._get_technology_preferences(context),
                "architecture_patterns": self._get_architecture_patterns(context)
            }
            
            logger.debug("Generated recommendation adjustments", adjustments=adjustments)
            return adjustments
            
        except Exception as e:
            logger.error("Failed to generate recommendation adjustments", error=str(e))
            return {}
    
    def get_learning_summary(self) -> Dict[str, Any]:
        """
        Get a summary of current learning state.
        """
        try:
            feedback_stats = self._calculate_feedback_stats()
            top_insights = sorted(self.learning_insights, 
                                key=lambda x: x.confidence_score, reverse=True)[:10]
            
            return {
                "total_feedback_entries": len(self.feedback_history),
                "feedback_statistics": feedback_stats,
                "top_insights": [asdict(insight) for insight in top_insights],
                "preference_patterns": dict(self.preference_patterns),
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error("Failed to generate learning summary", error=str(e))
            return {}
    
    def _classify_feedback_type(self, rating: float) -> str:
        """Classify feedback type based on rating."""
        if rating >= 4.0:
            return "positive"
        elif rating <= 2.0:
            return "negative"
        else:
            return "neutral"
    
    def _analyze_feedback_patterns(self) -> Dict[str, Any]:
        """Analyze patterns in feedback history."""
        if not self.feedback_history:
            return {}
        
        patterns = {
            "average_rating": sum(f.user_rating for f in self.feedback_history) / len(self.feedback_history),
            "rating_distribution": self._get_rating_distribution(),
            "common_positive_aspects": self._extract_positive_aspects(),
            "common_negative_aspects": self._extract_negative_aspects(),
            "preferred_cloud_providers": self._get_cloud_provider_preferences(),
            "architecture_preferences": self._get_architecture_preferences()
        }
        
        return patterns
    
    def _get_rating_distribution(self) -> Dict[str, int]:
        """Get distribution of ratings."""
        distribution = defaultdict(int)
        for feedback in self.feedback_history:
            rating_range = f"{int(feedback.user_rating)}-{int(feedback.user_rating) + 1}"
            distribution[rating_range] += 1
        return dict(distribution)
    
    def _extract_positive_aspects(self) -> List[str]:
        """Extract common positive aspects from feedback."""
        positive_feedback = [f for f in self.feedback_history if f.feedback_type == "positive"]
        aspects = []
        
        for feedback in positive_feedback:
            if feedback.feedback_text:
                # Simple keyword extraction - in production, use NLP
                if "cost" in feedback.feedback_text.lower():
                    aspects.append("cost-effective")
                if "performance" in feedback.feedback_text.lower():
                    aspects.append("high-performance")
                if "scalable" in feedback.feedback_text.lower():
                    aspects.append("scalable")
                if "secure" in feedback.feedback_text.lower():
                    aspects.append("secure")
        
        return list(set(aspects))
    
    def _extract_negative_aspects(self) -> List[str]:
        """Extract common negative aspects from feedback."""
        negative_feedback = [f for f in self.feedback_history if f.feedback_type == "negative"]
        aspects = []
        
        for feedback in negative_feedback:
            if feedback.feedback_text:
                # Simple keyword extraction - in production, use NLP
                if "expensive" in feedback.feedback_text.lower():
                    aspects.append("too-expensive")
                if "complex" in feedback.feedback_text.lower():
                    aspects.append("too-complex")
                if "slow" in feedback.feedback_text.lower():
                    aspects.append("poor-performance")
        
        return list(set(aspects))
    
    def _get_cloud_provider_preferences(self) -> Dict[str, float]:
        """Get cloud provider preferences from feedback."""
        provider_ratings = defaultdict(list)
        
        for feedback in self.feedback_history:
            provider = feedback.context.get("cloud_provider")
            if provider:
                provider_ratings[provider].append(feedback.user_rating)
        
        preferences = {}
        for provider, ratings in provider_ratings.items():
            preferences[provider] = sum(ratings) / len(ratings) if ratings else 0.0
        
        return preferences
    
    def _get_architecture_preferences(self) -> Dict[str, float]:
        """Get architecture pattern preferences from feedback."""
        arch_ratings = defaultdict(list)
        
        for feedback in self.feedback_history:
            arch_type = feedback.context.get("architecture_type")
            if arch_type:
                arch_ratings[arch_type].append(feedback.user_rating)
        
        preferences = {}
        for arch_type, ratings in arch_ratings.items():
            preferences[arch_type] = sum(ratings) / len(ratings) if ratings else 0.0
        
        return preferences
    
    def _update_preference_patterns(self, feedback: FeedbackEntry):
        """Update preference patterns based on new feedback."""
        # Update user preferences
        for key, value in feedback.user_preferences.items():
            if key not in self.preference_patterns:
                self.preference_patterns[key] = {"values": [], "ratings": []}
            
            self.preference_patterns[key]["values"].append(value)
            self.preference_patterns[key]["ratings"].append(feedback.user_rating)
        
        # Update context-based patterns
        for key, value in feedback.context.items():
            pattern_key = f"context_{key}"
            if pattern_key not in self.preference_patterns:
                self.preference_patterns[pattern_key] = {"values": [], "ratings": []}
            
            self.preference_patterns[pattern_key]["values"].append(value)
            self.preference_patterns[pattern_key]["ratings"].append(feedback.user_rating)
    
    def _generate_learning_insights(self, feedback: FeedbackEntry) -> List[LearningInsight]:
        """Generate new learning insights from feedback."""
        insights = []
        
        # Cost sensitivity insight
        if feedback.user_rating >= 4.0 and "cost" in str(feedback.context).lower():
            insights.append(LearningInsight(
                insight_id=self._generate_id(),
                category="cost_optimization",
                description="Users prefer cost-effective solutions",
                confidence_score=0.8,
                supporting_evidence=[f"Positive feedback on cost-effective recommendation: {feedback.feedback_id}"],
                created_at=datetime.now()
            ))
        
        # Performance preference insight
        if feedback.user_rating >= 4.0 and "performance" in str(feedback.feedback_text or "").lower():
            insights.append(LearningInsight(
                insight_id=self._generate_id(),
                category="performance_optimization",
                description="Users value high-performance architectures",
                confidence_score=0.7,
                supporting_evidence=[f"Positive feedback on performance: {feedback.feedback_id}"],
                created_at=datetime.now()
            ))
        
        # Cloud provider preference insight
        provider = feedback.context.get("cloud_provider")
        if provider and feedback.user_rating >= 4.0:
            insights.append(LearningInsight(
                insight_id=self._generate_id(),
                category="cloud_provider_preference",
                description=f"Users show preference for {provider} solutions",
                confidence_score=0.6,
                supporting_evidence=[f"Positive feedback for {provider}: {feedback.feedback_id}"],
                created_at=datetime.now()
            ))
        
        return insights
    
    def _get_preference_weights(self, context: Dict[str, Any]) -> Dict[str, float]:
        """Calculate preference weights based on learned patterns."""
        weights = {
            "cost": 1.0,
            "performance": 1.0,
            "scalability": 1.0,
            "security": 1.0,
            "complexity": 1.0
        }
        
        # Adjust weights based on learning insights
        for insight in self.learning_insights:
            if insight.category == "cost_optimization":
                weights["cost"] += insight.confidence_score * 0.5
            elif insight.category == "performance_optimization":
                weights["performance"] += insight.confidence_score * 0.5
        
        return weights
    
    def _get_service_priorities(self, context: Dict[str, Any]) -> Dict[str, float]:
        """Get service priorities based on learned patterns."""
        priorities = defaultdict(float)
        
        for insight in self.learning_insights:
            if "database" in insight.description.lower():
                priorities["database"] += insight.confidence_score
            if "cache" in insight.description.lower():
                priorities["cache"] += insight.confidence_score
            if "monitoring" in insight.description.lower():
                priorities["monitoring"] += insight.confidence_score
        
        return dict(priorities)
    
    def _get_cost_sensitivity(self, context: Dict[str, Any]) -> float:
        """Calculate cost sensitivity based on feedback patterns."""
        cost_feedback = [f for f in self.feedback_history 
                        if "cost" in str(f.feedback_text or "").lower()]
        
        if not cost_feedback:
            return 0.5  # Default moderate sensitivity
        
        avg_rating = sum(f.user_rating for f in cost_feedback) / len(cost_feedback)
        return min(1.0, max(0.0, (5.0 - avg_rating) / 5.0))  # Higher sensitivity for lower ratings
    
    def _get_technology_preferences(self, context: Dict[str, Any]) -> Dict[str, float]:
        """Get technology preferences based on feedback."""
        tech_preferences = defaultdict(float)
        
        for feedback in self.feedback_history:
            if feedback.user_rating >= 4.0:
                # Extract technology mentions from context
                for key, value in feedback.context.items():
                    if "technology" in key.lower() or "framework" in key.lower():
                        tech_preferences[str(value)] += 1.0
        
        return dict(tech_preferences)
    
    def _get_architecture_patterns(self, context: Dict[str, Any]) -> Dict[str, float]:
        """Get preferred architecture patterns."""
        patterns = defaultdict(float)
        
        for feedback in self.feedback_history:
            arch_type = feedback.context.get("architecture_type")
            if arch_type:
                patterns[arch_type] += feedback.user_rating / 5.0
        
        return dict(patterns)
    
    def _calculate_feedback_stats(self) -> Dict[str, Any]:
        """Calculate feedback statistics."""
        if not self.feedback_history:
            return {}
        
        ratings = [f.user_rating for f in self.feedback_history]
        
        return {
            "total_count": len(self.feedback_history),
            "average_rating": sum(ratings) / len(ratings),
            "positive_count": len([f for f in self.feedback_history if f.feedback_type == "positive"]),
            "negative_count": len([f for f in self.feedback_history if f.feedback_type == "negative"]),
            "neutral_count": len([f for f in self.feedback_history if f.feedback_type == "neutral"])
        }
    
    def _generate_id(self) -> str:
        """Generate a unique ID."""
        import uuid
        return str(uuid.uuid4())
    
    def load_learning_data(self):
        """Load learning data from storage."""
        try:
            import os
            if os.path.exists(self.storage_path):
                with open(self.storage_path, 'r') as f:
                    data = json.load(f)
                
                # Load feedback history
                self.feedback_history = [
                    FeedbackEntry(**item) for item in data.get("feedback_history", [])
                ]
                
                # Load learning insights
                self.learning_insights = [
                    LearningInsight(**item) for item in data.get("learning_insights", [])
                ]
                
                # Load preference patterns
                self.preference_patterns = defaultdict(dict, data.get("preference_patterns", {}))
                
                logger.info("Learning data loaded successfully", 
                           feedback_count=len(self.feedback_history),
                           insights_count=len(self.learning_insights))
        
        except Exception as e:
            logger.warning("Failed to load learning data", error=str(e))
    
    def save_learning_data(self):
        """Save learning data to storage."""
        try:
            data = {
                "feedback_history": [asdict(f) for f in self.feedback_history],
                "learning_insights": [asdict(i) for i in self.learning_insights],
                "preference_patterns": dict(self.preference_patterns),
                "saved_at": datetime.now().isoformat()
            }
            
            # Convert datetime objects to strings for JSON serialization
            for feedback in data["feedback_history"]:
                if isinstance(feedback["timestamp"], datetime):
                    feedback["timestamp"] = feedback["timestamp"].isoformat()
            
            for insight in data["learning_insights"]:
                if isinstance(insight["created_at"], datetime):
                    insight["created_at"] = insight["created_at"].isoformat()
            
            with open(self.storage_path, 'w') as f:
                json.dump(data, f, indent=2, default=str)
            
            logger.debug("Learning data saved successfully")
            
        except Exception as e:
            logger.error("Failed to save learning data", error=str(e))


class AdaptiveRecommendationEngine:
    """
    Adaptive recommendation engine that uses feedback to improve recommendations.
    """
    
    def __init__(self, feedback_processor: FeedbackProcessor):
        self.feedback_processor = feedback_processor
    
    def adjust_recommendation_scores(self, recommendations: List[Dict[str, Any]], 
                                   context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Adjust recommendation scores based on learned patterns.
        """
        try:
            adjustments = self.feedback_processor.get_recommendations_adjustments(context)
            
            for recommendation in recommendations:
                # Apply preference weights
                original_score = recommendation.get("confidence_score", 0.5)
                
                # Cost adjustment
                if "cost" in recommendation.get("description", "").lower():
                    cost_weight = adjustments.get("preference_weights", {}).get("cost", 1.0)
                    recommendation["confidence_score"] = min(1.0, original_score * cost_weight)
                
                # Performance adjustment
                if "performance" in recommendation.get("description", "").lower():
                    perf_weight = adjustments.get("preference_weights", {}).get("performance", 1.0)
                    recommendation["confidence_score"] = min(1.0, original_score * perf_weight)
                
                # Cloud provider preference
                provider = recommendation.get("cloud_provider")
                if provider and provider in adjustments.get("cloud_provider_preferences", {}):
                    provider_score = adjustments["cloud_provider_preferences"][provider]
                    recommendation["confidence_score"] = min(1.0, original_score * (1.0 + provider_score * 0.2))
            
            # Sort by adjusted confidence score
            recommendations.sort(key=lambda x: x.get("confidence_score", 0), reverse=True)
            
            logger.info("Recommendation scores adjusted", 
                       recommendations_count=len(recommendations))
            
            return recommendations
            
        except Exception as e:
            logger.error("Failed to adjust recommendation scores", error=str(e))
            return recommendations


# Factory functions
def create_feedback_processor(storage_path: str = "learning_data.json") -> FeedbackProcessor:
    """Create a FeedbackProcessor instance."""
    return FeedbackProcessor(storage_path)


def create_adaptive_recommendation_engine(feedback_processor: FeedbackProcessor) -> AdaptiveRecommendationEngine:
    """Create an AdaptiveRecommendationEngine instance."""
    return AdaptiveRecommendationEngine(feedback_processor)