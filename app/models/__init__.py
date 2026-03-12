"""Models module exports."""

from app.models.schemas import (
    BaseResponse,
    DetectionResult,
    DetectResponseData,
    OCRBoxResult,
    OCRResponseData,
    AnalyzeResponseData,
    ErrorResponse,
)

__all__ = [
    "BaseResponse",
    "DetectionResult",
    "DetectResponseData",
    "OCRBoxResult",
    "OCRResponseData",
    "AnalyzeResponseData",
    "ErrorResponse",
]
