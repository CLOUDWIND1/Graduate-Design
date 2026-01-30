"""
奖励API路由
文件名：app/api/rewards.py
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import datetime

from app.database import get_db
from app.api.deps import get_current_user
from app.models import User, Reward, Activity
from app.schemas.reward import RewardResponse, RewardListResponse, RewardSummaryResponse
from app.utils.logger import logger

router = APIRouter(prefix="/rewards", tags=["rewards"])



@router.get("/", response_model=RewardListResponse)
@router.get("", response_model=RewardListResponse)
def get_rewards(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    reward_type: Optional[str] = None,
    status: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取当前用户的奖励列表"""
    query = db.query(Reward).filter(Reward.user_id == current_user.id)
    
    if reward_type:
        query = query.filter(Reward.reward_type == reward_type)
    if status:
        query = query.filter(Reward.status == status)
    
    total = query.count()
    rewards = query.order_by(Reward.created_at.desc())\
        .offset((page - 1) * page_size)\
        .limit(page_size)\
        .all()
    
    # 手动填充 activity_name 字段，因为 Pydantic ORM mode 默认不会从 relationship 自动获取非直接关联字段
    # 或者可以在 Model 中定义一个 @property，但这里我们在 API 层处理
    # 手动填充 activity_name 字段
    # 注意：更优雅的方式是在 Schema 中配置 ORM 关联，或者在 Service 层处理
    # 这里为了保持 API 层逻辑简单，我们在转换前处理
    # 手动填充 activity_name 字段
    # 利用 SQLAlchemy 的 backref="activity" 获取关联的活动信息
    for reward in rewards:
        # 直接赋值，避免读取不存在的 activity_name 属性导致 AttributeError
        # 这里的 reward.activity 是通过 Activity 模型中的 relationship backref 自动生成的
        if getattr(reward, "activity", None):
             reward.activity_name = reward.activity.title
        else:
             # 如果 backref 还没生效，尝试手动查询 (为了兼容性)
             activity = db.query(Activity).filter(Activity.id == reward.activity_id).first()
             reward.activity_name = activity.title if activity else "未知活动"
    
    return RewardListResponse(
        items=rewards, # Pydantic v2 mode='from_attributes' handle ORM objects
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/summary/", response_model=RewardSummaryResponse)
@router.get("/summary", response_model=RewardSummaryResponse)
def get_rewards_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取奖励汇总"""
    # 红包和优惠券总金额
    total_amount = db.query(func.sum(Reward.amount)).filter(
        Reward.user_id == current_user.id,
        Reward.reward_type.in_(["red_packet", "coupon"]),
        Reward.status == "completed"
    ).scalar() or 0
    
    # 积分总数
    total_points = db.query(func.sum(Reward.amount)).filter(
        Reward.user_id == current_user.id,
        Reward.reward_type == "points",
        Reward.status == "completed"
    ).scalar() or 0
    
    # 待领取数量
    pending_count = db.query(Reward).filter(
        Reward.user_id == current_user.id,
        Reward.status == "pending"
    ).count()
    
    return RewardSummaryResponse(
        totalAmount=float(total_amount),
        totalPoints=int(total_points),
        pendingCount=pending_count
    )


@router.post("/{reward_id}/claim/")
@router.post("/{reward_id}/claim")
def claim_reward(
    reward_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """领取奖励"""
    reward = db.query(Reward).filter(
        Reward.id == reward_id,
        Reward.user_id == current_user.id
    ).first()
    
    if not reward:
        raise HTTPException(status_code=404, detail="奖励不存在")
    
    if reward.status != "pending":
        raise HTTPException(status_code=400, detail="奖励状态不可领取")
    
    reward.status = "completed"
    db.commit()
    
    logger.info(f"用户 {current_user.id} 领取奖励 {reward_id}")
    
    return {"message": "领取成功"}

