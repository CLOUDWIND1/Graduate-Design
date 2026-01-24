"""推荐数据模型"""
from sqlalchemy import Column, BigInteger, Integer, DECIMAL, Text, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class Recommendation(Base):
    """推荐记录表模型"""
    __tablename__ = "recommendations"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    activity_id = Column(Integer, ForeignKey("activities.id"), nullable=False)
    score = Column(DECIMAL(5, 4))
    reason = Column(Text)
    features = Column(JSON)
    is_clicked = Column(Integer, default=0)
    is_accepted = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 关系
    user = relationship("User", back_populates="recommendations")
