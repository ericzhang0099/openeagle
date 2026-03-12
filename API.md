# API Documentation

## VisionClaw Vision Service API

Base URL: `/api/v1/vision`

### 1. Image Analysis

Analyze an image and generate a description.

**Endpoint:** `POST /api/v1/vision/analyze`

**Request:**
```bash
curl -X POST "http://localhost:8000/api/v1/vision/analyze" \
  -F "image=@photo.jpg" \
  -F "task=描述这张图片"
```

**Response:**
```json
{
  "code": 0,
  "message": "Analysis completed successfully",
  "data": {
    "result": "图片中有一只橘色的猫坐在窗台上，窗外是蓝天白云..."
  },
  "timestamp": 1710211200
}
```

### 2. Object Detection

Detect objects in an image using YOLOv8.

**Endpoint:** `POST /api/v1/vision/detect`

**Parameters:**
- `image`: Image file (required)
- `threshold`: Confidence threshold 0-1 (optional, default 0.5)

**Request:**
```bash
curl -X POST "http://localhost:8000/api/v1/vision/detect" \
  -F "image=@photo.jpg" \
  -F "threshold=0.5"
```

**Response:**
```json
{
  "code": 0,
  "message": "Detected 3 objects",
  "data": {
    "detections": [
      {
        "bbox": [100, 200, 300, 400],
        "class": "person",
        "confidence": 0.95,
        "class_id": 0
      }
    ]
  },
  "timestamp": 1710211200
}
```

### 3. OCR Text Recognition

Extract text from an image using EasyOCR.

**Endpoint:** `POST /api/v1/vision/ocr`

**Parameters:**
- `image`: Image file (required)
- `language`: Language codes, comma-separated (optional, default "ch_sim,en")

**Supported Languages:**
- `ch_sim`: Simplified Chinese
- `ch_tra`: Traditional Chinese
- `en`: English
- `ja`: Japanese
- `ko`: Korean

**Request:**
```bash
curl -X POST "http://localhost:8000/api/v1/vision/ocr" \
  -F "image=@document.jpg" \
  -F "language=ch_sim,en"
```

**Response:**
```json
{
  "code": 0,
  "message": "OCR completed, found 5 text regions",
  "data": {
    "text": "识别的完整文字内容",
    "confidence": 0.92,
    "boxes": [
      {
        "text": "第一行文字",
        "confidence": 0.95,
        "bbox": [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]
      }
    ]
  },
  "timestamp": 1710211200
}
```

## Health Check

**Endpoint:** `GET /health`

**Response:**
```json
{
  "code": 0,
  "message": "healthy",
  "data": {"status": "up"},
  "timestamp": 1710211200
}
```

## Error Codes

| Code | Description |
|------|-------------|
| 0 | Success |
| 1000 | Parameter error |
| 1001 | Authentication failed |
| 1002 | Permission denied |
| 2000 | Resource not found |
| 3000 | Server internal error |
| 3001 | Image processing error |
| 3002 | Model load error |
| 4000 | Third-party service error |
