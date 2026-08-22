from uuid import uuid4

from fastapi import APIRouter, Request
from pydantic import BaseModel, Field

from core.schemas.recommendation_response import RecommendationResponse


class RecommendationRequest(BaseModel):
    query: str = Field(min_length=1)
    top_k: int = Field(default=5, ge=1, le=20)


router = APIRouter(
    prefix="/recommendations",
    tags=["Recommendations"],
)


@router.post(
    "",
    response_model=RecommendationResponse,
)
async def create_recommendation(
    request: Request,
    body: RecommendationRequest,
):
    service = request.app.state.container.recommendation_service

    return await service.recommend(
        request_id=str(uuid4()),
        query=body.query,
        top_k=body.top_k,
    )