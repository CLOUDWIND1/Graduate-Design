"""
活动数据模型
文件名：app/models/activity.py
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, DECIMAL, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Activity(Base):
    """活动模型"""
    __tablename__ = "activities"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False)
    description = Column(Text)
    type = Column(String(50))
    incentive_type = Column(String(50))
    incentive_amount = Column(DECIMAL(10, 2), default=0)
    target_cluster = Column(String(50))
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    status = Column(String(20), default="draft")
    view_count = Column(Integer, default=0)
    participate_count = Column(Integer, default=0)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # 关系
    recommendations = relationship("Recommendation", backref="activity", cascade="all, delete-orphan")
    rewards = relationship("Reward", backref="activity", cascade="all, delete-orphan")

    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "type": self.type,
            "incentive_type": self.incentive_type,
            "incentive_amount": float(self.incentive_amount) if self.incentive_amount else 0,
            "target_cluster": self.target_cluster,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "status": self.status,
            "view_count": self.view_count,
            "participate_count": self.participate_count,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
