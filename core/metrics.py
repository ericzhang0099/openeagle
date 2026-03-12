"""
指标监控模块
收集和报告服务性能指标
"""

import time
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class RequestMetrics:
    """请求指标数据"""
    endpoint: str
    duration: float
    timestamp: float
    success: bool


class MetricsCollector:
    """
    指标收集器
    
    收集API请求的性能指标
    """
    
    def __init__(self, max_history: int = 1000):
        """
        初始化收集器
        
        Args:
            max_history: 最大历史记录数
        """
        self.max_history = max_history
        self.requests: List[RequestMetrics] = []
        self.endpoint_stats: Dict[str, Dict] = defaultdict(lambda: {
            "count": 0,
            "success_count": 0,
            "error_count": 0,
            "total_duration": 0.0,
            "min_duration": float('inf'),
            "max_duration": 0.0
        })
    
    def record_request(self, endpoint: str, duration: float, success: bool = True):
        """
        记录请求指标
        
        Args:
            endpoint: 端点路径
            duration: 请求处理时间（秒）
            success: 是否成功
        """
        metrics = RequestMetrics(
            endpoint=endpoint,
            duration=duration,
            timestamp=time.time(),
            success=success
        )
        
        self.requests.append(metrics)
        
        # 限制历史记录数量
        if len(self.requests) > self.max_history:
            self.requests = self.requests[-self.max_history:]
        
        # 更新端点统计
        stats = self.endpoint_stats[endpoint]
        stats["count"] += 1
        stats["total_duration"] += duration
        stats["min_duration"] = min(stats["min_duration"], duration)
        stats["max_duration"] = max(stats["max_duration"], duration)
        
        if success:
            stats["success_count"] += 1
        else:
            stats["error_count"] += 1
    
    def get_summary(self) -> Dict:
        """
        获取指标摘要
        
        Returns:
            指标摘要字典
        """
        if not self.requests:
            return {
                "total_requests": 0,
                "avg_duration": 0,
                "error_rate": 0,
                "endpoints": {}
            }
        
        total_duration = sum(r.duration for r in self.requests)
        error_count = sum(1 for r in self.requests if not r.success)
        
        # 计算每个端点的统计
        endpoint_summaries = {}
        for endpoint, stats in self.endpoint_stats.items():
            count = stats["count"]
            if count > 0:
                endpoint_summaries[endpoint] = {
                    "count": count,
                    "avg_duration": round(stats["total_duration"] / count, 3),
                    "min_duration": round(stats["min_duration"], 3),
                    "max_duration": round(stats["max_duration"], 3),
                    "success_rate": round(stats["success_count"] / count * 100, 1),
                    "error_rate": round(stats["error_count"] / count * 100, 1)
                }
        
        return {
            "total_requests": len(self.requests),
            "avg_duration": round(total_duration / len(self.requests), 3),
            "error_rate": round(error_count / len(self.requests) * 100, 1),
            "endpoints": endpoint_summaries
        }
    
    def get_recent_errors(self, count: int = 10) -> List[Dict]:
        """
        获取最近的错误请求
        
        Args:
            count: 返回数量
            
        Returns:
            错误请求列表
        """
        errors = [r for r in self.requests if not r.success]
        errors = sorted(errors, key=lambda x: x.timestamp, reverse=True)
        
        return [
            {
                "endpoint": r.endpoint,
                "duration": round(r.duration, 3),
                "timestamp": int(r.timestamp)
            }
            for r in errors[:count]
        ]
    
    def reset(self):
        """重置所有指标"""
        self.requests.clear()
        self.endpoint_stats.clear()


# 全局指标收集器实例
metrics_collector = MetricsCollector()
