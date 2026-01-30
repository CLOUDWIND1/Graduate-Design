"""
奖励相关Pydantic模式
文件名：app/schemas/reward.py
"""

from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from decimal import Decimal


class RewardBase(BaseModel):
    """奖励基础模式"""
    reward_type: str
    amount: Decimal = 0.0
    status: str
    activity_id: int


class RewardCreate(RewardBase):
    """奖励创建模式"""
    user_id: int


class RewardResponse(RewardBase):
    """奖励响应模式"""
    id: int
    user_id: int
    created_at: datetime
    activity_name: Optional[str] = None
    
    model_config = {"from_attributes": True}


class RewardListResponse(BaseModel):
    """奖励列表响应模式"""
    total: int
    items: List[RewardResponse]
    page: int
    page_size: int

class RewardSummaryResponse(BaseModel):
    """奖励汇总响应模式"""
    totalAmount: float
    totalPoints: int
    pendingCount: int
