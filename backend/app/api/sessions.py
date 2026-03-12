"""
Session API
"""
from typing import List
from uuid import uuid4
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.core.database import get_db
from app.models.session import Session, Message, SessionStatus, MessageRole, MessageType
from app.schemas.session import SessionCreate, SessionResponse, MessageCreate, MessageResponse

router = APIRouter()


@router.post("/sessions", response_model=SessionResponse)
async def create_session(
    session_data: SessionCreate,
    db: AsyncSession = Depends(get_db)
):
    """创建会话"""
    session = Session(
        id=str(uuid4()),
        agent_id=session_data.agent_id,
        user_id=session_data.user_id,
        metadata=session_data.metadata,
    )
    db.add(session)
    await db.commit()
    await db.refresh(session)
    return session


@router.get("/sessions/{session_id}", response_model=SessionResponse)
async def get_session(
    session_id: str,
    db: AsyncSession = Depends(get_db)
):
    """获取会话详情"""
    result = await db.execute(
        select(Session).where(Session.id == session_id)
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session


@router.post("/sessions/{session_id}/messages", response_model=MessageResponse)
async def send_message(
    session_id: str,
    message_data: MessageCreate,
    db: AsyncSession = Depends(get_db)
):
    """发送消息"""
    # 验证session存在
    result = await db.execute(
        select(Session).where(Session.id == session_id)
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # 创建消息
    message = Message(
        id=str(uuid4()),
        session_id=session_id,
        role=MessageRole.USER,
        type=MessageType(message_data.type),
        content=message_data.content,
        metadata=message_data.metadata,
    )
    db.add(message)
    await db.commit()
    await db.refresh(message)
    return message


@router.get("/sessions/{session_id}/messages", response_model=List[MessageResponse])
async def get_messages(
    session_id: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """获取消息列表"""
    skip = (page - 1) * page_size
    result = await db.execute(
        select(Message)
        .where(Message.session_id == session_id)
        .order_by(desc(Message.created_at))
        .offset(skip)
        .limit(page_size)
    )
    messages = result.scalars().all()
    return messages


@router.delete("/sessions/{session_id}")
async def end_session(
    session_id: str,
    db: AsyncSession = Depends(get_db)
):
    """结束会话"""
    result = await db.execute(
        select(Session).where(Session.id == session_id)
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session.status = SessionStatus.ENDED
    session.ended_at = datetime.utcnow()
    await db.commit()
    return {"message": "Session ended"}
