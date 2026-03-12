"""
Application Configuration

Pydantic settings for vision service configuration.
"""

from pydantic_settings import BaseSettings
from typing import List
import json


class Settings(BaseSettings):
    """Application settings."""
    
    # Server settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True
    
    # Model settings
    MODEL_DEVICE: str = "cpu"
    YOLO_MODEL_PATH: str = "./models/yolov8n.pt"
    YOLO_CONFIDENCE_THRESHOLD: float = 0.5
    
    # OCR settings
    OCR_LANGUAGES: List[str] = ["ch_sim", "en"]
    OCR_GPU: bool = False
    
    # Image Analysis settings
    ANALYSIS_MODE: str = "api"  # "local" or "api"
    LLAVA_API_URL: str = ""
    LLAVA_API_KEY: str = ""
    
    # Temp files
    TEMP_DIR: str = "./temp"
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Parse OCR_LANGUAGES if it's a string
        if isinstance(self.OCR_LANGUAGES, str):
            try:
                self.OCR_LANGUAGES = json.loads(self.OCR_LANGUAGES)
            except json.JSONDecodeError:
                self.OCR_LANGUAGES = ["ch_sim", "en"]


# Global settings instance
settings = Settings()
