"""
Image Analysis Service

Image understanding and description using LLaVA or external API.
"""

import base64
from io import BytesIO
from typing import Dict, Any, Optional
import aiohttp

from app.core.config import settings
from app.core.exceptions import ImageProcessingError
from app.utils.logger import logger


class ImageAnalyzer:
    """
    Image analysis service for generating descriptions.
    
    Supports both local LLaVA model and external API.
    """
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        """Singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize analyzer if not already initialized."""
        if ImageAnalyzer._initialized:
            return
        
        self.mode = settings.ANALYSIS_MODE
        self.api_url = settings.LLAVA_API_URL
        self.api_key = settings.LLAVA_API_KEY
        
        if self.mode == "local":
            self._load_local_model()
        
        ImageAnalyzer._initialized = True
    
    def _load_local_model(self) -> None:
        """Load local LLaVA model (if configured)."""
        # TODO: Implement local LLaVA loading
        # This requires significant GPU resources
        logger.warning("Local LLaVA model not yet implemented, using API mode")
        self.mode = "api"
    
    def _encode_image(self, image_bytes: bytes) -> str:
        """
        Encode image to base64 string.
        
        Args:
            image_bytes: Raw image bytes
            
        Returns:
            Base64 encoded string
        """
        return base64.b64encode(image_bytes).decode("utf-8")
    
    async def _call_external_api(
        self,
        image_bytes: bytes,
        task: str
    ) -> str:
        """
        Call external vision API for analysis.
        
        Args:
            image_bytes: Raw image bytes
            task: Analysis task description
            
        Returns:
            Analysis result text
            
        Raises:
            ImageProcessingError: If API call fails
        """
        # For MVP, we'll use a simple fallback description
        # In production, this should call actual vision API (OpenAI, Claude, etc.)
        
        if not self.api_url:
            # Fallback for MVP: return generic response
            logger.warning("No vision API configured, using fallback")
            return self._fallback_analysis(task)
        
        try:
            # Encode image
            image_b64 = self._encode_image(image_bytes)
            
            # Prepare request
            headers = {
                "Content-Type": "application/json",
            }
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"
            
            payload = {
                "model": "gpt-4-vision-preview",
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": task},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_b64}"
                                }
                            }
                        ]
                    }
                ],
                "max_tokens": 500,
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.api_url,
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        raise ImageProcessingError(f"API error: {error_text}")
                    
                    result = await response.json()
                    return result["choices"][0]["message"]["content"]
                    
        except Exception as e:
            logger.error(f"API call failed: {e}")
            return self._fallback_analysis(task)
    
    def _fallback_analysis(self, task: str) -> str:
        """
        Generate fallback analysis when API is not available.
        
        Args:
            task: Original task description
            
        Returns:
            Fallback response
        """
        # MVP fallback: return a generic response
        # This should be replaced with actual model inference
        return (
            "这是一张图片。"
            "由于视觉分析模型尚未完全配置，暂时无法提供详细描述。"
            "请确保已配置 LLAVA_API_URL 和 LLAVA_API_KEY 环境变量，"
            "或等待本地模型加载完成。"
        )
    
    async def analyze(
        self,
        image_bytes: bytes,
        task: str = "描述这张图片"
    ) -> Dict[str, Any]:
        """
        Analyze image and generate description.
        
        Args:
            image_bytes: Raw image bytes
            task: Analysis task description
            
        Returns:
            Dictionary with analysis result
        """
        logger.info(f"Analyzing image with task: {task}")
        
        if self.mode == "api":
            result = await self._call_external_api(image_bytes, task)
        else:
            # Local model (not implemented yet)
            result = self._fallback_analysis(task)
        
        return {"result": result}


# Global analyzer instance
analyzer = ImageAnalyzer()
