import os
import logging
import time
import asyncio
from xai_sdk import AsyncClient
from xai_sdk.chat import SearchParameters
from aiohttp import ClientError, ClientConnectorError

logger = logging.getLogger(__name__)

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
            async with AsyncClient(api_key=self.api_key) as client:
                # Create a chat session with search enabled
                chat = await asyncio.wait_for(
                    client.chat.create(
                        model="grok-4-fast",
                        search=SearchParameters(
                            search_mode="on",
                            sources=["x_source"]
                        )
                    ),
                    timeout=30
                )

                # Query for user's posts and interactions
                query = f"Recent posts and interactions by @{username} on X, including topics they engage with"
                await chat.append(user=query)

                # Get the response
                response = await asyncio.wait_for(chat.get_response(), timeout=30)
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

    async def analyze_context(self, context: str) -> list[str]:
        """
        Analyze the gathered context to extract main topics/interests.

        Uses Grok AI to parse user context and extract key topics of interest.

        Args:
            context (str): User context text from gather_user_context

        Returns:
            list[str]: List of extracted topics (max 10), or fallback topics on error

        Raises:
            No exceptions raised - returns fallback responses on errors

        Example:
            >>> topics = await service.analyze_context("User posts about AI and space...")
            >>> print(len(topics))
            5
        """
        try:
            async with AsyncClient(api_key=self.api_key) as client:
                chat = await asyncio.wait_for(client.chat.create(model="grok-4-fast"), timeout=30)

                prompt = f"""
                Based on the following information about a user's X activity, extract the top 5-10 main topics or interests they seem to have.
                Return only a comma-separated list of topics, no other text.

                Context: {context}
                """
                await chat.append(user=prompt)
                response = await asyncio.wait_for(chat.get_response(), timeout=30)
                topics_str = response.content.strip()
                # Split by comma and clean
                topics = [t.strip() for t in topics_str.split(",") if t.strip()]
                return topics[:10]  # Limit to 10
        except ClientConnectorError as e:
            logger.error(f"Network connection error analyzing context: {str(e)}")
            return ["AI", "Technology", "Space", "Innovation", "Future"]
        except ClientError as e:
            logger.error(f"HTTP client error analyzing context: {str(e)}")
            return ["AI", "Technology", "Space", "Innovation", "Future"]
        except ValueError as e:
            logger.error(f"Validation error analyzing context: {str(e)}")
            return ["AI", "Technology", "Space", "Innovation", "Future"]
        except asyncio.TimeoutError as e:
            logger.error(f"Timeout error analyzing context: {str(e)}")
            return ["AI", "Technology", "Space", "Innovation", "Future"]
        except Exception as e:
            logger.error(f"Unexpected error analyzing context: {str(e)}")
            return ["AI", "Technology", "Space", "Innovation", "Future"]

    async def generate_recommendations(self, topics: list[str], context: str) -> str:
        """
        Simulate Elon's X recommendation algorithm using grok-code-fast-1.

        Generates personalized content recommendations based on user topics and context,
        simulating the X recommendation algorithm.

        Args:
            topics (list[str]): List of user interest topics
            context (str): Original user context for additional personalization

        Returns:
            str: Personalized recommendation text, or fallback text on error

        Raises:
            No exceptions raised - returns fallback responses on errors

        Example:
            >>> recs = await service.generate_recommendations(["AI", "Space"], "User context...")
            >>> print("recommendations" in recs.lower())
            True
        """
        try:
            async with AsyncClient(api_key=self.api_key) as client:
                chat = await asyncio.wait_for(client.chat.create(model="grok-code-fast-1"), timeout=30)

                prompt = f"""
                You are simulating Elon's X recommendation algorithm. Based on a user's interests in: {', '.join(topics)}

                And their activity context: {context[:1000]}...  # Truncate for token limit

                Generate a personalized recommendation summary as if the algorithm is suggesting posts.
                Focus on:
                - High-quality, engaging content
                - Topics the user cares about
                - Diverse but relevant suggestions
                - Surface "banger" posts from smaller accounts

                Return a natural language summary of recommended content, 2-3 paragraphs.
                """
                await chat.append(user=prompt)
                response = await asyncio.wait_for(chat.get_response(), timeout=30)
                return response.content
        except ClientConnectorError as e:
            logger.error(f"Network connection error generating recommendations: {str(e)}")
            return f"Based on your interests in {', '.join(topics)}, we recommend exploring more content about these topics. This is a mock response for testing - in production, this would be generated by Grok's algorithm simulation."
        except ClientError as e:
            logger.error(f"HTTP client error generating recommendations: {str(e)}")
            return f"Based on your interests in {', '.join(topics)}, we recommend exploring more content about these topics. This is a mock response for testing - in production, this would be generated by Grok's algorithm simulation."
        except ValueError as e:
            logger.error(f"Validation error generating recommendations: {str(e)}")
            return f"Based on your interests in {', '.join(topics)}, we recommend exploring more content about these topics. This is a mock response for testing - in production, this would be generated by Grok's algorithm simulation."
        except asyncio.TimeoutError as e:
            logger.error(f"Timeout error generating recommendations: {str(e)}")
            return f"Based on your interests in {', '.join(topics)}, we recommend exploring more content about these topics. This is a mock response for testing - in production, this would be generated by Grok's algorithm simulation."
        except Exception as e:
            logger.error(f"Unexpected error generating recommendations: {str(e)}")
            return f"Based on your interests in {', '.join(topics)}, we recommend exploring more content about these topics. This is a mock response for testing - in production, this would be generated by Grok's algorithm simulation."