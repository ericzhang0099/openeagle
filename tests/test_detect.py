"""
Test Object Detection

Unit tests for object detection endpoint.
"""

import pytest
from fastapi.testclient import TestClient
import numpy as np
from PIL import Image
import io

from app.main import app

client = TestClient(app)


def create_test_image(width=640, height=480, color=(255, 0, 0)):
    """Create a simple test image."""
    image = Image.new('RGB', (width, height), color)
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)
    return img_byte_arr


def test_detect_endpoint():
    """Test object detection endpoint."""
    # Create test image
    test_image = create_test_image()
    
    # Send request
    response = client.post(
        "/api/v1/vision/detect",
        files={"image": ("test.png", test_image, "image/png")},
        data={"threshold": 0.5}
    )
    
    # Check response
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 0
    assert "data" in data
    assert "detections" in data["data"]
    assert isinstance(data["data"]["detections"], list)


def test_detect_invalid_file():
    """Test detection with invalid file."""
    response = client.post(
        "/api/v1/vision/detect",
        files={"image": ("test.txt", b"not an image", "text/plain")}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["code"] != 0  # Should return error


def test_detect_threshold_validation():
    """Test threshold parameter validation."""
    test_image = create_test_image()
    
    # Test with invalid threshold (> 1)
    response = client.post(
        "/api/v1/vision/detect",
        files={"image": ("test.png", test_image, "image/png")},
        data={"threshold": 1.5}
    )
    
    assert response.status_code == 422  # Validation error
