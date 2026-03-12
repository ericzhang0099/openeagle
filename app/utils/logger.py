"""
Logger Utility

Centralized logging configuration using loguru.
"""

import sys
from pathlib import Path
from loguru import logger

# Ensure logs directory exists
Path("logs").mkdir(parents=True, exist_ok=True)

# Remove default handler
logger.remove()

# Add console handler with custom format
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
           "<level>{level: <8}</level> | "
           "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
           "<level>{message}</level>",
    level="INFO",
    colorize=True,
)

# Add file handler for errors
logger.add(
    "logs/vision_service_{time}.log",
    rotation="500 MB",
    retention="10 days",
    compression="zip",
    level="ERROR",
    encoding="utf-8",
)

__all__ = ["logger"]
