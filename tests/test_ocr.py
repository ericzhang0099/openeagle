"""
Test OCR

Unit tests for OCR endpoint.
"""

import pytest
from fastapi.testclient import TestClient
from PIL import Image, ImageDraw, ImageFont
import io

from app.main import app

client = TestClient(app)


def create_test_image_with_text(text="Hello World"):
    """Create a test image with text."""
    image = Image.new('RGB', (400, 100), color='white')
    draw = ImageDraw.Draw(image)
    
    # Try to use default font, fallback to default if not available
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 32)
    except:
        font = ImageFont.load_default()
    
    draw.text((10, 30), text, fill='black', font=font)
    
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)
    return img_byte_arr


def test_ocr_endpoint():
    """Test OCR endpoint."""
    # Create test image with text
    test_image = create_test_image_with_text("TEST")
    
    # Send request
    response = client.post(
        "/api/v1/vision/ocr",
        files={"image": ("test.png", test_image, "image/png")},
        data={"language": "en"}
    )
    
    # Check response
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 0
    assert "data" in data
    assert "text" in data["data"]
    assert "confidence" in data["data"]
    assert "boxes" in data["data"]


def test_ocr_chinese():
    """Test OCR with Chinese text."""
    test_image = create_test_image_with_text("中文测试")
    
    response = client.post(
        "/api/v1/vision/ocr",
        files={"image": ("test.png", test_image, "image/png")},
        data={"language": "ch_sim,en"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 0


def test_ocr_invalid_file():
    """Test OCR with invalid file."""
    response = client.post(
        "/api/v1/vision/ocr",
        files={"image": ("test.txt", b"not an image", "text/plain")}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["code"] != 0
