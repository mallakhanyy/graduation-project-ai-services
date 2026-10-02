import httpx
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from infrastructure.llm.qwen3_llm_service import Qwen3LLMService
from core.schemas.llm_recommendation_response import (
    LLMRecommendationResponse,
)


VALID_CONTENT = """
{
    "problem": "تراكم المياه في الأرض",
    "recommendations": [
        {
            "recommendation": "تحسين تصريف المياه",
            "reasoning": "لتقليل تراكم المياه",
            "priority": "high",
            "category": "drainage",
            "confidence": 0.95
        }
    ]
}
"""


@pytest.mark.asyncio
async def test_llm_generate_success():

    mock_response = MagicMock()

    mock_response.json.return_value = {
        "message": {
            "content": VALID_CONTENT
        }
    }

    mock_response.raise_for_status.return_value = None

    with patch(
        "httpx.AsyncClient.post",
        new_callable=AsyncMock,
        return_value=mock_response,
    ) as mock_post:

        service = Qwen3LLMService()

        result = await service.generate(
            "عندي مشكلة في تراكم المياه"
        )

    assert isinstance(result, LLMRecommendationResponse)
    assert result.problem == "تراكم المياه في الأرض"
    assert len(result.recommendations) == 1

    mock_post.assert_awaited_once()


@pytest.mark.asyncio
async def test_llm_generate_invalid_json():

    mock_response = MagicMock()

    mock_response.json.return_value = {
        "message": {
            "content": "this is not valid json"
        }
    }

    mock_response.raise_for_status.return_value = None

    with patch(
        "httpx.AsyncClient.post",
        new_callable=AsyncMock,
        return_value=mock_response,
    ):

        service = Qwen3LLMService()

        with pytest.raises(
            ValueError,
            match="invalid JSON",
        ):
            await service.generate("test prompt")


@pytest.mark.asyncio
async def test_llm_generate_http_error():

    mock_response = MagicMock()

    mock_response.raise_for_status.side_effect = (
        httpx.HTTPStatusError(
            "Server error",
            request=httpx.Request(
                "POST",
                "http://test",
            ),
            response=httpx.Response(500),
        )
    )

    with patch(
        "httpx.AsyncClient.post",
        new_callable=AsyncMock,
        return_value=mock_response,
    ):

        service = Qwen3LLMService()

        with pytest.raises(httpx.HTTPStatusError):
            await service.generate("test prompt")