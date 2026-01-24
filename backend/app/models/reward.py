"""
奖励数据模型
文件名：app/models/reward.py
"""

from sqlalchemy import Column, Integer, String, DECIMAL, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum


class RewardStatus(str, enum.Enum):
    """奖励状态"""
    PENDING = "pending"
    COMPLETED = "completed"
    EXPIRED = "expired"


class RewardType(str, enum.Enum):
    """奖励类型"""
    RED_PACKET = "red_packet"
    POINTS = "points"
    COUPON = "coupon"


class Reward(Base):
    """奖励模型"""
    __tablename__ = "rewards"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    activity_id = Column(Integer, ForeignKey("activities.id"), nullable=False)
    
    reward_type = Column(String(50), default=RewardType.POINTS.value)
    amount = Column(DECIMAL(10, 2), default=0)
    status = Column(String(20), default=RewardStatus.PENDING.value)
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # 关系
    user = relationship("User", back_populates="rewards")
    
    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "activity_id": self.activity_id,
            "reward_type": self.reward_type,
            "amount": float(self.amount) if self.amount else 0,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
