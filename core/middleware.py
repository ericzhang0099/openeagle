"""
中间件模块 - 提供限流、请求ID追踪等功能
"""

import time
import uuid
from typing import Optional

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware


class RequestIDMiddleware(BaseHTTPMiddleware):
    """
    请求ID追踪中间件
    
    为每个请求生成唯一ID，便于日志追踪和问题排查
    """
    
    async def dispatch(self, request: Request, call_next):
        # 生成请求ID
        request_id = str(uuid.uuid4())[:8]
        request.state.request_id = request_id
        
        # 记录请求开始时间
        start_time = time.time()
        
        # 处理请求
        response = await call_next(request)
        
        # 添加请求ID到响应头
        response.headers["X-Request-ID"] = request_id
        
        # 记录处理时间
        duration = time.time() - start_time
        response.headers["X-Response-Time"] = f"{duration:.3f}s"
        
        # 记录指标
        try:
            from core.metrics import metrics_collector
            success = response.status_code < 400
            metrics_collector.record_request(
                endpoint=request.url.path,
                duration=duration,
                success=success
            )
        except Exception as e:
            print(f"[Metrics] Failed to record: {e}")
        
        # 打印请求日志
        print(f"[{request_id}] {request.method} {request.url.path} - {duration:.3f}s")
        
        return response


class SimpleRateLimitMiddleware(BaseHTTPMiddleware):
    """
    简单限流中间件
    
    基于内存的滑动窗口限流，限制每个IP的请求频率
    """
    
    def __init__(self, app, requests_per_minute: int = 60):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.request_history = {}  # IP -> [(timestamp, count)]
    
    async def dispatch(self, request: Request, call_next):
        # 获取客户端IP
        client_ip = request.client.host if request.client else "unknown"
        
        # 检查限流
        if self._is_rate_limited(client_ip):
            from fastapi.responses import JSONResponse
            return JSONResponse(
                status_code=429,
                content={
                    "code": 1003,
                    "message": "请求过于频繁，请稍后再试",
                    "data": {},
                    "timestamp": int(time.time())
                }
            )
        
        # 记录请求
        self._record_request(client_ip)
        
        # 处理请求
        return await call_next(request)
    
    def _is_rate_limited(self, client_ip: str) -> bool:
        """检查是否超过限流阈值"""
        now = time.time()
        window_start = now - 60  # 60秒窗口
        
        # 获取该IP的请求历史
        history = self.request_history.get(client_ip, [])
        
        # 清理过期记录
        history = [(ts, count) for ts, count in history if ts > window_start]
        
        # 计算总请求数
        total_requests = sum(count for _, count in history)
        
        return total_requests >= self.requests_per_minute
    
    def _record_request(self, client_ip: str):
        """记录请求"""
        now = time.time()
        
        if client_ip not in self.request_history:
            self.request_history[client_ip] = []
        
        self.request_history[client_ip].append((now, 1))
        
        # 清理过期记录（保留最近5分钟）
        cutoff = now - 300
        self.request_history[client_ip] = [
            (ts, count) for ts, count in self.request_history[client_ip]
            if ts > cutoff
        ]
