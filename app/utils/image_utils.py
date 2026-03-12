"""
Image Utilities

Helper functions for image processing.
"""

import cv2
import numpy as np
from PIL import Image
from pathlib import Path
from typing import Tuple, Union
import io

from app.core.config import settings
from app.core.exceptions import InvalidImageError, FileTooLargeError
from app.utils.logger import logger


def validate_image(file_content: bytes) -> None:
    """
    Validate image file content.
    
    Args:
        file_content: Raw file bytes
        
    Raises:
        FileTooLargeError: If file exceeds max size
        InvalidImageError: If file is not a valid image
    """
    # Check file size
    if len(file_content) > settings.MAX_FILE_SIZE:
        raise FileTooLargeError(
            f"File size {len(file_content)} exceeds limit {settings.MAX_FILE_SIZE}"
        )
    
    # Try to decode as image
    try:
        image_array = np.frombuffer(file_content, np.uint8)
        image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
        if image is None:
            raise InvalidImageError("Cannot decode image file")
    except Exception as e:
        logger.error(f"Image validation failed: {e}")
        raise InvalidImageError(f"Invalid image format: {str(e)}")


def bytes_to_cv2(file_content: bytes) -> np.ndarray:
    """
    Convert file bytes to OpenCV image.
    
    Args:
        file_content: Raw file bytes
        
    Returns:
        OpenCV image array
    """
    image_array = np.frombuffer(file_content, np.uint8)
    image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
    if image is None:
        raise InvalidImageError("Failed to decode image")
    return image


def bytes_to_pil(file_content: bytes) -> Image.Image:
    """
    Convert file bytes to PIL Image.
    
    Args:
        file_content: Raw file bytes
        
    Returns:
        PIL Image object
    """
    try:
        image = Image.open(io.BytesIO(file_content))
        return image.convert("RGB")
    except Exception as e:
        logger.error(f"Failed to convert to PIL image: {e}")
        raise InvalidImageError(f"Failed to process image: {str(e)}")


def cv2_to_pil(cv2_image: np.ndarray) -> Image.Image:
    """
    Convert OpenCV image to PIL Image.
    
    Args:
        cv2_image: OpenCV image array
        
    Returns:
        PIL Image object
    """
    # Convert BGR to RGB
    rgb_image = cv2.cvtColor(cv2_image, cv2.COLOR_BGR2RGB)
    return Image.fromarray(rgb_image)


def pil_to_cv2(pil_image: Image.Image) -> np.ndarray:
    """
    Convert PIL Image to OpenCV image.
    
    Args:
        pil_image: PIL Image object
        
    Returns:
        OpenCV image array
    """
    # Convert RGB to BGR
    rgb_array = np.array(pil_image)
    return cv2.cvtColor(rgb_array, cv2.COLOR_RGB2BGR)


def get_image_size(file_content: bytes) -> Tuple[int, int]:
    """
    Get image dimensions without full decoding.
    
    Args:
        file_content: Raw file bytes
        
    Returns:
        Tuple of (width, height)
    """
    try:
        image = Image.open(io.BytesIO(file_content))
        return image.size
    except Exception as e:
        logger.error(f"Failed to get image size: {e}")
        raise InvalidImageError(f"Failed to read image size: {str(e)}")


def resize_image_if_needed(
    image: np.ndarray,
    max_size: int = 1920
) -> np.ndarray:
    """
    Resize image if it exceeds max dimensions.
    
    Args:
        image: OpenCV image array
        max_size: Maximum dimension size
        
    Returns:
        Resized image if needed
    """
    height, width = image.shape[:2]
    max_dim = max(height, width)
    
    if max_dim > max_size:
        scale = max_size / max_dim
        new_width = int(width * scale)
        new_height = int(height * scale)
        image = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)
        logger.info(f"Resized image from {width}x{height} to {new_width}x{new_height}")
    
    return image


def save_temp_image(file_content: bytes, filename: str) -> Path:
    """
    Save uploaded file to temp directory.
    
    Args:
        file_content: Raw file bytes
        filename: Original filename
        
    Returns:
        Path to saved file
    """
    temp_dir = Path(settings.TEMP_DIR)
    temp_dir.mkdir(parents=True, exist_ok=True)
    
    temp_path = temp_dir / filename
    counter = 1
    while temp_path.exists():
        stem = Path(filename).stem
        suffix = Path(filename).suffix
        temp_path = temp_dir / f"{stem}_{counter}{suffix}"
        counter += 1
    
    with open(temp_path, "wb") as f:
        f.write(file_content)
    
    logger.debug(f"Saved temp file: {temp_path}")
    return temp_path


def cleanup_temp_file(file_path: Path) -> None:
    """
    Remove temporary file.
    
    Args:
        file_path: Path to file to remove
    """
    try:
        if file_path.exists():
            file_path.unlink()
            logger.debug(f"Cleaned up temp file: {file_path}")
    except Exception as e:
        logger.warning(f"Failed to cleanup temp file {file_path}: {e}")
