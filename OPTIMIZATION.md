# VisionClaw Audio Service - 优化建议清单

## 高优先级 (必须修复)

### 1.1 添加限流保护
```python
# api/audio.py 添加
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

class RateLimitMiddleware(BaseHTTPMiddleware):
    """简单限流中间件"""
    async def dispatch(self, request: Request, call_next):
        # TODO: 实现Redis-based限流
        return await call_next(request)
```

### 1.2 添加请求ID追踪
```python
# core/logging.py
import uuid
import logging

class RequestIdFilter(logging.Filter):
    def filter(self, record):
        record.request_id = getattr(record, 'request_id', str(uuid.uuid4())[:8])
        return True
```

### 1.3 添加健康检查详情
```python
# main.py 健康检查增强
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "audio",
        "version": "0.1.0",
        "stt_status": "available" if WHISPER_AVAILABLE else "mock",
        "tts_status": "available" if PIPER_AVAILABLE else "mock",
        "timestamp": int(time.time())
    }
```

## 中优先级 (建议修复)

### 2.1 音频格式转换
```python
# utils/audio_converter.py
import ffmpeg

def convert_to_wav(input_path: str, output_path: str) -> bool:
    """将任意音频格式转换为WAV"""
    try:
        ffmpeg.input(input_path).output(
            output_path,
            ar=16000,  # 采样率
            ac=1,      # 单声道
            acodec='pcm_s16le'
        ).run(quiet=True)
        return True
    except Exception as e:
        print(f"[AudioConverter] Error: {e}")
        return False
```

### 2.2 添加音频缓存
```python
# services/cache.py
import hashlib
from pathlib import Path

class AudioCache:
    """TTS结果缓存"""
    def __init__(self, cache_dir: str = "./cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
    
    def get_cache_key(self, text: str, voice: str, speed: float) -> str:
        """生成缓存键"""
        content = f"{text}:{voice}:{speed}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def get(self, key: str) -> Optional[bytes]:
        """获取缓存"""
        cache_file = self.cache_dir / f"{key}.wav"
        if cache_file.exists():
            return cache_file.read_bytes()
        return None
    
    def set(self, key: str, data: bytes):
        """设置缓存"""
        cache_file = self.cache_dir / f"{key}.wav"
        cache_file.write_bytes(data)
```

### 2.3 添加指标监控
```python
# core/metrics.py
import time
from collections import defaultdict

class MetricsCollector:
    """指标收集器"""
    def __init__(self):
        self.request_count = defaultdict(int)
        self.request_duration = defaultdict(list)
    
    def record_request(self, endpoint: str, duration: float):
        self.request_count[endpoint] += 1
        self.request_duration[endpoint].append(duration)
    
    def get_stats(self) -> dict:
        return {
            endpoint: {
                "count": count,
                "avg_duration": sum(durations) / len(durations) if durations else 0
            }
            for endpoint, count in self.request_count.items()
            for durations in [self.request_duration[endpoint]]
        }
```

## 低优先级 (可选)

### 3.1 添加WebSocket支持
```python
# api/websocket.py
from fastapi import WebSocket

@router.websocket("/ws/audio")
async def audio_websocket(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            message = await websocket.receive_json()
            # 处理实时音频流
            if message["type"] == "stt":
                result = await stt_service.recognize_stream(message["audio"])
                await websocket.send_json(result)
    except Exception as e:
        await websocket.close()
```

### 3.2 添加批量处理
```python
# api/batch.py
@router.post("/batch/tts")
async def batch_tts(requests: List[TTSRequest]):
    """批量语音合成"""
    results = []
    for req in requests:
        audio = await tts_service.synthesize(req.text, req.voice, req.speed)
        results.append({
            "text": req.text,
            "audio": base64.b64encode(audio).decode()
        })
    return {"results": results}
```

### 3.3 添加语音活动检测(VAD)
```python
# services/vad.py
import webrtcvad

class VADService:
    """语音活动检测"""
    def __init__(self, aggressiveness: int = 3):
        self.vad = webrtcvad.Vad(aggressiveness)
    
    def is_speech(self, audio_frame: bytes, sample_rate: int = 16000) -> bool:
        return self.vad.is_speech(audio_frame, sample_rate)
```

## 代码质量评分

| 维度 | 得分 | 说明 |
|------|------|------|
| 可读性 | 9/10 | 文档完整，命名规范 |
| 健壮性 | 8/10 | 错误处理完善，缺少限流 |
| 性能 | 7/10 | 延迟加载，缺少缓存 |
| 安全性 | 8/10 | 输入验证，错误隐藏 |
| 可维护性 | 8/10 | 模块化，接口清晰 |
| **总分** | **40/50** | **良好** |

## 推荐修复顺序

1. **立即修复**: 限流保护、健康检查增强
2. **本周修复**: 音频格式转换、TTS缓存
3. **下周修复**: 指标监控、WebSocket支持
4. **后续优化**: 批量处理、VAD检测

---
*审计时间: 2026-03-12 11:58*
*审计人: Vera*
