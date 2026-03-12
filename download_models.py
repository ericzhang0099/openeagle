#!/usr/bin/env python3
"""
Model Download Script

Downloads required AI models for VisionClaw Vision Service.
"""

import os
import sys
from pathlib import Path

def download_yolo_model():
    """Download YOLOv8 model."""
    print("Downloading YOLOv8 model...")
    try:
        from ultralytics import YOLO
        
        model_path = Path("models/yolov8n.pt")
        if model_path.exists():
            print(f"  ✅ YOLOv8 model already exists at {model_path}")
            return True
        
        # Download model
        model = YOLO("yolov8n.pt")
        
        # Save to models directory
        model_path.parent.mkdir(parents=True, exist_ok=True)
        model.save(str(model_path))
        
        print(f"  ✅ YOLOv8 model downloaded to {model_path}")
        return True
    except Exception as e:
        print(f"  ❌ Failed to download YOLOv8: {e}")
        return False

def download_easyocr_models():
    """Download EasyOCR models."""
    print("Downloading EasyOCR models...")
    try:
        import easyocr
        
        # This will download models on first use
        reader = easyocr.Reader(['ch_sim', 'en'], verbose=False)
        print("  ✅ EasyOCR models ready")
        return True
    except Exception as e:
        print(f"  ❌ Failed to download EasyOCR: {e}")
        return False

def main():
    print("=" * 60)
    print("VisionClaw Vision Service - Model Download")
    print("=" * 60)
    print()
    
    # Create models directory
    Path("models").mkdir(exist_ok=True)
    
    results = []
    
    # Download YOLO
    results.append(("YOLOv8", download_yolo_model()))
    print()
    
    # Download EasyOCR
    results.append(("EasyOCR", download_easyocr_models()))
    print()
    
    # Summary
    print("=" * 60)
    success = sum(1 for _, r in results if r)
    total = len(results)
    print(f"Downloaded {success}/{total} models")
    
    if success == total:
        print("✅ All models ready!")
        return 0
    else:
        print("⚠️  Some models failed to download")
        return 1

if __name__ == "__main__":
    sys.exit(main())
