"""
用户画像数据模型
文件名：app/models/user_profile.py
"""

from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class UserProfile(Base):
    """用户画像模型"""
    __tablename__ = "user_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    
    # 用户因子 (0-1范围)
    factor_social = Column(Float, default=0.5)      # 社会因素敏感度
    factor_psych = Column(Float, default=0.5)       # 心理激励敏感度
    factor_incent = Column(Float, default=0.5)      # 物质激励敏感度
    factor_tech = Column(Float, default=0.5)        # 技术接受度
    factor_env = Column(Float, default=0.5)         # 环境适应度
    factor_personal = Column(Float, default=0.5)    # 个人偏好度
    
    # 聚类信息
    cluster_id = Column(Integer, default=0)         # 所属聚类ID
    cluster_tag = Column(String(50), default="新用户")  # 聚类标签
    
    # 问卷状态
    questionnaire_completed = Column(Integer, default=0)  # 是否完成问卷 (0/1)
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # 关系
    user = relationship("User", back_populates="profile")
    
    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "factor_social": self.factor_social,
            "factor_psych": self.factor_psych,
            "factor_incent": self.factor_incent,
            "factor_tech": self.factor_tech,
            "factor_env": self.factor_env,
            "factor_personal": self.factor_personal,
            "cluster_id": self.cluster_id,
            "cluster_tag": self.cluster_tag,
            "questionnaire_completed": self.questionnaire_completed,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
    
    def get_factors_vector(self):
        """获取因子向量"""
        return [
            self.factor_social or 0.5,
            self.factor_psych or 0.5,
            self.factor_incent or 0.5,
            self.factor_tech or 0.5,
            self.factor_env or 0.5,
            self.factor_personal or 0.5
        ]
