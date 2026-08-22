import pytest
from unittest.mock import AsyncMock, MagicMock

from application.services.recommendation_service import RecommendationService
from core.schemas.llm_recommendation_response import (
    LLMRecommendationResponse,
)
from core.schemas.recommendation_response import (
    RecommendationItemResponse,
)
from core.enums.priority import Priority


@pytest.mark.asyncio
async def test_recommendation_service_async_flow():

    # Arrange

    mock_retrieval_service = AsyncMock()
    mock_context_builder = MagicMock()
    mock_prompt_builder = MagicMock()
    mock_llm_service = AsyncMock()

    retrieved_chunks = [
        MagicMock(
            text="Drainage problems can cause water accumulation.",
            metadata={
                "document_id": "test.pdf",
                "page_number": 1,
            },
            score=0.95,
        )
    ]

    mock_retrieval_service.retrieve.return_value = retrieved_chunks

    mock_context_builder.build.return_value = (
        "Mocked Context String"
    )

    mock_prompt_builder.build.return_value = (
        "Mocked Prompt String"
    )

    mock_llm_service.generate.return_value = (
        LLMRecommendationResponse(
            problem="تراكم المياه في الأرض",
            recommendations=[
                RecommendationItemResponse(
                    recommendation="تحسين تصريف المياه",
                    reasoning="لتقليل تراكم المياه",
                    category="drainage",
                    priority=Priority.HIGH,
                    confidence=0.95,
                )
            ],
        )
    )

    service = RecommendationService(
        retrieval_service=mock_retrieval_service,
        context_builder_service=mock_context_builder,
        prompt_builder_service=mock_prompt_builder,
        llm=mock_llm_service,
    )

    # Act

    response = await service.recommend(
        request_id="req-999",
        query="عندي مشكلة في تراكم المياه",
        top_k=5,
    )

    # Assert - final response

    assert response is not None
    assert response.request_id == "req-999"
    assert response.problem == "تراكم المياه في الأرض"
    assert len(response.recommendations) == 1

    recommendation = response.recommendations[0]

    assert recommendation.recommendation == "تحسين تصريف المياه"
    assert recommendation.category == "drainage"
    assert recommendation.priority == Priority.HIGH
    assert recommendation.confidence == 0.95

    # Assert - retrieval

    mock_retrieval_service.retrieve.assert_awaited_once_with(
        query="عندي مشكلة في تراكم المياه",
        top_k=5,
    )

    # Assert - context builder

    mock_context_builder.build.assert_called_once_with(
        retrieved_chunks
    )

    # Assert - prompt builder

    mock_prompt_builder.build.assert_called_once_with(
        query="عندي مشكلة في تراكم المياه",
        context="Mocked Context String",
        max_recommendations=3,
    )

    # Assert - LLM

    mock_llm_service.generate.assert_awaited_once_with(
        "Mocked Prompt String"
    )