import os
import logging
import time
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any
from pydantic import BaseModel, Field
from xai_sdk import AsyncClient  # type: ignore
from xai_sdk.chat import user  # type: ignore
from xai_sdk.tools import x_search, code_execution  # type: ignore
from aiohttp import ClientError, ClientConnectorError

logger = logging.getLogger(__name__)

# Pydantic Models for Structured Outputs
class TopicWithWeight(BaseModel):
    """Represents a topic with its calculated weight."""
    topic: str = Field(description="The topic or interest area")
    weight: float = Field(description="Weight/importance score (0-1)", ge=0, le=1)

class TopicsResponse(BaseModel):
    """Response model for topic analysis."""
    topics: List[TopicWithWeight] = Field(description="List of identified topics with weights")

class Signal(BaseModel):
    """Algorithmic signal adjustment."""
    name: str = Field(description="Name of the signal")
    adjustment: str = Field(description="Adjustment percentage (e.g., '+40%' or '-30%')")
    reason: str = Field(description="Brief explanation for the adjustment")

class FeedComposition(BaseModel):
    """Feed composition changes."""
    increase: List[str] = Field(description="Content types that will increase")
    decrease: List[str] = Field(description="Content types that will decrease")
    account_distribution: str = Field(description="Account size distribution changes")

class QualityMetrics(BaseModel):
    """Quality metrics being applied."""
    prioritized_signals: List[str] = Field(description="Signals being prioritized")
    spam_filters: List[str] = Field(description="Spam/low-quality filters applied")
    diversity_mechanisms: List[str] = Field(description="Diversity mechanisms")

class AlgorithmReport(BaseModel):
    """Complete algorithm adjustment report."""
    analysis_process: str = Field(description="Explanation of the analysis reasoning")
    signals_boosted: List[Signal] = Field(description="Signals being boosted")
    signals_reduced: List[Signal] = Field(description="Signals being reduced")
    feed_composition: FeedComposition = Field(description="Feed composition changes")
    quality_metrics: QualityMetrics = Field(description="Quality metrics applied")
    expected_outcome: str = Field(description="Summary of expected feed changes")

class RecommendationResponse(BaseModel):
    """Response model for recommendations with metadata."""
    report: AlgorithmReport = Field(description="The algorithm adjustment report")
    tokens: Dict[str, int] = Field(description="Token usage statistics")

class QuickInsight(BaseModel):
    """A quick observation about user activity."""
    insight: str = Field(description="Short observation (1-2 sentences)")

class QuickInsightsResponse(BaseModel):
    """Response model for quick insights."""
    insights: List[str] = Field(description="List of quick observations about the user")

class XAIService:
    """
    Service class for handling X (Twitter) algorithm simulation operations.

    This service provides methods to gather user context, analyze content,
    and generate personalized recommendations using xAI's Grok models.
    Includes caching and error handling for robust operation.

    Attributes:
        api_key (str): xAI API key for authentication
        cache (dict): In-memory cache for user context results
        CACHE_TTL (int): Cache time-to-live in seconds (default: 300)
    """

    def __init__(self, api_key: str):
        """
        Initialize the XAI service.

        Args:
            api_key (str): Valid xAI API key starting with 'xai-'
        """
        self.api_key = api_key
        self.cache = {}
        self.CACHE_TTL = 300  # 5 minutes

    async def generate_quick_insights(self, username: str, context: str) -> List[str]:
        """
        Generate quick insights about a user's account using grok-3.
        
        These are fast, generic observations that can be displayed while
        the main analysis is running. Designed to rotate every 4 seconds.
        
        Args:
            username (str): X username being analyzed
            context (str): User context from gather_user_context
            
        Returns:
            List[str]: 8-12 quick insights about the user's activity
        """
        try:
            client = AsyncClient(api_key=self.api_key, timeout=30)
            chat = client.chat.create(model="grok-3")
            
            prompt = f"""
            Based on this X user's activity, generate 10 quick, interesting insights that reveal patterns 
            in their behavior. These will be shown to the user while their full analysis loads.
            
            Keep each insight:
            - Short (1-2 sentences max)
            - Specific and actionable
            - Varied (cover different aspects: topics, engagement style, network, timing, content preferences)
            - Neutral/positive tone
            - Data-driven when possible
            
            Examples of good insights:
            - "You engage most with accounts under 10K followers, suggesting you prefer authentic voices over influencers."
            - "Your posting activity peaks on weekday mornings, indicating a professional content strategy."
            - "You reply more than you retweet, showing a preference for genuine conversation over amplification."
            - "Your interests span both technical depth and creative expression—a rare combination."
            
            Avoid generic statements like "You post about technology." Be specific and insightful.
            
            Username: @{username}
            Activity Data: {context[:1500]}
            
            Generate exactly 10 distinct insights.
            """
            chat.append(user(prompt))
            
            # Use structured output
            response, parsed = await chat.parse(QuickInsightsResponse)
            
            return parsed.insights[:12]  # Cap at 12 insights
            
        except Exception as e:
            logger.error(f"Error generating quick insights: {str(e)}")
            # Fallback insights
            return [
                f"Analyzing @{username}'s recent activity patterns...",
                "Detecting primary interest signals...",
                "Mapping engagement behavior across content types...",
                "Identifying network interaction patterns...",
                "Calculating topic weights based on engagement depth...",
                "Analyzing content creation vs consumption balance...",
                "Evaluating temporal activity patterns...",
                "Building personalized recommendation profile..."
            ]

    async def gather_user_context(self, username: str) -> str:
        """
        Gather context about a user from X using xAI search.

        Retrieves recent posts and interactions for the given username,
        using xAI's search capabilities to analyze user activity.

        Args:
            username (str): X username to analyze (without @ symbol)

        Returns:
            str: Summary of user's posts and interactions, or fallback text on error

        Raises:
            No exceptions raised - returns fallback responses on errors

        Example:
            >>> context = await service.gather_user_context("elonmusk")
            >>> print(len(context) > 0)
            True
        """
        # Check cache first
        if username in self.cache:
            timestamp, cached_result = self.cache[username]
            if time.time() - timestamp < self.CACHE_TTL:
                logger.info(f"Using cached context for {username}")
                return cached_result

        try:
            # Configure client with extended timeout
            client = AsyncClient(api_key=self.api_key, timeout=120)
            
            # Calculate date range for recent activity (past 30 days)
            to_date = datetime.now()
            from_date = to_date - timedelta(days=30)
            
            chat = client.chat.create(
                model="grok-4-fast",
                tools=[
                    x_search(
                        from_date=from_date,
                        to_date=to_date,
                        enable_image_understanding=True,
                        enable_video_understanding=True
                    )
                ],
            )

            # Query for user's posts and interactions
            query = f"Posts, replies, images, and videos by or to @{username} on X from the past 30 days, including topics they engage with, replies they make, media they share, and visual content they post"
            chat.append(user(query))

            # Get the response
            response = await chat.sample()
            result = response.content
            # Cache the result
            self.cache[username] = (time.time(), result)
            return result
        except ClientConnectorError as e:
            logger.error(f"Network connection error gathering context for {username}: {str(e)}")
            return f"Mock context for {username}: This is a placeholder response for testing purposes. In a real scenario, this would contain actual X search results."
        except ClientError as e:
            logger.error(f"HTTP client error gathering context for {username}: {str(e)}")
            return f"Mock context for {username}: This is a placeholder response for testing purposes. In a real scenario, this would contain actual X search results."
        except ValueError as e:
            logger.error(f"Validation error gathering context for {username}: {str(e)}")
            return f"Mock context for {username}: This is a placeholder response for testing purposes. In a real scenario, this would contain actual X search results."
        except asyncio.TimeoutError as e:
            logger.error(f"Timeout error gathering context for {username}: {str(e)}")
            return f"Mock context for {username}: This is a placeholder response for testing purposes. In a real scenario, this would contain actual X search results."
        except Exception as e:
            logger.error(f"Unexpected error gathering context for {username}: {str(e)}")
            return f"Mock context for {username}: This is a placeholder response for testing purposes. In a real scenario, this would contain actual X search results."

    async def analyze_context(self, context: str) -> List[Dict[str, Any]]:
        """
        Analyze the gathered context to extract main topics/interests.

        Uses Grok AI to parse user context and extract key topics of interest.

        Args:
            context (str): User context text from gather_user_context

        Returns:
            List[Dict[str, Any]]: List of topics with weights (max 10), or fallback topics on error

        Raises:
            No exceptions raised - returns fallback responses on errors

        Example:
            >>> topics = await service.analyze_context("User posts about AI and space...")
            >>> print(len(topics))
            5
        """
        try:
            # Configure client with timeout
            client = AsyncClient(api_key=self.api_key, timeout=120)
            chat = client.chat.create(
                model="grok-4-fast"
            )

            prompt = f"""
            CONTEXT: You're analyzing a LIMITED SAMPLE (approximately 1-20 posts) of a user's X activity to demonstrate 
            how X's recommendation algorithm would personalize their feed. This is for an educational simulator showing 
            users what signals the algorithm picks up from their activity.
            
            Based on this limited sample of the user's X activity, extract the main topics or interests.

            Analyze the context and calculate weights for each topic based on:
            - Frequency: how often the topic appears in this sample
            - Recency: how recent the mentions are (assume recent if mentioned in recent context)
            - Engagement: indicators like likes, retweets, replies (infer from context)

            Return the top 5-10 topics with their weights (0-1 scale), ensuring diversity (no repetitive similar topics).
            
            CRITICAL: The weights MUST be normalized so that they sum to exactly 1.0 (100% when displayed as percentages).
            For example, if you identify 5 topics, their weights might be [0.35, 0.25, 0.20, 0.12, 0.08] which sum to 1.0.

            User Activity Sample: {context}
            """
            chat.append(user(prompt))
            
            # Use structured output to guarantee format
            response, parsed = await chat.parse(TopicsResponse)
            
            # Convert to dict format and normalize weights to sum to 1.0
            topics_with_weights = [{"topic": t.topic, "weight": t.weight} for t in parsed.topics[:10]]
            
            # Normalize weights to ensure they sum to exactly 1.0
            total_weight = sum(t["weight"] for t in topics_with_weights)
            if total_weight > 0:
                topics_with_weights = [
                    {"topic": t["topic"], "weight": round(t["weight"] / total_weight, 3)}
                    for t in topics_with_weights
                ]
            
            return topics_with_weights
        except ClientConnectorError as e:
            logger.error(f"Network connection error analyzing context: {str(e)}")
            return self._extract_fallback_topics(context)
        except ClientError as e:
            logger.error(f"HTTP client error analyzing context: {str(e)}")
            return self._extract_fallback_topics(context)
        except ValueError as e:
            logger.error(f"Validation error analyzing context: {str(e)}")
            return self._extract_fallback_topics(context)
        except asyncio.TimeoutError as e:
            logger.error(f"Timeout error analyzing context: {str(e)}")
            return self._extract_fallback_topics(context)
        except Exception as e:
            logger.error(f"Unexpected error analyzing context: {str(e)}")
            return self._extract_fallback_topics(context)

    async def generate_recommendations(self, topics: List[Dict[str, Any]], context: str) -> Dict[str, Any]:
        """
        Simulate Elon's X recommendation algorithm using grok-4-fast-reasoning.

        Generates personalized content recommendations based on user topics and context,
        simulating the X recommendation algorithm with structured output.

        Args:
            topics (List[Dict[str, Any]]): List of topics with weights
            context (str): Original user context for additional personalization

        Returns:
            Dict[str, Any]: Dictionary containing algorithm report and token usage

        Raises:
            No exceptions raised - returns fallback responses on errors

        Example:
            >>> recs = await service.generate_recommendations(["AI", "Space"], "User context...")
            >>> print("recommendations" in recs.lower())
            True
        """
        try:
            # Configure client with extended timeout for reasoning model
            client = AsyncClient(api_key=self.api_key, timeout=3600)
            chat = client.chat.create(model="grok-4-fast-reasoning")

            # Extract topic names and weights
            topic_names = [t.get('topic', str(t)) for t in topics]
            topics_with_weights_str = ', '.join([f"{t['topic']} (weight: {t['weight']:.2f})" for t in topics if isinstance(t, dict)])
            
            prompt = f"""
            CONTEXT: You are generating an educational simulator report that demonstrates how X's recommendation algorithm 
            would adjust based on a LIMITED SAMPLE (1-20 posts) of user activity. This is to help users understand what 
            signals the algorithm detects and how it personalizes their feed. Be realistic about the limited data available.
            
            USER INTEREST SIGNALS DETECTED: {topics_with_weights_str}
            USER ACTIVITY SAMPLE: {context[:1000]}
            
            Generate a technical, analytical report on how the recommendation algorithm would adjust for this user.
            Your output should be professional and data-driven, structured as follows:
            
            ## Analysis Process
            - Briefly explain your reasoning: How you analyzed the user's interests and activity patterns FROM THIS LIMITED SAMPLE
            - What key signals you identified and why they matter
            - Acknowledge that this is based on a small sample and represents potential adjustments
            - Your decision-making process for the adjustments below
            
            ## Algorithm Adjustments
            
            ### Content Signals Being Modified:
            - List specific algorithmic flags/signals being BOOSTED (e.g., "SpaceX content signal +40%", "Small account amplification +25%")
            - List specific algorithmic flags/signals being REDUCED (e.g., "Generic political commentary -30%", "Low-engagement posts -20%")
            
            ### Feed Composition Changes:
            CRITICAL: Use RELATIVE percentage changes (increases/decreases from baseline), NOT absolute feed allocations.
            - Specify what content types will INCREASE (e.g., "SpaceX-related posts +35% increase from baseline")
            - Specify what content types will DECREASE (e.g., "Generic news -25% decrease from baseline")
            - Mention account size distribution adjustments (e.g., "Surfacing 15% more posts from accounts <10K followers")
            - These are RELATIVE adjustments to the existing feed mix, not absolute percentages that need to sum to 100%
            
            ### Quality Metrics Applied:
            - Explain the intrinsic value signals being prioritized (engagement rate, reply depth, share velocity, etc.)
            - Note any spam/low-quality filters being applied
            - Mention diversity mechanisms to avoid echo chambers
            
            ### Expected Outcome:
            - Briefly summarize the net effect on user's feed in 2-3 sentences
            - Acknowledge this is a simulation based on limited sample data
            
            Use technical language. Be specific with metrics and percentages. Avoid conversational tone.
            This should read like an internal engineering report, not a letter to the user.
            Show your analytical reasoning throughout.
            
            IMPORTANT: Structure your response to match these exact fields:
            - analysis_process: Your reasoning explanation (string)
            - signals_boosted: List of signals being boosted (each with name, adjustment, reason)
            - signals_reduced: List of signals being reduced (each with name, adjustment, reason)
            - feed_composition: Object with increase (list), decrease (list), account_distribution (string)
            - quality_metrics: Object with prioritized_signals (list), spam_filters (list), diversity_mechanisms (list)
            - expected_outcome: Summary of net effect (string)
            """
            chat.append(user(prompt))
            
            # Use structured output to guarantee format
            response, parsed_report = await chat.parse(AlgorithmReport)
            
            # Extract token usage statistics
            tokens = {
                "completion_tokens": response.usage.completion_tokens if hasattr(response.usage, 'completion_tokens') else 0,
                "reasoning_tokens": response.usage.reasoning_tokens if hasattr(response.usage, 'reasoning_tokens') else 0,
                "total_tokens": response.usage.total_tokens if hasattr(response.usage, 'total_tokens') else 0
            }
            
            # Return structured response with report and metadata
            return {
                "report": parsed_report.model_dump(),
                "tokens": tokens
            }
        except ClientConnectorError as e:
            logger.error(f"Network connection error generating recommendations: {str(e)}")
            topic_names = [t.get('topic', str(t)) for t in topics]
            return self._fallback_response(topic_names)
        except ClientError as e:
            logger.error(f"HTTP client error generating recommendations: {str(e)}")
            topic_names = [t.get('topic', str(t)) for t in topics]
            return self._fallback_response(topic_names)
        except ValueError as e:
            logger.error(f"Validation error generating recommendations: {str(e)}")
            topic_names = [t.get('topic', str(t)) for t in topics]
            return self._fallback_response(topic_names)
        except asyncio.TimeoutError as e:
            logger.error(f"Timeout error generating recommendations: {str(e)}")
            topic_names = [t.get('topic', str(t)) for t in topics]
            return self._fallback_response(topic_names)
        except Exception as e:
            logger.error(f"Unexpected error generating recommendations: {str(e)}")
            topic_names = [t.get('topic', str(t)) for t in topics]
            return self._fallback_response(topic_names)
    
    def _extract_fallback_topics(self, context: str) -> List[Dict[str, Any]]:
        """
        Extract basic topics from context string when API fails.
        Uses simple keyword analysis as a last resort.
        """
        import re
        from collections import Counter
        
        # Remove common words and extract meaningful terms
        text = context.lower()
        # Simple word extraction (words with 4+ chars, excluding common terms)
        words = re.findall(r'\b[a-z]{4,}\b', text)
        common_words = {'that', 'this', 'with', 'from', 'have', 'been', 'will', 'about', 'their', 'would', 'there', 'could', 'when', 'what', 'which', 'these', 'those', 'some', 'more', 'than', 'other', 'such', 'into', 'only', 'also', 'then', 'them', 'your', 'just', 'like', 'much', 'make', 'made', 'many', 'over', 'posts', 'user', 'mock', 'context', 'placeholder', 'testing', 'purposes', 'real', 'scenario', 'contain', 'actual', 'results', 'search'}
        meaningful_words = [w for w in words if w not in common_words]
        
        # Count word frequency and get top terms
        word_counts = Counter(meaningful_words)
        top_words = word_counts.most_common(10)
        
        if not top_words:
            # Ultimate fallback if no words found
            return [{"topic": "General Interest", "weight": 1.0}]
        
        # Calculate raw weights based on frequency
        topics = []
        for word, count in top_words[:8]:
            topics.append({
                "topic": word.capitalize(),
                "weight": float(count)
            })
        
        # Normalize weights to sum to exactly 1.0
        total_weight = sum(t["weight"] for t in topics)
        if total_weight > 0:
            topics = [
                {"topic": t["topic"], "weight": round(t["weight"] / total_weight, 3)}
                for t in topics
            ]
        
        return topics
    
    def _fallback_response(self, topic_names: List[str]) -> Dict[str, Any]:
        """Generate a fallback response when API calls fail."""
        return {
            "report": {
                "analysis_process": f"Mock analysis for topics: {', '.join(topic_names)}. This is a fallback response for testing.",
                "signals_boosted": [
                    {"name": "Content relevance", "adjustment": "+30%", "reason": "Matches user interests"}
                ],
                "signals_reduced": [
                    {"name": "Generic content", "adjustment": "-20%", "reason": "Low relevance"}
                ],
                "feed_composition": {
                    "increase": ["Topic-specific content"],
                    "decrease": ["Off-topic posts"],
                    "account_distribution": "Standard distribution"
                },
                "quality_metrics": {
                    "prioritized_signals": ["Engagement rate"],
                    "spam_filters": ["Low-quality filter"],
                    "diversity_mechanisms": ["Topic diversity"]
                },
                "expected_outcome": "Mock outcome: Feed will be adjusted based on user interests."
            },
            "tokens": {"completion_tokens": 0, "reasoning_tokens": 0, "total_tokens": 0}
        }