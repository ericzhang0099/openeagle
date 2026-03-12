"""
Health Check API
"""
from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "ok",
        "service": "VisionClaw API"
    }


@router.get("/")
async def root():
    """根路径"""
    return {
        "name": "VisionClaw API",
        "version": "1.0.0"
    }
