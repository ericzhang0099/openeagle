"""
OCR Service

EasyOCR-based text recognition implementation.
"""

import numpy as np
from typing import List, Dict, Any
import re

from app.core.config import settings
from app.core.exceptions import ModelLoadError, ImageProcessingError
from app.utils.logger import logger


class OCRService:
    """
    OCR service using EasyOCR.
    
    Attributes:
        reader: EasyOCR reader instance
        languages: List of supported languages
        gpu: Whether to use GPU
    """
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        """Singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize OCR if not already initialized."""
        if OCRService._initialized:
            return
        
        self.reader = None
        self.languages = settings.OCR_LANGUAGES
        self.gpu = settings.OCR_GPU and settings.MODEL_DEVICE == "cuda"
        
        self._load_model()
        OCRService._initialized = True
    
    def _load_model(self) -> None:
        """
        Load EasyOCR model.
        
        Raises:
            ModelLoadError: If model fails to load
        """
        try:
            import easyocr
            
            logger.info(f"Loading EasyOCR model with languages: {self.languages}")
            self.reader = easyocr.Reader(
                self.languages,
                gpu=self.gpu,
                verbose=False,
            )
            logger.info("EasyOCR model loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load EasyOCR model: {e}")
            raise ModelLoadError(f"Failed to load OCR model: {str(e)}")
    
    async def recognize(
        self,
        image: np.ndarray,
        language: str = None
    ) -> Dict[str, Any]:
        """
        Recognize text in image.
        
        Args:
            image: OpenCV image array (BGR format)
            language: Language code(s), comma-separated (uses default if None)
            
        Returns:
            Dictionary with text, confidence, and boxes
            
        Raises:
            ImageProcessingError: If recognition fails
        """
        if self.reader is None:
            raise ModelLoadError("OCR model not loaded")
        
        try:
            # Use specified language or default
            languages = language.split(",") if language else self.languages
            
            # Convert BGR to RGB for EasyOCR
            image_rgb = np.array(image)
            if len(image_rgb.shape) == 3:
                import cv2
                image_rgb = cv2.cvtColor(image_rgb, cv2.COLOR_BGR2RGB)
            
            # Run OCR
            results = self.reader.readtext(image_rgb)
            
            # Parse results
            boxes = []
            texts = []
            confidences = []
            
            for (bbox, text, conf) in results:
                # Clean text
                text = text.strip()
                if not text:
                    continue
                
                box_result = {
                    "text": text,
                    "confidence": float(conf),
                    "bbox": [[float(x), float(y)] for x, y in bbox],
                }
                boxes.append(box_result)
                texts.append(text)
                confidences.append(float(conf))
            
            # Calculate average confidence
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0
            
            # Join all text
            full_text = " ".join(texts)
            
            logger.info(f"OCR recognized {len(boxes)} text regions")
            
            return {
                "text": full_text,
                "confidence": round(avg_confidence, 4),
                "boxes": boxes,
            }
            
        except Exception as e:
            logger.error(f"OCR recognition failed: {e}")
            raise ImageProcessingError(f"OCR failed: {str(e)}")


# Global OCR instance
ocr_service = OCRService()
