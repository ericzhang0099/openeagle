"""
Pydantic Schemas

Request and response models for API endpoints.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Any


# ============== Response Models ==============

class BaseResponse(BaseModel):
    """Base API response model."""
    code: int = Field(..., description="Status code: 0 for success, non-zero for error")
    message: str = Field(..., description="Response message")
    data: Optional[Any] = Field(None, description="Response data")
    timestamp: int = Field(..., description="Unix timestamp")


class DetectionResult(BaseModel):
    """Object detection result."""
    bbox: List[float] = Field(..., description="Bounding box [x1, y1, x2, y2]")
    class_name: str = Field(..., description="Detected class name")
    confidence: float = Field(..., ge=0, le=1, description="Confidence score")
    class_id: int = Field(..., description="Class ID")


class DetectResponseData(BaseModel):
    """Detect endpoint response data."""
    detections: List[DetectionResult] = Field(default_factory=list)


class OCRBoxResult(BaseModel):
    """OCR text box result."""
    text: str = Field(..., description="Recognized text")
    confidence: float = Field(..., ge=0, le=1, description="Confidence score")
    bbox: List[List[float]] = Field(..., description="Text bounding box coordinates")


class OCRResponseData(BaseModel):
    """OCR endpoint response data."""
    text: str = Field(..., description="Full recognized text")
    confidence: float = Field(..., ge=0, le=1, description="Average confidence")
    boxes: List[OCRBoxResult] = Field(default_factory=list)


class AnalyzeResponseData(BaseModel):
    """Analyze endpoint response data."""
    result: str = Field(..., description="Analysis result description")


# ============== Error Response Models ==============

class ErrorResponse(BaseModel):
    """Error response model."""
    code: int = Field(..., description="Error code")
    message: str = Field(..., description="Error message")
    timestamp: int = Field(..., description="Unix timestamp")
