#!/bin/bash

# Integration Test Script for VisionClaw Vision Service
# Tests all three API endpoints

set -e

BASE_URL="http://localhost:8000"
TEMP_DIR="./temp_test"

echo "======================================"
echo "VisionClaw Vision Service - Integration Test"
echo "======================================"
echo ""

# Create temp directory
mkdir -p $TEMP_DIR

# Create test images
echo "Creating test images..."
python3 << 'EOF'
from PIL import Image, ImageDraw, ImageFont
import os

os.makedirs("./temp_test", exist_ok=True)

# Test image 1: Simple color
img1 = Image.new('RGB', (640, 480), color='blue')
img1.save('./temp_test/test1.jpg')

# Test image 2: With text
img2 = Image.new('RGB', (400, 100), color='white')
draw = ImageDraw.Draw(img2)
try:
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 32)
except:
    font = ImageFont.load_default()
draw.text((10, 30), "Hello World", fill='black', font=font)
img2.save('./temp_test/test2.png')

print("Test images created.")
EOF

echo ""
echo "======================================"
echo "Test 1: Health Check"
echo "======================================"
curl -s $BASE_URL/health | python3 -m json.tool || echo "Health check failed"
echo ""

echo "======================================"
echo "Test 2: Object Detection"
echo "======================================"
curl -s -X POST "$BASE_URL/api/v1/vision/detect" \
  -F "image=@./temp_test/test1.jpg" \
  -F "threshold=0.3" | python3 -m json.tool || echo "Detection test failed"
echo ""

echo "======================================"
echo "Test 3: OCR Text Recognition"
echo "======================================"
curl -s -X POST "$BASE_URL/api/v1/vision/ocr" \
  -F "image=@./temp_test/test2.png" \
  -F "language=en" | python3 -m json.tool || echo "OCR test failed"
echo ""

echo "======================================"
echo "Test 4: Image Analysis"
echo "======================================"
curl -s -X POST "$BASE_URL/api/v1/vision/analyze" \
  -F "image=@./temp_test/test1.jpg" \
  -F "task=描述这张图片" | python3 -m json.tool || echo "Analysis test failed"
echo ""

# Cleanup
rm -rf $TEMP_DIR

echo "======================================"
echo "Integration test completed"
echo "======================================"
