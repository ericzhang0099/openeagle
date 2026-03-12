"""
Object Detection Service

YOLO-based object detection implementation.
"""

import os
from pathlib import Path
from typing import List, Dict, Any
import numpy as np

from app.core.config import settings
from app.core.exceptions import ModelLoadError, ImageProcessingError
from app.utils.logger import logger


class ObjectDetector:
    """
    Object detector using YOLOv8.
    
    Attributes:
        model: YOLO model instance
        device: Computation device (cpu/cuda)
        confidence_threshold: Minimum confidence for detections
    """
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        """Singleton pattern to ensure model is loaded only once."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize detector if not already initialized."""
        if ObjectDetector._initialized:
            return
        
        self.model = None
        self.device = settings.MODEL_DEVICE
        self.confidence_threshold = settings.YOLO_CONFIDENCE_THRESHOLD
        self.model_path = settings.YOLO_MODEL_PATH
        
        self._load_model()
        ObjectDetector._initialized = True
    
    def _load_model(self) -> None:
        """
        Load YOLO model.
        
        Raises:
            ModelLoadError: If model fails to load
        """
        try:
            # Import here to avoid loading on startup if not needed
            from ultralytics import YOLO
            
            # Check if model file exists
            if not Path(self.model_path).exists():
                logger.info(f"Model not found at {self.model_path}, downloading...")
                # Download nano model (smallest and fastest)
                self.model = YOLO("yolov8n.pt")
                # Save for future use
                Path(self.model_path).parent.mkdir(parents=True, exist_ok=True)
                self.model.save(self.model_path)
            else:
                logger.info(f"Loading YOLO model from {self.model_path}")
                self.model = YOLO(self.model_path)
            
            logger.info(f"YOLO model loaded successfully on {self.device}")
            
        except Exception as e:
            logger.error(f"Failed to load YOLO model: {e}")
            raise ModelLoadError(f"Failed to load YOLO model: {str(e)}")
    
    async def detect(
        self,
        image: np.ndarray,
        threshold: float = None
    ) -> List[Dict[str, Any]]:
        """
        Detect objects in image.
        
        Args:
            image: OpenCV image array (BGR format)
            threshold: Confidence threshold (uses default if None)
            
        Returns:
            List of detection results
            
        Raises:
            ImageProcessingError: If detection fails
        """
        if self.model is None:
            raise ModelLoadError("Model not loaded")
        
        threshold = threshold or self.confidence_threshold
        
        try:
            # Run inference
            results = self.model(image, conf=threshold, device=self.device)
            
            # Parse results
            detections = []
            for result in results:
                boxes = result.boxes
                for box in boxes:
                    detection = {
                        "bbox": box.xyxy[0].cpu().numpy().tolist(),
                        "class": result.names[int(box.cls)],
                        "confidence": float(box.conf),
                        "class_id": int(box.cls),
                    }
                    detections.append(detection)
            
            logger.info(f"Detected {len(detections)} objects")
            return detections
            
        except Exception as e:
            logger.error(f"Object detection failed: {e}")
            raise ImageProcessingError(f"Detection failed: {str(e)}")


# Global detector instance
detector = ObjectDetector()
