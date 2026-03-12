"""
VisionClaw Backend - FastAPI Application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

from app.api import agents, sessions, chat, vision, audio, health
from app.core.config import settings
from app.core.database import engine, Base

# 创建数据库表
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="VisionClaw API",
    description="VisionClaw Backend API for Vision Intelligence Agent",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# GZIP压缩
app.add_middleware(GZipMiddleware, minimum_size=1000)

# 注册路由
app.include_router(health.router, prefix="/api/v1", tags=["Health"])
app.include_router(agents.router, prefix="/api/v1", tags=["Agents"])
app.include_router(sessions.router, prefix="/api/v1", tags=["Sessions"])
app.include_router(chat.router, prefix="/api/v1", tags=["Chat"])
app.include_router(vision.router, prefix="/api/v1", tags=["Vision"])
app.include_router(audio.router, prefix="/api/v1", tags=["Audio"])


@app.on_event("startup")
async def startup_event():
    """启动时执行"""
    # 初始化Redis连接
    from app.core.redis import redis_client
    await redis_client.ping()
    print("✅ Redis connected")


@app.on_event("shutdown")
async def shutdown_event():
    """关闭时执行"""
    from app.core.redis import redis_client
    await redis_client.close()
    print("✅ Redis disconnected")


@app.get("/")
async def root():
    """根路径"""
    return {
        "name": "VisionClaw API",
        "version": "1.0.0",
        "docs": "/docs"
    }
