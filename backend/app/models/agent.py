"""
数据库模型 - Agent
"""
from sqlalchemy import Column, String, DateTime, JSON, Text, Boolean
from sqlalchemy.sql import func

from app.core.database import Base


class Agent(Base):
    """Agent模型"""
    __tablename__ = "agents"
    
    id = Column(String(36), primary_key=True)
    name = Column(String(100), nullable=False)
    type = Column(String(50), default="default")
    description = Column(Text, nullable=True)
    config = Column(JSON, default={})
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<Agent {self.id} {self.name}>"
