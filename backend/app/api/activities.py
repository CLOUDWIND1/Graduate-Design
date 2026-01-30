"""活动API路由"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from decimal import Decimal
from datetime import datetime

from app.database import get_db
from app.api.deps import get_current_user, get_current_admin
from app.models import Activity, User, Reward
from app.schemas.activity import ActivityCreate, ActivityUpdate, ActivityResponse, ActivityListResponse
from app.utils.logger import logger

router = APIRouter()



@router.get("/", response_model=ActivityListResponse)
def list_activities(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    name: Optional[str] = None,
    status: Optional[str] = None,
    type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """获取活动列表"""
    query = db.query(Activity)
    
    # 按名称关键字模糊查询
    if name:
        query = query.filter(Activity.title.like(f"%{name}%"))
    
    if status:
        query = query.filter(Activity.status == status)
    
    if type:
        query = query.filter(Activity.type == type)
    
    total = query.count()
    activities = query.order_by(Activity.id.asc())\
        .offset((page - 1) * page_size)\
        .limit(page_size)\
        .all()
    
    logger.info(f"Listing activities: page={page}, size={page_size}, total={total}")
    logger.info(f"Listing activities: page={page}, size={page_size}, total={total}")
    return ActivityListResponse(
        items=activities,
        total=total,
        page=page,
        page_size=page_size
    )


@router.post("/", response_model=ActivityResponse)
def create_activity(
    activity: ActivityCreate,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """创建活动（管理员）"""
    new_activity = Activity(
        title=activity.title,
        description=activity.description,
        type=activity.type,
        incentive_type=activity.incentive_type,
        incentive_amount=activity.incentive_amount,
        target_cluster=activity.target_cluster,
        start_time=activity.start_time,
        end_time=activity.end_time,
        status="draft",
        created_by=current_user.id
    )
    db.add(new_activity)
    db.commit()
    db.refresh(new_activity)
    logger.info(f"Admin {current_user.username} created activity: {new_activity.id} - {new_activity.title}")
    return new_activity


@router.get("/{activity_id}", response_model=ActivityResponse)
def get_activity(activity_id: int, db: Session = Depends(get_db)):
    """获取活动详情"""
    activity = db.query(Activity).filter(Activity.id == activity_id).first()
    if not activity:
        raise HTTPException(status_code=404, detail="活动不存在")
    return activity


@router.put("/{activity_id}", response_model=ActivityResponse)
def update_activity(
    activity_id: int,
    updates: ActivityUpdate,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """更新活动（管理员）"""
    activity = db.query(Activity).filter(Activity.id == activity_id).first()
    if not activity:
        raise HTTPException(status_code=404, detail="活动不存在")
    
    update_data = updates.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(activity, key, value)
    
    db.commit()
    db.refresh(activity)
    logger.info(f"Admin {current_user.username} updated activity: {activity.id}")
    return activity


@router.delete("/{activity_id}")
def delete_activity(
    activity_id: int,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """删除活动（管理员）"""
    activity = db.query(Activity).filter(Activity.id == activity_id).first()
    if not activity:
        raise HTTPException(status_code=404, detail="活动不存在")
    
    db.delete(activity)
    db.commit()
    logger.info(f"Admin {current_user.username} deleted activity: {activity_id}")
    return {"message": "活动已删除"}


class StatusUpdate(BaseModel):
    status: str


@router.patch("/{activity_id}/status/", response_model=ActivityResponse)
@router.patch("/{activity_id}/status", response_model=ActivityResponse)
def update_activity_status(
    activity_id: int,
    payload: StatusUpdate,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """更新活动状态（管理员）"""
    activity = db.query(Activity).filter(Activity.id == activity_id).first()
    if not activity:
        raise HTTPException(status_code=404, detail="活动不存在")
    
    # 验证状态值（需与数据库 ENUM 一致）
    valid_statuses = ["draft", "active", "paused", "ended"]
    if payload.status not in valid_statuses:
        raise HTTPException(
            status_code=400, 
            detail=f"无效状态，有效值: {', '.join(valid_statuses)}"
        )
    
    activity.status = payload.status
    db.commit()
    db.refresh(activity)
    logger.info(f"Admin {current_user.username} updated status of activity {activity.id} to {payload.status}")
    return activity


@router.post("/{activity_id}/participate/")
@router.post("/{activity_id}/participate")
def participate_activity(
    activity_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """参与活动并获得奖励"""
    activity = db.query(Activity).filter(Activity.id == activity_id).first()
    if not activity:
        raise HTTPException(status_code=404, detail="活动不存在")
    
    # 检查是否已参与
    existing_reward = db.query(Reward).filter(
        Reward.user_id == current_user.id,
        Reward.activity_id == activity_id
    ).first()
    
    if existing_reward:
        raise HTTPException(status_code=400, detail="您已参与过该活动")
    
    # 创建奖励
    reward = Reward(
        user_id=current_user.id,
        activity_id=activity_id,
        reward_type=activity.incentive_type or "points",
        amount=activity.incentive_amount or 0,
        status="completed"
    )
    db.add(reward)
    
    # 更新活动参与数
    activity.participate_count = (activity.participate_count or 0) + 1
    
    db.commit()
    
    logger.info(f"User {current_user.id} participated in activity {activity_id}, reward: {reward.id}")
    return {
        "message": "参与成功",
        "reward": reward.to_dict()
    }

