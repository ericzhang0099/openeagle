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

---

## Advanced AI APIs

Base URL: `/api/v1/ai`

### 1. Multimodal Fusion

Fuse features from multiple modalities (vision, audio, text, temporal).

**Endpoint:** `POST /api/v1/ai/fusion`

**Parameters:**
- `vision_features`: List of vision feature vectors
- `audio_features`: List of audio feature vectors (optional)
- `text_features`: List of text feature vectors (optional)
- `temporal_features`: List of temporal feature vectors (optional)
- `fusion_type`: Fusion strategy - "early", "late", or "attention" (default: "attention")

**Request:**
```bash
curl -X POST "http://localhost:8000/api/v1/ai/fusion" \
  -H "Content-Type: application/json" \
  -d '{
    "vision_features": [[0.1, 0.2, ...], [0.3, 0.4, ...]],
    "audio_features": [[0.5, 0.6, ...], [0.7, 0.8, ...]],
    "fusion_type": "attention"
  }'
```

**Response:**
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "fused_features": [[0.25, 0.35, ...]],
    "fusion_type": "attention",
    "modalities_used": ["vision", "audio"]
  },
  "timestamp": 1710211200
}
```

### 2. Student State Classification

Classify student state (focused, distracted, tired, excited, confused) from multimodal data.

**Endpoint:** `POST /api/v1/ai/student-state`

**Parameters:**
- `vision_features`: Vision feature vectors (required)
- `audio_features`: Audio feature vectors (optional)
- `temporal_features`: Temporal feature vectors (required)

**Request:**
```bash
curl -X POST "http://localhost:8000/api/v1/ai/student-state" \
  -H "Content-Type: application/json" \
  -d '{
    "vision_features": [[0.1, 0.2, ...]],
    "temporal_features": [[0.9, 1.0, ...]]
  }'
```

**Response:**
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "predicted_state": "focused",
    "confidence": 0.92,
    "all_probabilities": {
      "focused": 0.92,
      "distracted": 0.05,
      "tired": 0.02,
      "excited": 0.01,
      "confused": 0.00
    }
  },
  "timestamp": 1710211200
}
```

### 3. Causal Discovery

Discover causal relationships from observational data.

**Endpoint:** `POST /api/v1/ai/causal/discover`

**Parameters:**
- `data`: Dictionary of variable names to observations
- `method`: Discovery method - "correlation" or "granger" (default: "correlation")
- `threshold`: Significance threshold (default: 0.3)

**Request:**
```bash
curl -X POST "http://localhost:8000/api/v1/ai/causal/discover" \
  -H "Content-Type: application/json" \
  -d '{
    "data": {
      "sleep_hours": [7, 8, 6, 7.5, ...],
      "mood_score": [8, 9, 6, 8.5, ...],
      "learning_efficiency": [7.5, 8.5, 6.5, 8, ...]
    },
    "method": "correlation",
    "threshold": 0.5
  }'
```

**Response:**
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "variables": ["sleep_hours", "mood_score", "learning_efficiency"],
    "edges": [
      {"source": "sleep_hours", "target": "mood_score", "strength": 0.75, "confidence": 0.95},
      {"source": "mood_score", "target": "learning_efficiency", "strength": 0.68, "confidence": 0.92}
    ],
    "method": "correlation"
  },
  "timestamp": 1710211200
}
```

### 4. Intervention Analysis

Compute the effect of an intervention using do-calculus.

**Example:** "What is the expected learning score if we ensure 8 hours of sleep?"

**Endpoint:** `POST /api/v1/ai/causal/intervention`

**Request:**
```bash
curl -X POST "http://localhost:8000/api/v1/ai/causal/intervention" \
  -H "Content-Type: application/json" \
  -d '{
    "graph_structure": {
      "variables": [{"name": "sleep_hours"}, {"name": "learning_efficiency"}],
      "edges": [{"source": "sleep_hours", "target": "learning_efficiency", "strength": 0.7}]
    },
    "data": {
      "sleep_hours": [6, 7, 8, 7.5, ...],
      "learning_efficiency": [6.5, 7.5, 8.5, 8, ...]
    },
    "treatment_var": "sleep_hours",
    "outcome_var": "learning_efficiency",
    "treatment_value": 8.0
  }'
```

**Response:**
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "expected_outcome": 8.2,
    "treatment_var": "sleep_hours",
    "treatment_value": 8.0
  },
  "timestamp": 1710211200
}
```

### 5. Counterfactual Analysis

Compute counterfactual: "What would have happened if...?"

**Example:** "What would the test score be if the child had slept 8 hours instead of 6?"

**Endpoint:** `POST /api/v1/ai/causal/counterfactual`

**Request:**
```bash
curl -X POST "http://localhost:8000/api/v1/ai/causal/counterfactual" \
  -H "Content-Type: application/json" \
  -d '{
    "graph_structure": {
      "variables": [{"name": "sleep"}, {"name": "performance"}],
      "edges": [{"source": "sleep", "target": "performance"}]
    },
    "data": {
      "sleep": [6, 7, 8, ...],
      "performance": [7, 8, 9, ...]
    },
    "observed": {"sleep": 6.0, "performance": 7.5},
    "intervention": {"sleep": 8.5},
    "target_var": "performance"
  }'
```

**Response:**
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "counterfactual_value": 9.2,
    "observed_value": 7.5,
    "difference": 1.7,
    "interpretation": "If the intervention had occurred, performance would have been 1.70 points higher."
  },
  "timestamp": 1710211200
}
```

### 6. Intervention Optimization

Find the optimal intervention to achieve a desired outcome.

**Example:** "How many hours of sleep are needed to achieve a test score of 85?"

**Endpoint:** `POST /api/v1/ai/causal/optimize`

**Request:**
```bash
curl -X POST "http://localhost:8000/api/v1/ai/causal/optimize" \
  -H "Content-Type: application/json" \
  -d '{
    "graph_structure": {
      "variables": [{"name": "study_hours"}, {"name": "test_score"}],
      "edges": [{"source": "study_hours", "target": "test_score", "strength": 0.8}]
    },
    "data": {
      "study_hours": [2, 3, 4, 5, ...],
      "test_score": [65, 72, 78, 85, ...]
    },
    "treatment_var": "study_hours",
    "outcome_var": "test_score",
    "outcome_target": 85.0,
    "treatment_range": [1.0, 6.0]
  }'
```

**Response:**
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "optimal_treatment": 5.0,
    "expected_outcome": 85.2,
    "improvement": 12.5
  },
  "timestamp": 1710211200
}
```
