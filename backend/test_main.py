import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from services.xai_service import XAIService
from main import AnalyzeRequest, AnalyzeResponse

# Create service instance for testing
service = XAIService("test_key")

@pytest.mark.asyncio
async def test_gather_user_context_success():
    """Test successful context gathering."""
    mock_client = AsyncMock()
    mock_chat = AsyncMock()
    mock_response = MagicMock()
    mock_response.content = "Sample X search results"
    mock_chat.get_response.return_value = mock_response
    mock_client.chat.create.return_value = mock_chat

    with patch('services.xai_service.AsyncClient', return_value=mock_client):
        result = await service.gather_user_context("testuser")
        assert "Sample X search results" in result

@pytest.mark.asyncio
async def test_gather_user_context_error():
    """Test error handling in context gathering."""
    with patch('services.xai_service.AsyncClient', side_effect=Exception("API Error")):
        result = await service.gather_user_context("testuser")
        assert "Mock context for testuser" in result

@pytest.mark.asyncio
async def test_analyze_context_success():
    """Test successful context analysis."""
    mock_client = AsyncMock()
    mock_chat = AsyncMock()
    mock_response = MagicMock()
    mock_response.content = "AI, Technology, Space"
    mock_chat.get_response.return_value = mock_response
    mock_client.chat.create.return_value = mock_chat

    with patch('services.xai_service.AsyncClient', return_value=mock_client):
        result = await service.analyze_context("Sample context")
        assert result == ["AI", "Technology", "Space"]

@pytest.mark.asyncio
async def test_analyze_context_error():
    """Test error handling in context analysis."""
    with patch('services.xai_service.AsyncClient', side_effect=Exception("API Error")):
        result = await service.analyze_context("Sample context")
        assert result == ["AI", "Technology", "Space", "Innovation", "Future"]

@pytest.mark.asyncio
async def test_generate_recommendations_success():
    """Test successful recommendation generation."""
    mock_client = AsyncMock()
    mock_chat = AsyncMock()
    mock_response = MagicMock()
    mock_response.content = "Here are your recommendations..."
    mock_chat.get_response.return_value = mock_response
    mock_client.chat.create.return_value = mock_chat

    with patch('services.xai_service.AsyncClient', return_value=mock_client):
        result = await service.generate_recommendations(["AI", "Tech"], "Sample context")
        assert "Here are your recommendations" in result

@pytest.mark.asyncio
async def test_generate_recommendations_error():
    """Test error handling in recommendation generation."""
    with patch('services.xai_service.AsyncClient', side_effect=Exception("API Error")):
        result = await service.generate_recommendations(["AI", "Tech"], "Sample context")
        assert "Based on your interests in AI, Tech" in result

def test_analyze_request_model():
    """Test Pydantic models."""
    request = AnalyzeRequest(username="testuser")
    assert request.username == "testuser"

    response = AnalyzeResponse(topics=["AI"], recommendations="Test recs")
    assert response.topics == ["AI"]
    assert response.recommendations == "Test recs"