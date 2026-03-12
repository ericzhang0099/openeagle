"""
Chat API
"""
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.redis import redis_client
from app.models.session import Session, Message, SessionStatus, MessageRole, MessageType
from app.schemas.session import ChatRequest, ChatResponse

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db)
):
    """单轮对话"""
    message_id = str(uuid4())
    
    # 构建上下文
    context = request.context or {}
    
    # 调用LLM（这里先用简单实现）
    response_text = await call_llm(request.message, context)
    
    return ChatResponse(
        response=response_text,
        message_id=message_id,
        metadata={}
    )


@router.get("/chat/stream")
async def chat_stream(message: str):
    """流式对话"""
    async def generate():
        # 流式生成响应
        response = await call_llm_stream(message)
        for chunk in response:
            yield f"data: {chunk}\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream"
    )


async def call_llm(message: str, context: dict) -> str:
    """
    调用LLM
    这里需要接入实际的LLM API
    """
    # TODO: 实现实际的LLM调用
    # 可以使用OpenAI、DeepSeek、Claude等
    
    # 模拟响应
    return f"收到消息: {message}\n\n这是一个模拟响应。在实际部署时请配置LLM API。"


async def call_llm_stream(message: str):
    """流式调用LLM"""
    # TODO: 实现实际的流式LLM调用
    response = f"收到消息: {message}\n\n"
    for char in response:
        yield char
        import asyncio
        await asyncio.sleep(0.01)
