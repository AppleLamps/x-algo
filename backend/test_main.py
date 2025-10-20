import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from services.xai_service import XAIService
from main import AnalyzeRequest, AnalyzeResponse, TopicWithWeight as APITopicWithWeight, InsightsRequest, InsightsResponse

# Create service instance for testing
service = XAIService("test_key")

@pytest.mark.asyncio
async def test_gather_user_context_success():
    """Test successful context gathering."""
    with patch('services.xai_service.AsyncClient') as mock_client:
        mock_chat = AsyncMock()
        mock_response = MagicMock()
        mock_response.content = "Sample X search results about AI and technology"
        mock_chat.sample = AsyncMock(return_value=mock_response)
        mock_client.return_value.chat.create.return_value = mock_chat

        result = await service.gather_user_context("testuser")
        assert isinstance(result, str)
        assert len(result) > 0

@pytest.mark.asyncio
async def test_gather_user_context_uses_cache():
    """Test that context gathering uses cache."""
    # Clear cache first
    service.cache.clear()

    # First call - should make API call
    with patch('services.xai_service.AsyncClient') as mock_client:
        mock_chat = AsyncMock()
        mock_response = MagicMock()
        mock_response.content = "Cached context"
        mock_chat.sample = AsyncMock(return_value=mock_response)
        mock_client.return_value.chat.create.return_value = mock_chat

        result1 = await service.gather_user_context("cachetest")

    # Second call - should use cache (no new API call)
    result2 = await service.gather_user_context("cachetest")
    assert result1 == result2

@pytest.mark.asyncio
async def test_analyze_context_returns_weighted_topics():
    """Test that analyze_context returns topics with weights."""
    result = await service.analyze_context("Sample context about AI and technology")

    assert isinstance(result, list)
    assert len(result) > 0
    assert all(isinstance(item, dict) for item in result)
    assert all('topic' in item and 'weight' in item for item in result)

    # Weights should be between 0 and 1
    for item in result:
        assert 0 <= item['weight'] <= 1

    # Weights should sum to approximately 1.0
    total_weight = sum(item['weight'] for item in result)
    assert 0.99 <= total_weight <= 1.01

@pytest.mark.asyncio
async def test_analyze_context_fallback():
    """Test that analyze_context has fallback on error."""
    with patch('services.xai_service.AsyncClient', side_effect=Exception("API Error")):
        result = await service.analyze_context("Sample context")

        # Should return fallback topics
        assert isinstance(result, list)
        assert len(result) > 0
        assert all('topic' in item and 'weight' in item for item in result)

@pytest.mark.asyncio
async def test_generate_recommendations_structure():
    """Test that recommendations have correct structure."""
    topics = [{"topic": "AI", "weight": 0.5}, {"topic": "Tech", "weight": 0.5}]
    result = await service.generate_recommendations(topics, "Sample context")

    # Check top-level structure
    assert 'report' in result
    assert 'tokens' in result

    # Check report structure
    report = result['report']
    assert 'analysis_process' in report
    assert 'signals_boosted' in report
    assert 'signals_reduced' in report
    assert 'feed_composition' in report
    assert 'quality_metrics' in report
    assert 'diversity_metrics' in report
    assert 'opposing_viewpoints' in report
    assert 'temporal_analysis' in report
    assert 'recommendation_explanations' in report
    assert 'expected_outcome' in report
    assert 'profile_report' in report

    # Check tokens structure
    assert 'completion_tokens' in result['tokens']
    assert 'total_tokens' in result['tokens']

@pytest.mark.asyncio
async def test_generate_quick_insights():
    """Test quick insights generation."""
    result = await service.generate_quick_insights("Sample context about user activity")

    assert isinstance(result, list)
    assert len(result) > 0
    assert all(isinstance(insight, str) for insight in result)

def test_analyze_request_model():
    """Test AnalyzeRequest Pydantic model."""
    request = AnalyzeRequest(username="testuser")
    assert request.username == "testuser"

def test_analyze_response_model():
    """Test AnalyzeResponse Pydantic model."""
    response = AnalyzeResponse(
        topics=[APITopicWithWeight(topic="AI", weight=0.5)],
        recommendations={
            "report": {
                "analysis_process": "Test analysis",
                "signals_boosted": [],
                "signals_reduced": [],
                "feed_composition": {
                    "increase": ["AI content"],
                    "decrease": ["Sports"],
                    "account_distribution": "More tech accounts"
                },
                "quality_metrics": {
                    "prioritized_signals": ["engagement"],
                    "spam_filters": ["low quality"],
                    "diversity_mechanisms": ["topic variety"]
                },
                "diversity_metrics": {
                    "diversity_score": 75,
                    "topic_entropy": 0.8,
                    "filter_bubble_risk": "Low",
                    "viewpoint_diversity": "High"
                },
                "opposing_viewpoints": {
                    "included": True,
                    "topics_with_diversity": ["AI"],
                    "explanation": "Balanced perspectives"
                },
                "temporal_analysis": {
                    "recency_bias": "Moderate",
                    "temporal_mix_explanation": "Balanced mix",
                    "content_freshness": "50/50"
                },
                "recommendation_explanations": [],
                "expected_outcome": "More AI content",
                "profile_report": "User interested in AI"
            },
            "tokens": {
                "completion_tokens": 100,
                "reasoning_tokens": 50,
                "total_tokens": 150
            }
        }
    )
    assert len(response.topics) == 1
    assert response.topics[0].topic == "AI"
    assert response.recommendations["tokens"]["total_tokens"] == 150

def test_insights_request_model():
    """Test InsightsRequest Pydantic model."""
    request = InsightsRequest(username="testuser")
    assert request.username == "testuser"

def test_insights_response_model():
    """Test InsightsResponse Pydantic model."""
    response = InsightsResponse(insights=["Insight 1", "Insight 2"])
    assert len(response.insights) == 2
    assert response.insights[0] == "Insight 1"

@pytest.mark.asyncio
async def test_generate_political_analysis():
    """Test political analysis generation."""
    result = await service.generate_political_analysis("Sample context about politics and policy")

    assert isinstance(result, dict)
    assert "report" in result
    assert "tokens" in result
    assert "political_spectrum" in result["report"]
    assert "key_political_topics" in result["report"]
    assert "ideological_markers" in result["report"]
    assert "engagement_level" in result["report"]
    assert "primary_concerns" in result["report"]
    assert "policy_interests" in result["report"]
    assert "analysis_summary" in result["report"]
    assert "disclaimer" in result["report"]

@pytest.mark.asyncio
async def test_political_analysis_fallback():
    """Test political analysis fallback response."""
    # This tests the fallback when API fails
    result = await service._fallback_political_response()

    assert isinstance(result, dict)
    assert "report" in result
    assert result["report"]["political_spectrum"]["position"] == "Center"
    assert result["report"]["political_spectrum"]["confidence"] == 0.3
    assert "disclaimer" in result["report"]

def test_political_analysis_response_model():
    """Test PoliticalAnalysisResponse Pydantic model."""
    from services.xai_service import PoliticalAnalysisResponse, PoliticalAnalysisReport, PoliticalSpectrum

    response = PoliticalAnalysisResponse(
        report=PoliticalAnalysisReport(
            political_spectrum=PoliticalSpectrum(
                position="Center-Right",
                confidence=0.75,
                reasoning="Based on policy positions"
            ),
            key_political_topics=["Healthcare", "Economy"],
            ideological_markers=["Conservative", "Pro-business"],
            engagement_level="Active",
            primary_concerns=["Inflation", "Regulation"],
            policy_interests=["Tax Policy", "Healthcare Reform"],
            analysis_summary="User shows center-right political alignment",
            disclaimer="This is an AI analysis"
        ),
        tokens={"completion_tokens": 100, "reasoning_tokens": 50, "total_tokens": 150}
    )

    assert response.report.political_spectrum.position == "Center-Right"
    assert response.report.political_spectrum.confidence == 0.75
    assert len(response.report.key_political_topics) == 2
    assert response.tokens["total_tokens"] == 150