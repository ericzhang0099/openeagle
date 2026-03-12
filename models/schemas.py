"""
VisionClaw Audio Service - 数据模型模块

定义API请求和响应的数据模型
"""

from enum import Enum
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field, field_validator


class ResponseStatus(str, Enum):
    """响应状态枚举"""
    SUCCESS = "success"
    ERROR = "error"
    PARTIAL = "partial"


class AudioFormat(str, Enum):
    """支持的音频格式枚举"""
    WAV = "wav"
    MP3 = "mp3"
    M4A = "m4a"
    OGG = "ogg"
    FLAC = "flac"
    WEBM = "webm"


class LanguageCode(str, Enum):
    """支持的语言代码枚举"""
    ZH = "zh"  # 中文
    EN = "en"  # 英文
    JA = "ja"  # 日文
    KO = "ko"  # 韩文
    FR = "fr"  # 法文
    DE = "de"  # 德文
    ES = "es"  # 西班牙文
    AUTO = "auto"  # 自动检测


# ==================== 基础响应模型 ====================

class BaseResponse(BaseModel):
    """
    基础响应模型
    
    所有API响应的基类，提供统一的响应格式
    
    Attributes:
        status: 响应状态 (success/error/partial)
        code: 业务状态码
        message: 响应消息
        data: 响应数据
        request_id: 请求追踪ID
    """
    status: ResponseStatus = Field(default=ResponseStatus.SUCCESS, description="响应状态")
    code: int = Field(default=200, description="业务状态码")
    message: str = Field(default="OK", description="响应消息")
    data: Optional[Dict[str, Any]] = Field(default=None, description="响应数据")
    request_id: Optional[str] = Field(default=None, description="请求追踪ID")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "code": 200,
                "message": "操作成功",
                "data": {},
                "request_id": "req_1234567890"
            }
        }


class ErrorResponse(BaseResponse):
    """
    错误响应模型
    
    用于返回错误信息的响应
    """
    status: ResponseStatus = ResponseStatus.ERROR
    code: int = 500
    message: str = "Internal Server Error"
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "error",
                "code": 500,
                "message": "服务器内部错误",
                "data": None,
                "request_id": "req_1234567890"
            }
        }


# ==================== ASR/STT 模型 ====================

class ASRRequest(BaseModel):
    """
    语音识别请求模型
    
    Attributes:
        language: 音频语言 (默认自动检测)
        task: 任务类型 (transcribe/translate)
        prompt: 提示文本，帮助模型识别特定词汇
    """
    language: LanguageCode = Field(
        default=LanguageCode.AUTO,
        description="音频语言，auto表示自动检测"
    )
    task: str = Field(
        default="transcribe",
        description="任务类型: transcribe(转录) 或 translate(翻译)"
    )
    prompt: Optional[str] = Field(
        default=None,
        description="提示文本，帮助识别特定词汇"
    )


class ASRResponseData(BaseModel):
    """
    语音识别响应数据
    
    Attributes:
        text: 识别出的文本
        language: 检测到的语言
        duration: 音频时长(秒)
        confidence: 置信度分数
        segments: 分段识别结果
    """
    text: str = Field(description="识别出的文本")
    language: str = Field(description="检测到的语言")
    duration: float = Field(description="音频时长(秒)")
    confidence: Optional[float] = Field(default=None, description="置信度分数(0-1)")
    segments: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        description="分段识别结果"
    )


class ASRResponse(BaseResponse):
    """语音识别响应模型"""
    data: Optional[ASRResponseData] = None


# ==================== TTS 模型 ====================

class TTSRequest(BaseModel):
    """
    语音合成请求模型
    
    Attributes:
        text: 要合成的文本
        voice: 声音ID
        speed: 语速 (0.5-2.0, 1.0为正常)
        pitch: 音调 (-10到10, 0为正常)
        volume: 音量 (0.0-1.0)
        format: 输出音频格式
    """
    text: str = Field(
        ...,
        min_length=1,
        max_length=5000,
        description="要合成的文本(1-5000字符)"
    )
    voice: str = Field(
        default="default",
        description="声音ID"
    )
    speed: float = Field(
        default=1.0,
        ge=0.5,
        le=2.0,
        description="语速 (0.5-2.0)"
    )
    pitch: float = Field(
        default=0.0,
        ge=-10.0,
        le=10.0,
        description="音调 (-10到10)"
    )
    volume: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="音量 (0.0-1.0)"
    )
    format: AudioFormat = Field(
        default=AudioFormat.WAV,
        description="输出音频格式"
    )


class TTSResponseData(BaseModel):
    """
    语音合成响应数据
    
    Attributes:
        audio_url: 音频文件URL
        audio_base64: Base64编码的音频数据
        duration: 音频时长(秒)
        sample_rate: 采样率
        format: 音频格式
        text_length: 文本长度
    """
    audio_url: Optional[str] = Field(default=None, description="音频文件URL")
    audio_base64: str = Field(description="Base64编码的音频数据")
    duration: float = Field(description="音频时长(秒)")
    sample_rate: int = Field(description="采样率")
    format: str = Field(description="音频格式")
    text_length: int = Field(description="文本长度")


class TTSResponse(BaseResponse):
    """语音合成响应模型"""
    data: Optional[TTSResponseData] = None


# ==================== 健康检查模型 ====================

class HealthStatus(str, Enum):
    """健康状态枚举"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


class ServiceHealth(BaseModel):
    """
    服务健康状态
    
    Attributes:
        name: 服务名称
        status: 健康状态
        latency_ms: 响应延迟(毫秒)
        message: 状态消息
    """
    name: str = Field(description="服务名称")
    status: HealthStatus = Field(description="健康状态")
    latency_ms: Optional[float] = Field(default=None, description="响应延迟(毫秒)")
    message: Optional[str] = Field(default=None, description="状态消息")


class HealthCheckData(BaseModel):
    """
    健康检查数据
    
    Attributes:
        status: 整体健康状态
        version: 服务版本
        timestamp: 检查时间戳
        services: 各服务健康状态
    """
    status: HealthStatus = Field(description="整体健康状态")
    version: str = Field(description="服务版本")
    timestamp: str = Field(description="检查时间戳(ISO格式)")
    services: List[ServiceHealth] = Field(description="各服务健康状态")


class HealthCheckResponse(BaseResponse):
    """健康检查响应模型"""
    data: Optional[HealthCheckData] = None


# ==================== 批量处理模型 ====================

class BatchASRRequest(BaseModel):
    """批量语音识别请求"""
    files: List[str] = Field(description="文件ID列表")
    language: LanguageCode = Field(default=LanguageCode.AUTO)


class BatchTTSRequest(BaseModel):
    """批量语音合成请求"""
    texts: List[str] = Field(
        ...,
        min_length=1,
        max_length=10,
        description="文本列表(最多10条)"
    )
    voice: str = Field(default="default")
    speed: float = Field(default=1.0, ge=0.5, le=2.0)


class BatchTaskStatus(BaseModel):
    """批量任务状态"""
    task_id: str = Field(description="任务ID")
    status: str = Field(description="任务状态")
    progress: int = Field(ge=0, le=100, description="进度百分比")
    results: Optional[List[Dict[str, Any]]] = Field(default=None)
    error: Optional[str] = Field(default=None)
