"""
API Schemas - Session和Message
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime


class MessageCreate(BaseModel):
    """创建消息请求"""
    content: str = Field(..., description="消息内容")
    type: str = Field(default="text", description="消息类型")
    metadata: Dict[str, Any] = Field(default_factory=dict)


class MessageResponse(BaseModel):
    """消息响应"""
    id: str
    session_id: str
    role: str
    type: str
    content: str
    metadata: Dict[str, Any]
    created_at: datetime
    
    class Config:
        from_attributes = True


class SessionCreate(BaseModel):
    """创建会话请求"""
    agent_id: str = Field(..., description="Agent ID")
    user_id: Optional[str] = Field(None, description="用户ID")
    metadata: Dict[str, Any] = Field(default_factory=dict)


class SessionResponse(BaseModel):
    """会话响应"""
    id: str
    agent_id: str
    user_id: Optional[str]
    status: str
    metadata: Dict[str, Any]
    created_at: datetime
    ended_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class ChatRequest(BaseModel):
    """聊天请求"""
    message: str = Field(..., description="用户消息")
    context: Dict[str, Any] = Field(default_factory=dict)


class ChatResponse(BaseModel):
    """聊天响应"""
    response: str
    message_id: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
