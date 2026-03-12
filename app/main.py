"""
VisionClaw Vision Service - Main Application

FastAPI application for image analysis, object detection, and OCR services.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.api import vision, advanced_ai
from app.core.config import settings
from app.utils.logger import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    logger.info("Starting VisionClaw Vision Service...")
    logger.info(f"Debug mode: {settings.DEBUG}")
    logger.info(f"Model device: {settings.MODEL_DEVICE}")
    yield
    logger.info("Shutting down VisionClaw Vision Service...")


# Create FastAPI application
app = FastAPI(
    title="VisionClaw Vision Service",
    description="Image analysis, object detection, and OCR service",
    version="1.0.0",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(vision.router, prefix="/api/v1/vision", tags=["vision"])
app.include_router(advanced_ai.router, prefix="/api/v1/ai", tags=["advanced-ai"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "code": 0,
        "message": "VisionClaw Vision Service is running",
        "data": {
            "version": "1.0.0",
            "docs_url": "/docs",
        },
        "timestamp": __import__("time").time(),
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "code": 0,
        "message": "healthy",
        "data": {"status": "up"},
        "timestamp": __import__("time").time(),
    }
