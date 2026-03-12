"""
Pytest Configuration

Test fixtures and configuration for vision service tests.
"""

import pytest
from fastapi.testclient import TestClient
from PIL import Image
import io
import numpy as np

from app.main import app


@pytest.fixture
def client():
    """Create a test client."""
    return TestClient(app)


@pytest.fixture
def sample_image():
    """Create a sample test image."""
    image = Image.new('RGB', (640, 480), color='blue')
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format='JPEG')
    img_byte_arr.seek(0)
    return img_byte_arr


@pytest.fixture
def sample_image_with_text():
    """Create a sample test image with text."""
    image = Image.new('RGB', (400, 100), color='white')
    from PIL import ImageDraw, ImageFont
    draw = ImageDraw.Draw(image)
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 32)
    except:
        font = ImageFont.load_default()
    draw.text((10, 30), "TEST TEXT", fill='black', font=font)
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)
    return img_byte_arr


@pytest.fixture
def temp_dir(tmp_path):
    """Create a temporary directory for tests."""
    return tmp_path
