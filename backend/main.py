from fastapi import FastAPI, HTTPException, Header, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any
import os
import logging
import time
import re
from dotenv import load_dotenv
from services.xai_service import (
    XAIService,
    DiversityMetrics,
    OpposingViewpoints,
    TemporalAnalysis,
    RecommendationExplanation,
    PoliticalAnalysisReport,
    PoliticalAnalysisResponse
)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
XAI_API_KEY = os.getenv("XAI_API_KEY", "").strip()
API_KEY = os.getenv("API_KEY", "").strip()

# Validate XAI_API_KEY
if not XAI_API_KEY:
    raise ValueError("XAI_API_KEY environment variable is required and cannot be empty")
if not XAI_API_KEY.startswith("xai-"):
    logger.warning("XAI_API_KEY does not appear to be a valid xAI key format (should start with 'xai-')")

# Validate API_KEY
if not API_KEY:
    raise ValueError("API_KEY environment variable is required and cannot be empty")
if len(API_KEY) < 16:
    logger.warning("API_KEY is shorter than 16 characters - consider using a longer key for security")

# Get allowed origins from environment variable, default to localhost for development
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")
# Strip whitespace from each origin
ALLOWED_ORIGINS = [origin.strip() for origin in ALLOWED_ORIGINS]
logger.info(f"CORS allowed origins: {ALLOWED_ORIGINS}")

# Initialize XAI service
xai_service = XAIService(XAI_API_KEY)

# Simple rate limiting (API key -> list of timestamps)
rate_limit = {}
RATE_LIMIT_REQUESTS = 10  # requests per minute
RATE_LIMIT_WINDOW = 60  # seconds

def verify_api_key(x_api_key: str = Header(None, alias="X-API-Key")):
    if not x_api_key:
        logger.warning("Authentication failed: No API key provided")
        raise HTTPException(status_code=401, detail="Invalid API key")
    if x_api_key != API_KEY:
        logger.warning(f"Authentication failed: Invalid API key attempted (key: {x_api_key[:8]}...)")
        raise HTTPException(status_code=401, detail="Invalid API key")

def check_rate_limit(request: Request, x_api_key: str = Header(None, alias="X-API-Key")):
    # Rate limit by API key instead of IP
    rate_key = x_api_key or request.client.host  # Fallback to IP if no key
    now = time.time()

    if rate_key not in rate_limit:
        rate_limit[rate_key] = []

    # Clean old entries
    rate_limit[rate_key] = [t for t in rate_limit[rate_key] if now - t < RATE_LIMIT_WINDOW]

    if len(rate_limit[rate_key]) >= RATE_LIMIT_REQUESTS:
        logger.warning(f"Rate limit exceeded for key: {rate_key[:8] if len(rate_key) > 8 else rate_key}... ({len(rate_limit[rate_key])} requests in {RATE_LIMIT_WINDOW}s)")
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded. Maximum {RATE_LIMIT_REQUESTS} requests per {RATE_LIMIT_WINDOW} seconds."
        )

    rate_limit[rate_key].append(now)

def validate_username(username: str) -> str:
    """
    Validate and sanitize X username.

    Args:
        username: Raw username input

    Returns:
        Sanitized username

    Raises:
        HTTPException: If username is invalid
    """
    # Strip whitespace
    username = username.strip()

    # Remove @ symbol if user included it
    username = username.lstrip('@')

    # Validate username is not empty
    if not username:
        logger.warning("Invalid username attempt: Empty username")
        raise HTTPException(status_code=400, detail="Username cannot be empty")

    # Validate username length (X usernames are 1-15 characters)
    if len(username) < 1 or len(username) > 15:
        logger.warning(f"Invalid username attempt: Length {len(username)} (must be 1-15 characters)")
        raise HTTPException(
            status_code=400,
            detail="Username must be between 1 and 15 characters"
        )

    # Validate username format (alphanumeric and underscores only)
    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        logger.warning(f"Invalid username attempt: Invalid characters in '{username}'")
        raise HTTPException(
            status_code=400,
            detail="Username can only contain letters, numbers, and underscores"
        )

    return username

# Check API availability (optional - for graceful degradation)
API_AVAILABLE = True
try:
    # Simple validation - try to create a client to check if key works
    # This is optional and can be removed if it causes issues
    pass
except Exception as e:
    logger.warning(f"API key validation failed: {str(e)}. API calls will use fallback responses.")
    API_AVAILABLE = False

app = FastAPI(title="X Algorithm Simulator API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AnalyzeRequest(BaseModel):
    username: str

class TopicWithWeight(BaseModel):
    topic: str
    weight: float

class AnalyzeResponse(BaseModel):
    topics: List[TopicWithWeight]
    recommendations: Dict[str, Any]  # Contains 'report' and 'tokens'

class InsightsRequest(BaseModel):
    username: str

class InsightsResponse(BaseModel):
    insights: List[str]

@app.post("/analyze", response_model=AnalyzeResponse, dependencies=[Depends(verify_api_key), Depends(check_rate_limit)])
async def analyze_user(request: AnalyzeRequest):
    """
    Analyze a user's X activity and return personalized topic recommendations.

    This endpoint processes a username, gathers context from X using AI search,
    analyzes the context to extract topics, and generates personalized content
    recommendations using Grok models.

    Args:
        request (AnalyzeRequest): Request object containing the username to analyze.
            The username should be a valid X (Twitter) handle without the @ symbol.

    Returns:
        AnalyzeResponse: Response containing:
            - topics: List of extracted interest topics with weights
            - recommendations: Personalized content recommendations with report and token usage

    Raises:
        HTTPException: 
            - 400: If username is empty or invalid
            - 401: If API key is missing or invalid
            - 429: If rate limit is exceeded
            - 500: If internal processing fails

    Example:
        >>> response = await analyze_user(AnalyzeRequest(username="elonmusk"))
        >>> print(response.topics)
        [{'topic': 'AI', 'weight': 0.8}, {'topic': 'Technology', 'weight': 0.6}, {'topic': 'Space', 'weight': 0.4}]
    """
    # Validate and sanitize username
    username = validate_username(request.username)

    logger.info(f"Starting analysis for user: {username}")

    try:
        # Gather context from X (with date filtering and media understanding)
        context = await xai_service.gather_user_context(username)

        # Analyze context to extract topics with weights (structured output)
        topics_with_weights = await xai_service.analyze_context(context)

        # Generate recommendations using grok-4-fast-reasoning (structured output with tokens)
        recommendations_response = await xai_service.generate_recommendations(topics_with_weights, context)

        # Convert topics to response format
        topics_response = [TopicWithWeight(topic=t["topic"], weight=t["weight"]) for t in topics_with_weights]

        logger.info(f"Successfully analyzed user: {username} (found {len(topics_response)} topics)")
        return AnalyzeResponse(topics=topics_response, recommendations=recommendations_response)
    except Exception as e:
        logger.error(f"Error analyzing user {username}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.post("/insights", response_model=InsightsResponse, dependencies=[Depends(verify_api_key), Depends(check_rate_limit)])
async def get_insights(request: InsightsRequest):
    """
    Generate quick insights about a user's account.

    This endpoint is designed to be called while the main /analyze endpoint is running.
    It returns 8-12 quick observations that can be displayed and rotated every 4 seconds.
    Uses grok-3 for fast generation.

    Args:
        request (InsightsRequest): Request object containing the username

    Returns:
        InsightsResponse: List of quick insights about the user

    Raises:
        HTTPException: 400 if username is invalid, 500 if generation fails
    """
    # Validate and sanitize username
    username = validate_username(request.username)

    logger.info(f"Generating insights for user: {username}")

    try:
        # Gather context (will use cache if available from /analyze call)
        context = await xai_service.gather_user_context(username)

        # Generate quick insights with grok-3
        insights = await xai_service.generate_quick_insights(username, context)

        logger.info(f"Successfully generated {len(insights)} insights for user: {username}")
        return InsightsResponse(insights=insights)
    except Exception as e:
        logger.error(f"Error generating insights for {username}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Insight generation failed: {str(e)}")

@app.post("/political-analysis", response_model=PoliticalAnalysisResponse, dependencies=[Depends(verify_api_key), Depends(check_rate_limit)])
async def analyze_political_profile(request: AnalyzeRequest):
    """
    Analyze a user's political leanings and engagement based on their X activity.

    This endpoint performs a specialized analysis focused on identifying political topics,
    ideological markers, and positioning on the political spectrum based on the user's posts.

    Args:
        request (AnalyzeRequest): Request object containing the username to analyze.
            The username should be a valid X (Twitter) handle without the @ symbol.

    Returns:
        PoliticalAnalysisResponse: Response containing:
            - report: Political analysis report with spectrum positioning, topics, and engagement
            - tokens: Token usage statistics

    Raises:
        HTTPException:
            - 400: If username is empty or invalid
            - 401: If API key is missing or invalid
            - 429: If rate limit is exceeded
            - 500: If internal processing fails

    Example:
        >>> response = await analyze_political_profile(AnalyzeRequest(username="elonmusk"))
        >>> print(response.report.political_spectrum.position)
        'Center-Right'
    """
    # Validate and sanitize username
    username = validate_username(request.username)

    logger.info(f"Starting political analysis for user: {username}")

    try:
        # Gather context from X (will use cache if available from /analyze call)
        context = await xai_service.gather_user_context(username)

        # Generate political analysis using grok-4-fast-reasoning
        political_analysis_response = await xai_service.generate_political_analysis(context)

        logger.info(f"Successfully completed political analysis for user: {username}")
        return PoliticalAnalysisResponse(
            report=political_analysis_response["report"],
            tokens=political_analysis_response["tokens"]
        )
    except Exception as e:
        logger.error(f"Error analyzing political profile for {username}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Political analysis failed: {str(e)}")

@app.get("/")
async def root():
    """
    Root endpoint providing basic API information.

    Returns:
        dict: Welcome message with API details.
    """
    return {"message": "X Algorithm Simulator API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)