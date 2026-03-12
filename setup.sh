#!/bin/bash

# VisionClaw Vision Service Setup Script
# This script sets up the development environment

set -e

echo "======================================"
echo "VisionClaw Vision Service Setup"
echo "======================================"

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python version: $python_version"

# Create directories
echo "Creating directories..."
mkdir -p logs temp models

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Download YOLO model
echo "Downloading YOLOv8 model..."
if [ ! -f "models/yolov8n.pt" ]; then
    python3 -c "from ultralytics import YOLO; YOLO('yolov8n.pt').save('models/yolov8n.pt')"
    echo "YOLOv8 model downloaded."
else
    echo "YOLOv8 model already exists."
fi

echo ""
echo "======================================"
echo "Setup completed!"
echo "======================================"
echo ""
echo "To start the service:"
echo "  make run"
echo ""
echo "To run tests:"
echo "  make test"
echo ""
echo "API documentation:"
echo "  http://localhost:8000/docs"
echo ""
