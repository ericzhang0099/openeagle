# VisionClaw Vision Service

## Project Structure

```
vision_service/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application entry
│   ├── api/
│   │   ├── __init__.py
│   │   └── vision.py        # API routes
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py        # Configuration
│   │   └── exceptions.py    # Custom exceptions
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py       # Pydantic models
│   ├── services/
│   │   ├── __init__.py
│   │   ├── object_detector.py   # YOLO detection
│   │   ├── ocr_service.py       # EasyOCR
│   │   └── image_analyzer.py    # Image analysis
│   └── utils/
│       ├── __init__.py
│       ├── logger.py        # Logging
│       └── image_utils.py   # Image utilities
├── tests/                   # Test files
├── models/                  # AI model files
├── logs/                    # Log files
├── temp/                    # Temporary files
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── Makefile
├── setup.py
├── setup.sh
├── API.md
└── README.md
```

## Quick Start

```bash
# Setup
./setup.sh

# Run
make run

# Test
make test

# Docker
make docker-build
make docker-run
```
