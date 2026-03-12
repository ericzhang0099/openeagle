"""
Custom Exceptions

Application-specific exceptions for vision service.
"""


class VisionServiceException(Exception):
    """Base exception for vision service."""
    
    def __init__(self, message: str, code: int = 3000):
        self.message = message
        self.code = code
        super().__init__(self.message)


class ImageProcessingError(VisionServiceException):
    """Error during image processing."""
    
    def __init__(self, message: str = "Image processing failed"):
        super().__init__(message, code=3001)


class ModelLoadError(VisionServiceException):
    """Error loading AI model."""
    
    def __init__(self, message: str = "Failed to load model"):
        super().__init__(message, code=3002)


class InvalidImageError(VisionServiceException):
    """Invalid image file."""
    
    def __init__(self, message: str = "Invalid image file"):
        super().__init__(message, code=1000)


class FileTooLargeError(VisionServiceException):
    """File size exceeds limit."""
    
    def __init__(self, message: str = "File too large"):
        super().__init__(message, code=1000)
