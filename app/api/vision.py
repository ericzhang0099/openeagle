"""
Vision API Routes

API endpoints for image analysis, object detection, and OCR.
"""

import time
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from typing import Optional

from app.services import detector, ocr_service, analyzer
from app.models import (
    BaseResponse,
    DetectResponseData,
    OCRResponseData,
    AnalyzeResponseData,
)
from app.utils import (
    logger,
    validate_image,
    bytes_to_cv2,
    resize_image_if_needed,
)
from app.core import VisionServiceException

router = APIRouter()


def create_response(data: Optional[dict] = None, message: str = "success") -> dict:
    """Create standardized API response."""
    return {
        "code": 0,
        "message": message,
        "data": data,
        "timestamp": int(time.time()),
    }


def create_error_response(code: int, message: str) -> JSONResponse:
    """Create standardized error response."""
    return JSONResponse(
        status_code=200,
        content={
            "code": code,
            "message": message,
            "timestamp": int(time.time()),
        },
    )


@router.post(
    "/analyze",
    response_model=BaseResponse,
    summary="Analyze Image",
    description="Upload an image for AI analysis and description generation.",
)
async def analyze_image(
    image: UploadFile = File(..., description="Image file to analyze"),
    task: str = Form("描述这张图片", description="Analysis task description"),
):
    """
    Analyze an image and generate a description.
    
    - **image**: Image file (JPG, PNG, WEBP supported)
    - **task**: Custom analysis prompt (optional)
    
    Returns analysis result as natural language description.
    """
    try:
        # Read and validate image
        content = await image.read()
        validate_image(content)
        
        logger.info(f"Analyzing image: {image.filename}, task: {task}")
        
        # Analyze image
        result = await analyzer.analyze(content, task)
        
        return create_response(
            data=result,
            message="Analysis completed successfully"
        )
        
    except VisionServiceException as e:
        logger.error(f"Analysis error: {e.message}")
        return create_error_response(e.code, e.message)
    except Exception as e:
        logger.error(f"Unexpected error in analyze: {e}")
        return create_error_response(3000, f"Analysis failed: {str(e)}")


@router.post(
    "/detect",
    response_model=BaseResponse,
    summary="Object Detection",
    description="Detect objects in an image using YOLOv8.",
)
async def detect_objects(
    image: UploadFile = File(..., description="Image file for detection"),
    threshold: float = Form(0.5, ge=0, le=1, description="Confidence threshold"),
):
    """
    Detect objects in an image.
    
    - **image**: Image file (JPG, PNG, WEBP supported)
    - **threshold**: Minimum confidence (0.0-1.0, default 0.5)
    
    Returns list of detected objects with bounding boxes.
    """
    try:
        # Read and validate image
        content = await image.read()
        validate_image(content)
        
        logger.info(f"Detecting objects in: {image.filename}, threshold: {threshold}")
        
        # Convert to OpenCV format
        cv2_image = bytes_to_cv2(content)
        
        # Resize if needed for performance
        cv2_image = resize_image_if_needed(cv2_image, max_size=1920)
        
        # Detect objects
        detections = await detector.detect(cv2_image, threshold)
        
        return create_response(
            data={"detections": detections},
            message=f"Detected {len(detections)} objects"
        )
        
    except VisionServiceException as e:
        logger.error(f"Detection error: {e.message}")
        return create_error_response(e.code, e.message)
    except Exception as e:
        logger.error(f"Unexpected error in detect: {e}")
        return create_error_response(3000, f"Detection failed: {str(e)}")


@router.post(
    "/ocr",
    response_model=BaseResponse,
    summary="OCR Text Recognition",
    description="Extract text from an image using EasyOCR.",
)
async def recognize_text(
    image: UploadFile = File(..., description="Image file for OCR"),
    language: str = Form("ch_sim,en", description="Language codes (comma-separated)"),
):
    """
    Recognize text in an image.
    
    - **image**: Image file (JPG, PNG, WEBP supported)
    - **language**: Language codes like "ch_sim,en" or "en" (default: "ch_sim,en")
    
    Supported languages:
    - ch_sim: Simplified Chinese
    - ch_tra: Traditional Chinese
    - en: English
    - ja: Japanese
    - ko: Korean
    
    Returns recognized text and bounding boxes.
    """
    try:
        # Read and validate image
        content = await image.read()
        validate_image(content)
        
        logger.info(f"OCR on image: {image.filename}, language: {language}")
        
        # Convert to OpenCV format
        cv2_image = bytes_to_cv2(content)
        
        # Resize if needed
        cv2_image = resize_image_if_needed(cv2_image, max_size=2560)
        
        # Perform OCR
        result = await ocr_service.recognize(cv2_image, language)
        
        return create_response(
            data=result,
            message=f"OCR completed, found {len(result['boxes'])} text regions"
        )
        
    except VisionServiceException as e:
        logger.error(f"OCR error: {e.message}")
        return create_error_response(e.code, e.message)
    except Exception as e:
        logger.error(f"Unexpected error in OCR: {e}")
        return create_error_response(3000, f"OCR failed: {str(e)}")
