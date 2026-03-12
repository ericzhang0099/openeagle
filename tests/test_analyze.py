"""
Test Image Analysis

Unit tests for image analysis endpoint.
"""

import pytest
from fastapi.testclient import TestClient
from PIL import Image
import io

from app.main import app

client = TestClient(app)


def create_test_image():
    """Create a simple test image."""
    image = Image.new('RGB', (640, 480), color='blue')
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format='JPEG')
    img_byte_arr.seek(0)
    return img_byte_arr


def test_analyze_endpoint():
    """Test image analysis endpoint."""
    test_image = create_test_image()
    
    response = client.post(
        "/api/v1/vision/analyze",
        files={"image": ("test.jpg", test_image, "image/jpeg")},
        data={"task": "描述这张图片"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 0
    assert "data" in data
    assert "result" in data["data"]


def test_analyze_custom_task():
    """Test analysis with custom task."""
    test_image = create_test_image()
    
    response = client.post(
        "/api/v1/vision/analyze",
        files={"image": ("test.jpg", test_image, "image/jpeg")},
        data={"task": "What color is dominant in this image?"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 0
    assert "result" in data["data"]
