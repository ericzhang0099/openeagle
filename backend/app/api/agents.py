"""
Agent API
"""
from typing import List
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.models.agent import Agent
from app.schemas.agent import AgentCreate, AgentUpdate, AgentResponse

router = APIRouter()


@router.post("/agents", response_model=AgentResponse)
async def create_agent(
    agent_data: AgentCreate,
    db: AsyncSession = Depends(get_db)
):
    """创建Agent"""
    agent = Agent(
        id=str(uuid4()),
        name=agent_data.name,
        type=agent_data.type,
        description=agent_data.description,
        config=agent_data.config,
    )
    db.add(agent)
    await db.commit()
    await db.refresh(agent)
    return agent


@router.get("/agents", response_model=List[AgentResponse])
async def list_agents(
    skip: int = 0,
    limit: int = 20,
    db: AsyncSession = Depends(get_db)
):
    """获取Agent列表"""
    result = await db.execute(
        select(Agent).offset(skip).limit(limit)
    )
    agents = result.scalars().all()
    return agents


@router.get("/agents/{agent_id}", response_model=AgentResponse)
async def get_agent(
    agent_id: str,
    db: AsyncSession = Depends(get_db)
):
    """获取Agent详情"""
    result = await db.execute(
        select(Agent).where(Agent.id == agent_id)
    )
    agent = result.scalar_one_or_none()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent


@router.put("/agents/{agent_id}", response_model=AgentResponse)
async def update_agent(
    agent_id: str,
    agent_data: AgentUpdate,
    db: AsyncSession = Depends(get_db)
):
    """更新Agent"""
    result = await db.execute(
        select(Agent).where(Agent.id == agent_id)
    )
    agent = result.scalar_one_or_none()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    update_data = agent_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(agent, field, value)
    
    await db.commit()
    await db.refresh(agent)
    return agent


@router.delete("/agents/{agent_id}")
async def delete_agent(
    agent_id: str,
    db: AsyncSession = Depends(get_db)
):
    """删除Agent"""
    result = await db.execute(
        select(Agent).where(Agent.id == agent_id)
    )
    agent = result.scalar_one_or_none()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    await db.delete(agent)
    await db.commit()
    return {"message": "Agent deleted"}
