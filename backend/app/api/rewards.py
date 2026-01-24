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
from app.utils.logger import logger

router = APIRouter(prefix="/rewards", tags=["rewards"])


@router.get("/")
@router.get("")
async def get_rewards(
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
    
    # 获取活动名称
    result = []
    for reward in rewards:
        activity = db.query(Activity).filter(Activity.id == reward.activity_id).first()
        result.append({
            "id": reward.id,
            "reward_type": reward.reward_type,
            "amount": float(reward.amount) if reward.amount else 0,
            "status": reward.status,
            "activity_name": activity.title if activity else "未知活动",
            "created_at": reward.created_at.isoformat() if reward.created_at else None
        })
    
    return {
        "items": result,
        "total": total,
        "page": page,
        "page_size": page_size
    }


@router.get("/summary/")
@router.get("/summary")
async def get_rewards_summary(
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
    
    return {
        "totalAmount": float(total_amount),
        "totalPoints": int(total_points),
        "pendingCount": pending_count
    }


@router.post("/{reward_id}/claim/")
@router.post("/{reward_id}/claim")
async def claim_reward(
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
