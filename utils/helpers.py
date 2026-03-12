"""
VisionClaw Audio Service - 工具函数模块

提供通用的工具函数和异常处理
"""

import base64
import io
import os
import tempfile
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

import structlog

logger = structlog.get_logger()


# ==================== 异常类 ====================

class AudioServiceError(Exception):
    """
    音频服务基础异常类
    
    Attributes:
        message: 错误消息
        code: 错误代码
        status_code: HTTP状态码
        details: 详细错误信息
    """
    
    def __init__(
        self,
        message: str,
        code: str = "INTERNAL_ERROR",
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class ValidationError(AudioServiceError):
    """请求参数验证错误"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code="VALIDATION_ERROR",
            status_code=400,
            details=details
        )


class FileTooLargeError(AudioServiceError):
    """文件过大错误"""
    
    def __init__(self, file_size: int, max_size: int):
        super().__init__(
            message=f"文件大小({file_size / 1024 / 1024:.2f}MB)超过限制({max_size / 1024 / 1024:.2f}MB)",
            code="FILE_TOO_LARGE",
            status_code=413,
            details={"file_size": file_size, "max_size": max_size}
        )


class UnsupportedFormatError(AudioServiceError):
    """不支持的文件格式错误"""
    
    def __init__(self, format: str, supported_formats: list):
        super().__init__(
            message=f"不支持的音频格式: {format}",
            code="UNSUPPORTED_FORMAT",
            status_code=415,
            details={"format": format, "supported_formats": supported_formats}
        )


class ASRError(AudioServiceError):
    """语音识别错误"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code="ASR_ERROR",
            status_code=500,
            details=details
        )


class TTSError(AudioServiceError):
    """语音合成错误"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code="TTS_ERROR",
            status_code=500,
            details=details
        )


# ==================== 工具函数 ====================

def generate_request_id() -> str:
    """
    生成请求追踪ID
    
    Returns:
        唯一的请求ID字符串
    """
    return f"req_{uuid.uuid4().hex[:16]}"


def get_timestamp() -> str:
    """
    获取当前时间戳(ISO格式)
    
    Returns:
        ISO格式的时间字符串
    """
    return datetime.utcnow().isoformat() + "Z"


def validate_audio_format(filename: str, allowed_formats: list) -> Tuple[str, str]:
    """
    验证音频文件格式
    
    Args:
        filename: 文件名
        allowed_formats: 允许的格式列表
        
    Returns:
        (格式, 扩展名) 元组
        
    Raises:
        UnsupportedFormatError: 格式不支持时抛出
    """
    ext = Path(filename).suffix.lower().lstrip(".")
    
    if ext not in allowed_formats:
        raise UnsupportedFormatError(ext, allowed_formats)
    
    return ext, f".{ext}"


def validate_file_size(file_size: int, max_size: int) -> None:
    """
    验证文件大小
    
    Args:
        file_size: 文件大小(字节)
        max_size: 最大允许大小(字节)
        
    Raises:
        FileTooLargeError: 文件过大时抛出
    """
    if file_size > max_size:
        raise FileTooLargeError(file_size, max_size)


def audio_to_base64(audio_data: bytes, mime_type: str = "audio/wav") -> str:
    """
    将音频数据转换为Base64字符串
    
    Args:
        audio_data: 音频字节数据
        mime_type: MIME类型
        
    Returns:
        Base64编码的字符串(包含data URI)
    """
    base64_str = base64.b64encode(audio_data).decode("utf-8")
    return f"data:{mime_type};base64,{base64_str}"


def base64_to_audio(base64_str: str) -> bytes:
    """
    将Base64字符串转换为音频数据
    
    Args:
        base64_str: Base64编码的字符串
        
    Returns:
        音频字节数据
    """
    # 移除data URI前缀
    if "," in base64_str:
        base64_str = base64_str.split(",")[1]
    
    return base64.b64decode(base64_str)


def save_upload_file(upload_file: bytes, suffix: str = ".wav") -> Path:
    """
    保存上传的文件到临时目录
    
    Args:
        upload_file: 上传的文件字节
        suffix: 文件后缀
        
    Returns:
        保存的文件路径
    """
    temp_dir = Path(tempfile.gettempdir()) / "visionclaw_audio"
    temp_dir.mkdir(parents=True, exist_ok=True)
    
    file_path = temp_dir / f"{uuid.uuid4().hex}{suffix}"
    file_path.write_bytes(upload_file)
    
    logger.debug("file_saved", path=str(file_path), size=len(upload_file))
    
    return file_path


def cleanup_temp_file(file_path: Path) -> None:
    """
    清理临时文件
    
    Args:
        file_path: 文件路径
    """
    try:
        if file_path.exists():
            file_path.unlink()
            logger.debug("file_cleaned", path=str(file_path))
    except Exception as e:
        logger.warning("cleanup_failed", path=str(file_path), error=str(e))


def get_audio_duration(audio_data: bytes, sample_rate: int = 22050) -> float:
    """
    估算音频时长
    
    Args:
        audio_data: 音频字节数据
        sample_rate: 采样率
        
    Returns:
        估算的时长(秒)
    """
    # 简化的时长估算 (假设16bit单声道)
    bytes_per_sample = 2
    channels = 1
    num_samples = len(audio_data) / (bytes_per_sample * channels)
    return num_samples / sample_rate


def format_error_response(
    error: Exception,
    request_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    格式化错误响应
    
    Args:
        error: 异常对象
        request_id: 请求ID
        
    Returns:
        格式化的错误响应字典
    """
    if isinstance(error, AudioServiceError):
        return {
            "status": "error",
            "code": error.status_code,
            "message": error.message,
            "data": {
                "error_code": error.code,
                "details": error.details
            },
            "request_id": request_id or generate_request_id()
        }
    else:
        return {
            "status": "error",
            "code": 500,
            "message": str(error) or "Internal Server Error",
            "data": None,
            "request_id": request_id or generate_request_id()
        }


def log_request(
    method: str,
    path: str,
    request_id: str,
    **kwargs
) -> None:
    """
    记录请求日志
    
    Args:
        method: HTTP方法
        path: 请求路径
        request_id: 请求ID
        **kwargs: 额外日志字段
    """
    logger.info(
        "request_received",
        method=method,
        path=path,
        request_id=request_id,
        **kwargs
    )


def log_response(
    request_id: str,
    status_code: int,
    duration_ms: float,
    **kwargs
) -> None:
    """
    记录响应日志
    
    Args:
        request_id: 请求ID
        status_code: HTTP状态码
        duration_ms: 处理时长(毫秒)
        **kwargs: 额外日志字段
    """
    logger.info(
        "request_completed",
        request_id=request_id,
        status_code=status_code,
        duration_ms=round(duration_ms, 2),
        **kwargs
    )
