"""
用户数据模型
文件名：app/models/user.py
"""

from sqlalchemy import Column, Integer, String, DateTime, Enum, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum


class UserRole(str, enum.Enum):
    """用户角色"""
    USER = "user"
    ADMIN = "admin"


class UserStatus(int, enum.Enum):
    """用户状态"""
    ACTIVE = 1
    INACTIVE = 0


class User(Base):
    """用户模型"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=False)
    email = Column(String(100))
    phone = Column(String(20))
    role = Column(Enum(UserRole), default=UserRole.USER)
    status = Column(Integer, default=1)  # 1=active, 0=inactive
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # 关系
    profile = relationship("UserProfile", back_populates="user", uselist=False)
    rewards = relationship("Reward", back_populates="user")
    recommendations = relationship("Recommendation", back_populates="user")