"""
用户画像数据模型
文件名：app/models/profile.py
"""

from sqlalchemy import Column, Integer, Numeric, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class UserProfile(Base):
    """用户画像模型"""
    __tablename__ = "user_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    
    # 六大因子得分
    factor_social = Column(Numeric(5, 3), comment="社会因素得分")
    factor_psych = Column(Numeric(5, 3), comment="心理因素得分")
    factor_incent = Column(Numeric(5, 3), comment="激励因素得分")
    factor_tech = Column(Numeric(5, 3), comment="技术因素得分")
    factor_env = Column(Numeric(5, 3), comment="环境因素得分")
    factor_personal = Column(Numeric(5, 3), comment="个人因素得分")
    
    # 分群标签
    cluster_tag = Column(String(20), comment="分群标签：social_active/conservative")
    
    # 综合得分
    total_score = Column(Numeric(5, 3), comment="综合接受度得分")
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # 关系
    user = relationship("User", back_populates="profile")