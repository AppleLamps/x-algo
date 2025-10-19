from fastapi import FastAPI, HTTPException, Header, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any
import os
import logging
import time
from dotenv import load_dotenv
from xai_sdk import AsyncClient
from xai_sdk.chat import SearchParameters
import asyncio
from aiohttp import ClientError, ClientConnectorError
from services.xai_service import XAIService

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
XAI_API_KEY = os.getenv("XAI_API_KEY")
API_KEY = os.getenv("API_KEY")
if not XAI_API_KEY:
    raise ValueError("XAI_API_KEY not found in environment variables")
if not API_KEY:
    raise ValueError("API_KEY not found in environment variables")

# Add validation for API key format and presence
if not XAI_API_KEY or len(XAI_API_KEY.strip()) == 0:
    raise ValueError("XAI_API_KEY environment variable is required and cannot be empty")
if not XAI_API_KEY.startswith("xai-"):
    logger.warning("XAI_API_KEY does not appear to be a valid xAI key format")

# Validate API_KEY
if not API_KEY or len(API_KEY.strip()) == 0:
    raise ValueError("API_KEY environment variable is required and cannot be empty")

# Initialize XAI service
xai_service = XAIService(XAI_API_KEY)

# Simple rate limiting (client_ip -> list of timestamps)
rate_limit = {}
RATE_LIMIT_REQUESTS = 10  # requests per minute
RATE_LIMIT_WINDOW = 60  # seconds

def verify_api_key(x_api_key: str = Header(None, alias="X-API-Key")):
    if not x_api_key or x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")

def check_rate_limit(request: Request):
    client_ip = request.client.host
    now = time.time()
    
    if client_ip not in rate_limit:
        rate_limit[client_ip] = []
    
    # Clean old entries
    rate_limit[client_ip] = [t for t in rate_limit[client_ip] if now - t < RATE_LIMIT_WINDOW]
    
    if len(rate_limit[client_ip]) >= RATE_LIMIT_REQUESTS:
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    
    rate_limit[client_ip].append(now)

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
    allow_origins=["http://localhost:3000"],  # Frontend URL
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
    username = request.username.strip()
    if not username:
        raise HTTPException(status_code=400, detail="Username cannot be empty")

    try:
        # Gather context from X (with date filtering and media understanding)
        context = await xai_service.gather_user_context(username)

        # Analyze context to extract topics with weights (structured output)
        topics_with_weights = await xai_service.analyze_context(context)

        # Generate recommendations using grok-4-fast-reasoning (structured output with tokens)
        recommendations_response = await xai_service.generate_recommendations(topics_with_weights, context)

        # Convert topics to response format
        topics_response = [TopicWithWeight(topic=t["topic"], weight=t["weight"]) for t in topics_with_weights]

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
    username = request.username.strip()
    if not username:
        raise HTTPException(status_code=400, detail="Username cannot be empty")
    
    try:
        # Gather context (will use cache if available from /analyze call)
        context = await xai_service.gather_user_context(username)
        
        # Generate quick insights with grok-3
        insights = await xai_service.generate_quick_insights(username, context)
        
        return InsightsResponse(insights=insights)
    except Exception as e:
        logger.error(f"Error generating insights for {username}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Insight generation failed: {str(e)}")

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