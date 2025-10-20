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

class DiversityMetrics(BaseModel):
    """Diversity and filter bubble risk metrics."""
    diversity_score: float = Field(description="Feed diversity score (0-100%, higher=more diverse)", ge=0, le=100)
    topic_entropy: float = Field(description="Topic entropy measure (0-1, higher=more varied)", ge=0, le=1)
    filter_bubble_risk: str = Field(description="Risk level: 'Low', 'Moderate', or 'High'")
    viewpoint_diversity: str = Field(description="Assessment of ideological/viewpoint spread in recommendations")

class OpposingViewpoints(BaseModel):
    """Opposing viewpoints included in recommendations."""
    included: bool = Field(description="Whether opposing viewpoints are being included")
    topics_with_diversity: List[str] = Field(description="Topics where opposing viewpoints will be shown")
    explanation: str = Field(description="How opposing viewpoints improve the feed")

class TemporalAnalysis(BaseModel):
    """Temporal characteristics of recommendations."""
    recency_bias: str = Field(description="Assessment: 'High (recent-focused)', 'Moderate (balanced)', or 'Low (evergreen-focused)'")
    temporal_mix_explanation: str = Field(description="How recommendations balance recent vs. evergreen content")
    content_freshness: str = Field(description="Percentage of recent content vs. timeless content")

class RecommendationExplanation(BaseModel):
    """Explanation for why a specific signal is being adjusted."""
    signal_name: str = Field(description="Name of the signal being explained")
    why_this_recommendation: str = Field(description="Why this adjustment benefits the user")
    expected_impact: str = Field(description="What users will notice from this adjustment")

class AlgorithmReport(BaseModel):
    """Complete algorithm adjustment report."""
    analysis_process: str = Field(description="Explanation of the analysis reasoning")
    signals_boosted: List[Signal] = Field(description="Signals being boosted")
    signals_reduced: List[Signal] = Field(description="Signals being reduced")
    feed_composition: FeedComposition = Field(description="Feed composition changes")
    quality_metrics: QualityMetrics = Field(description="Quality metrics applied")
    diversity_metrics: DiversityMetrics = Field(description="Diversity and filter bubble risk assessment")
    opposing_viewpoints: OpposingViewpoints = Field(description="Opposing viewpoints strategy")
    temporal_analysis: TemporalAnalysis = Field(description="Temporal characteristics of recommendations")
    recommendation_explanations: List[RecommendationExplanation] = Field(description="Why-this-recommendation explanations for key signals")
    expected_outcome: str = Field(description="Summary of expected feed changes")
    profile_report: str = Field(description="Detailed narrative profile report summarizing all findings")

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

class PoliticalSpectrum(BaseModel):
    """Political positioning on left-right spectrum."""
    position: str = Field(description="Position on spectrum: 'Far Left', 'Left', 'Center-Left', 'Center', 'Center-Right', 'Right', 'Far Right', or 'Apolitical'")
    confidence: float = Field(description="Confidence score (0-1) for this positioning", ge=0, le=1)
    reasoning: str = Field(description="Detailed explanation (3-5 sentences) for why this positioning was determined, citing specific posts or patterns")

class PoliticalValueAlignment(BaseModel):
    """Specific political value or issue alignment."""
    value_name: str = Field(description="Name of the political value or issue (e.g., 'Economic Regulation', 'Social Programs', 'Individual Liberty')")
    stance: str = Field(description="User's apparent stance: 'Strongly Support', 'Support', 'Neutral', 'Oppose', 'Strongly Oppose', or 'Mixed'")
    evidence: str = Field(description="Brief evidence from posts supporting this assessment")

class PoliticalAnalysisReport(BaseModel):
    """Complete political analysis report."""
    political_spectrum: PoliticalSpectrum = Field(description="User's position on political spectrum")
    key_political_topics: List[str] = Field(description="8-12 main political topics the user engages with")
    ideological_markers: List[str] = Field(description="6-10 specific ideological positions or markers identified")
    value_alignments: List[PoliticalValueAlignment] = Field(description="5-8 specific political values and the user's alignment on each")
    engagement_level: str = Field(description="Political engagement level: 'Very Active', 'Active', 'Moderate', 'Low', or 'Minimal'")
    engagement_style: str = Field(description="How they engage: 'Activist', 'Commentator', 'Observer', 'Debater', 'Educator', 'Satirist', etc.")
    primary_concerns: List[str] = Field(description="5-8 primary political concerns or issues ranked by frequency")
    policy_interests: List[str] = Field(description="6-10 specific policy areas of interest")
    notable_positions: List[str] = Field(description="3-5 notable or distinctive political positions they've expressed")
    communication_tone: str = Field(description="Overall tone: 'Analytical', 'Passionate', 'Moderate', 'Confrontational', 'Humorous', etc.")
    analysis_summary: str = Field(description="Comprehensive 4-6 paragraph summary with specific examples from posts, organized with clear paragraph breaks using \\n\\n")
    disclaimer: str = Field(description="Important disclaimer about AI analysis limitations")

class PoliticalAnalysisResponse(BaseModel):
    """Response model for political analysis with metadata."""
    report: PoliticalAnalysisReport = Field(description="The political analysis report")
    tokens: Dict[str, int] = Field(description="Token usage statistics")

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

    def _cleanup_cache(self):
        """
        Remove expired entries from cache and limit cache size.

        This method:
        1. Removes entries older than CACHE_TTL
        2. Limits cache to MAX_CACHE_SIZE entries (removes oldest if exceeded)
        """
        now = time.time()

        # Remove expired entries
        expired_keys = [
            key for key, (timestamp, _) in self.cache.items()
            if now - timestamp >= self.CACHE_TTL
        ]
        for key in expired_keys:
            del self.cache[key]
            logger.debug(f"Removed expired cache entry for: {key}")

        # Limit cache size to prevent memory issues
        MAX_CACHE_SIZE = 100
        if len(self.cache) > MAX_CACHE_SIZE:
            # Remove oldest entries
            sorted_items = sorted(self.cache.items(), key=lambda x: x[1][0])
            entries_to_remove = len(self.cache) - MAX_CACHE_SIZE
            for key, _ in sorted_items[:entries_to_remove]:
                del self.cache[key]
                logger.debug(f"Removed old cache entry (size limit): {key}")
            logger.info(f"Cache size limited to {MAX_CACHE_SIZE} entries (removed {entries_to_remove} oldest)")

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
        # Clean up expired cache entries
        self._cleanup_cache()

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

            ### Diversity & Filter Bubble Risk Analysis:
            - Calculate a diversity_score (0-100) representing how diverse the personalized feed would be
            - Assess topic_entropy (0-1) measuring variety in topic spread
            - Evaluate filter_bubble_risk as "Low", "Moderate", or "High" - is this algorithm creating an echo chamber?
            - Analyze viewpoint_diversity: Are opposing/diverse perspectives being included?

            ### Opposing Viewpoints Strategy:
            - Determine if opposing viewpoints should be included (included: true/false)
            - List specific topics where opposing viewpoints would be introduced
            - Explain how this improves user understanding and prevents filter bubbles

            ### Temporal Analysis (Recency vs. Evergreen):
            - Assess recency_bias: Is this "High (recent-focused)", "Moderate (balanced)", or "Low (evergreen-focused)"?
            - Explain the temporal_mix: How are recent trending topics balanced with timeless evergreen content?
            - Specify content_freshness as a percentage (e.g., "65% recent content, 35% timeless content")

            ### Why This Recommendation? (User-Facing Explanations):
            - For 3-4 key signals being boosted, provide signal_name, why_this_recommendation (why users benefit), and expected_impact (what they'll notice)
            - Make these explanations clear and non-technical for end users

            ### Expected Outcome:
            - Briefly summarize the net effect on user's feed in 2-3 sentences
            - Acknowledge this is a simulation based on limited sample data

            ### Detailed Profile Report (inferred from posts):
            - Base this section exclusively on USER ACTIVITY SAMPLE and detected topics/weights; do not describe algorithm behavior or adjustments.
            - Identify likely stances and affiliations stated or strongly implied (e.g., support/opposition to public figures, policies, teams, or communities).
            - Characterize ideological leaning if evidence exists (e.g., left/right; libertarian/authoritarian) and note uncertainty clearly.
            - Summarize recurring interests, communities, tone/style, values, and notable themes inferred from the posts.
            - Call out contradictions or ambiguity where present; avoid overclaiming.
            - Include 2–4 short quotes or paraphrased snippets as evidence with brief context.
            - Conclude with a one‑sentence caveat that findings are speculative based on a limited sample.
            - Tone: neutral, factual, evidence‑first; avoid judgmental language.


            Use technical language for your analysis. Be specific with metrics and percentages. Avoid conversational tone.
            This should read like an internal engineering report, not a letter to the user.
            Show your analytical reasoning throughout.

            IMPORTANT: Structure your response to match these exact fields:
            - analysis_process: Your reasoning explanation (string)
            - signals_boosted: List of signals being boosted (each with name, adjustment, reason)
            - signals_reduced: List of signals being reduced (each with name, adjustment, reason)
            - feed_composition: Object with increase (list), decrease (list), account_distribution (string)
            - quality_metrics: Object with prioritized_signals (list), spam_filters (list), diversity_mechanisms (list)
            - diversity_metrics: Object with diversity_score (0-100), topic_entropy (0-1), filter_bubble_risk ("Low"/"Moderate"/"High"), viewpoint_diversity (string)
            - opposing_viewpoints: Object with included (boolean), topics_with_diversity (list of strings), explanation (string)
            - temporal_analysis: Object with recency_bias ("High (recent-focused)"/"Moderate (balanced)"/"Low (evergreen-focused)"), temporal_mix_explanation (string), content_freshness (string)
            - recommendation_explanations: List of objects, each with signal_name, why_this_recommendation, expected_impact
            - expected_outcome: Summary of net effect (string)
            - profile_report: Detailed profile about the user inferred from their posts (string)
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

    async def generate_political_analysis(self, context: str) -> Dict[str, Any]:
        """
        Analyze a user's political leanings and engagement based on their X activity.

        Performs a specialized analysis focused on identifying political topics, ideological markers,
        and positioning on the political spectrum based on the user's posts and interactions.

        Args:
            context (str): User's X activity context from gather_user_context

        Returns:
            Dict[str, Any]: Dictionary containing political analysis report and token usage

        Raises:
            No exceptions raised - returns fallback responses on errors
        """
        try:
            # Configure client with extended timeout for reasoning model
            client = AsyncClient(api_key=self.api_key, timeout=3600)
            chat = client.chat.create(model="grok-4-fast-reasoning")

            prompt = f"""
            CONTEXT: You are analyzing a LIMITED SAMPLE of a user's X activity to understand their political interests,
            engagement, and positioning on the political spectrum. This is for an educational tool showing users their
            political profile based on observable patterns in their posts.

            IMPORTANT DISCLAIMERS:
            - This analysis is based on a limited sample of posts
            - Political positioning is speculative and should not be treated as definitive
            - The analysis identifies patterns and interests, not personal beliefs
            - AI analysis has inherent limitations and biases

            Based on the user's X activity, provide a comprehensive and DETAILED political analysis including:

            1. POLITICAL SPECTRUM POSITIONING: Determine where on the left-right spectrum the user appears to fall
               based on observable patterns. Options: Far Left, Left, Center-Left, Center, Center-Right, Right, Far Right, or Apolitical
               Include a confidence score (0-1) and detailed reasoning (3-5 sentences with specific examples from posts).

            2. KEY POLITICAL TOPICS: List 8-12 main political topics or issues the user engages with
               (e.g., "Climate Policy", "Healthcare Reform", "Immigration", "Economic Policy", "Foreign Policy", etc.)

            3. IDEOLOGICAL MARKERS: Identify 6-10 specific ideological positions or markers
               (e.g., "Pro-regulation", "Free market advocate", "Social justice focus", "Nationalist", "Globalist", etc.)

            4. VALUE ALIGNMENTS: For 5-8 key political values/issues, identify their stance and provide brief evidence
               (e.g., Economic Regulation: "Support" - evidence from posts)

            5. ENGAGEMENT LEVEL: Rate their political engagement: Very Active, Active, Moderate, Low, or Minimal

            6. ENGAGEMENT STYLE: Describe HOW they engage (e.g., "Activist", "Commentator", "Observer", "Debater", "Educator", "Satirist")

            7. PRIMARY CONCERNS: List 5-8 primary political concerns or issues ranked by frequency of discussion

            8. POLICY INTERESTS: List 6-10 specific policy areas they show interest in

            9. NOTABLE POSITIONS: Identify 3-5 notable or distinctive political positions they've expressed

            10. COMMUNICATION TONE: Describe their overall tone (e.g., "Analytical", "Passionate", "Moderate", "Confrontational", "Humorous")

            11. ANALYSIS SUMMARY: Provide a DETAILED 4-6 paragraph comprehensive summary of their political profile.
                IMPORTANT FORMATTING: Separate each paragraph with a blank line (use \\n\\n between paragraphs).
                Include specific examples from their posts, quote paraphrased content, and provide nuanced analysis.
                Structure:
                - Paragraph 1: Overall political positioning and confidence level
                - Paragraph 2: Key topics and engagement patterns with specific examples
                - Paragraph 3: Ideological markers and value alignments with evidence
                - Paragraph 4: Communication style and notable positions
                - Paragraph 5-6: Nuanced observations and caveats

            User Activity Sample: {context}

            Return a structured analysis with all the above components. Be thorough and specific.
            """
            chat.append(user(prompt))

            # Use structured output to guarantee format
            response, parsed = await chat.parse(PoliticalAnalysisReport)

            # Add disclaimer
            if not parsed.disclaimer:
                parsed.disclaimer = (
                    "This analysis is AI-generated based on a limited sample of posts. "
                    "It identifies observable patterns and interests, not definitive political beliefs. "
                    "Political positioning is speculative and should be interpreted with caution."
                )

            # Extract token usage
            tokens = {
                "completion_tokens": response.usage.completion_tokens if hasattr(response.usage, 'completion_tokens') else 0,
                "reasoning_tokens": response.usage.reasoning_tokens if hasattr(response.usage, 'reasoning_tokens') else 0,
                "total_tokens": response.usage.total_tokens if hasattr(response.usage, 'total_tokens') else 0
            }

            logger.info(f"Successfully generated political analysis (tokens: {tokens['total_tokens']})")
            return {
                "report": parsed.dict(),
                "tokens": tokens
            }

        except ClientConnectorError as e:
            logger.error(f"Network connection error in political analysis: {str(e)}")
            return self._fallback_political_response()
        except ClientError as e:
            logger.error(f"HTTP client error in political analysis: {str(e)}")
            return self._fallback_political_response()
        except ValueError as e:
            logger.error(f"Validation error in political analysis: {str(e)}")
            return self._fallback_political_response()
        except asyncio.TimeoutError as e:
            logger.error(f"Timeout error in political analysis: {str(e)}")
            return self._fallback_political_response()
        except Exception as e:
            logger.error(f"Unexpected error in political analysis: {str(e)}")
            return self._fallback_political_response()

    def _fallback_political_response(self) -> Dict[str, Any]:
        """Generate a fallback response for political analysis when API calls fail."""
        return {
            "report": {
                "political_spectrum": {
                    "position": "Center",
                    "confidence": 0.3,
                    "reasoning": "Insufficient data for reliable analysis. This is a fallback response due to API limitations. Unable to determine political positioning with confidence."
                },
                "key_political_topics": ["General Politics", "Policy Discussion", "Social Issues", "Current Events"],
                "ideological_markers": ["Moderate", "Pragmatic", "Centrist"],
                "value_alignments": [
                    {
                        "value_name": "Political Engagement",
                        "stance": "Neutral",
                        "evidence": "Insufficient data for assessment"
                    }
                ],
                "engagement_level": "Moderate",
                "engagement_style": "Observer",
                "primary_concerns": ["Economic Policy", "Social Issues", "Governance", "Public Policy"],
                "policy_interests": ["General Policy", "Reform", "Governance"],
                "notable_positions": ["Unable to identify specific positions due to limited data"],
                "communication_tone": "Neutral",
                "analysis_summary": "Unable to perform complete analysis due to API limitations.\n\nThe user appears to engage with political content at a moderate level based on the available sample. However, this is a fallback response and should not be considered reliable.\n\nPolitical analysis requires more comprehensive data and successful API connectivity for accurate assessment. Please try again later.",
                "disclaimer": "This is a fallback response due to API limitations. The analysis is incomplete and should not be relied upon. Political analysis requires more comprehensive data for accuracy."
            },
            "tokens": {"completion_tokens": 0, "reasoning_tokens": 0, "total_tokens": 0}
        }

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
                "expected_outcome": "Mock outcome: Feed will be adjusted based on user interests.",
                "profile_report": "Mock profile report: Based on the sample posts, the user expresses support/opposition to certain figures or policies, shows a likely leaning on common axes, and exhibits recurring interests and communities; this is speculative and based on a limited sample."
            },
            "tokens": {"completion_tokens": 0, "reasoning_tokens": 0, "total_tokens": 0}
        }