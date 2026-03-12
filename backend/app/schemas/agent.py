"""
API Schemas - Agent
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime


class AgentCreate(BaseModel):
    """创建Agent请求"""
    name: str = Field(..., description="Agent名称")
    type: str = Field(default="default", description="Agent类型")
    description: Optional[str] = Field(None, description="Agent描述")
    config: Dict[str, Any] = Field(default_factory=dict, description="Agent配置")


class AgentUpdate(BaseModel):
    """更新Agent请求"""
    name: Optional[str] = None
    description: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class AgentResponse(BaseModel):
    """Agent响应"""
    id: str
    name: str
    type: str
    description: Optional[str]
    config: Dict[str, Any]
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
