"""活动数据验证schema"""
from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from decimal import Decimal


class ActivityBase(BaseModel):
    """活动基础schema"""
    title: str
    description: Optional[str] = None
    type: Optional[str] = None
    incentive_type: Optional[str] = None
    incentive_amount: Optional[Decimal] = None
    target_cluster: Optional[str] = None


class ActivityCreate(ActivityBase):
    """活动创建schema"""
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None


class ActivityUpdate(BaseModel):
    """活动更新schema"""
    title: Optional[str] = None
    description: Optional[str] = None
    type: Optional[str] = None
    incentive_type: Optional[str] = None
    incentive_amount: Optional[Decimal] = None
    target_cluster: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    status: Optional[str] = None


class ActivityResponse(ActivityBase):
    """活动响应schema"""
    id: int
    status: str
    view_count: int
    participate_count: int
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True}


class ActivityListResponse(BaseModel):
    """活动列表响应schema"""
    total: int
    items: list[ActivityResponse]
