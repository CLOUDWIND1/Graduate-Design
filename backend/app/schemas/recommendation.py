"""
推荐相关Pydantic模式
文件名：app/schemas/recommendation.py
"""

from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


class RecommendationResponse(BaseModel):
    """推荐响应模式"""
    activity_id: int
    title: str
    description: Optional[str] = None
    incentive_type: Optional[str] = None
    incentive_amount: float = 0.0
    score: float
    reason: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    
    model_config = {"from_attributes": True}


class FeedbackRequest(BaseModel):
    """反馈请求模式"""
    is_clicked: bool = False
    is_accepted: bool = False


class RecommendationDetailResponse(BaseModel):
    """推荐详情响应模式"""
    activity_id: int
    score: float
    reason: str
    feature_importance: List[dict]
    force_plot_data: dict
    
    model_config = {"from_attributes": True}


class StatisticsResponse(BaseModel):
    """统计响应模式"""
    total_recommendations: int
    click_rate: float
    accept_rate: float
    top_features: List[dict]


class RecommendationHistoryResponse(BaseModel):
    """推荐历史响应模式"""
    id: int
    activity_id: int
    activity_title: str
    score: float
    reason: Optional[str] = None
    is_clicked: bool
    is_accepted: bool
    created_at: datetime
    
    model_config = {"from_attributes": True}
