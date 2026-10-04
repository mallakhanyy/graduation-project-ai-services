"""
Request and Response schemas for the Vision Service API.
"""

from typing import Optional, List
from pydantic import BaseModel, Field

# ============================================
# Request Schemas
# ============================================
class PredictionRequest(BaseModel):
    """Request model for prediction endpoint."""
    file: bytes = Field(..., description="Image file data")

# ============================================
# Response Schemas
# ============================================
class PredictionResponse(BaseModel):
    """Response model for prediction endpoint."""
    status: str = Field(..., description="Status: success, low_confidence, poor_quality, error")
    problem: Optional[str] = Field(None, description="Problem name in Arabic")
    problem_code: Optional[str] = Field(None, description="Problem code")
    confidence: Optional[str] = Field(None, description="Confidence percentage as string")
    confidence_raw: Optional[float] = Field(None, description="Raw confidence score")
    severity: Optional[str] = Field(None, description="Severity level")
    recommendation: Optional[str] = Field(None, description="Recommendation text")
    explanation: Optional[str] = Field(None, description="Detailed explanation")
    repair_steps: Optional[List[str]] = Field(None, description="Repair instructions")
    message: Optional[str] = Field(None, description="Status message")
    suggestion: Optional[str] = Field(None, description="Suggestion for user")
    timestamp: str = Field(..., description="ISO timestamp")

class ErrorResponse(BaseModel):
    """Error response model."""
    detail: str = Field(..., description="Error details")
    code: Optional[str] = Field(None, description="Error code")
    timestamp: str = Field(..., description="ISO timestamp")