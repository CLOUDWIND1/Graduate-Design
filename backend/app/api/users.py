"""用户API路由"""
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional, List
from sqlalchemy.orm import Session
from app.database import get_db
from app.api.deps import get_current_user
from app.models import User, UserProfile
from app.services.profile_service import profile_service
from app.utils.logger import logger
from app.schemas.profile import UserPreferences, UserProfileUpdate

router = APIRouter()


# Removed UserProfileUpdate class definition here as it is imported from schemas


class QuestionnaireSubmit(BaseModel):
    """问卷提交数据"""
    answers: List[int]  # 20个答案，每个1-5


@router.post("/questionnaire/")
@router.post("/questionnaire")
async def submit_questionnaire(
    payload: QuestionnaireSubmit,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    提交问卷数据
    
    问卷共20题，按顺序对应6个因子：
    - social: 3题 (索引 0-2)
    - psych: 4题 (索引 3-6)
    - incent: 3题 (索引 7-9)
    - tech: 3题 (索引 10-12)
    - env: 3题 (索引 13-15)
    - personal: 4题 (索引 16-19)
    """
    answers = payload.answers
    
    if len(answers) < 20:
        # 补齐不足的答案
        answers.extend([3] * (20 - len(answers)))
    
    # 计算各因子分数（平均值，归一化到0-1）
    def avg_factor(start: int, end: int) -> float:
        return sum(answers[start:end]) / ((end - start) * 5)
    
    questionnaire_data = {
        'factor_social': avg_factor(0, 3),
        'factor_psych': avg_factor(3, 7),
        'factor_incent': avg_factor(7, 10),
        'factor_tech': avg_factor(10, 13),
        'factor_env': avg_factor(13, 16),
        'factor_personal': avg_factor(16, 20)
    }
    
    logger.info(f"用户 {current_user.id} 提交问卷，计算因子: {questionnaire_data}")
    
    # 更新用户画像
    profile = profile_service.calculate_user_profile(db, current_user.id, questionnaire_data)
    
    return {
        "message": "问卷提交成功",
        "profile": profile.to_dict() if profile else None
    }


@router.get("/profile")
async def get_user_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取当前用户画像"""
    profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    if not profile:
        profile = UserProfile(user_id=current_user.id)
        db.add(profile)
        db.commit()
        db.refresh(profile)
    return profile.to_dict()


@router.get("/me")
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取当前用户信息"""
    profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    # 统一返回角色的字符串值 (user 或 admin)
    role_value = current_user.role.value if hasattr(current_user.role, 'value') else str(current_user.role)
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "phone": current_user.phone,
        "role": role_value,
        "status": current_user.status,
        "cluster_tag": profile.cluster_tag if profile else "新用户",
        "questionnaire_completed": profile.questionnaire_completed if profile else 0,
        "created_at": current_user.created_at.isoformat() if current_user.created_at else None,
        "preferences": {
            "frequency": profile.preference_frequency if profile and profile.preference_frequency else "daily",
            "activityTypes": profile.preference_activity_types.split(",") if profile and profile.preference_activity_types else [],
            "incentiveTypes": profile.preference_incentive_types.split(",") if profile and profile.preference_incentive_types else []
        }
    }


@router.put("/profile")
async def update_user_profile(
    payload: UserProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新当前用户画像"""
    profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    if not profile:
        profile = UserProfile(user_id=current_user.id)
        db.add(profile)

    data = payload.dict(exclude_unset=True)
    for key, value in data.items():
        setattr(profile, key, value)

    db.commit()
    db.refresh(profile)
    return profile.to_dict()

    db.commit()
    db.refresh(profile)
    return profile.to_dict()


@router.put("/me/preferences")
async def update_user_preferences(
    preferences: UserPreferences,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新用户偏好设置"""
    profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    if not profile:
        profile = UserProfile(user_id=current_user.id)
        db.add(profile)
    
    # Update fields
    profile.preference_frequency = preferences.frequency
    profile.preference_activity_types = ",".join(preferences.activityTypes)
    profile.preference_incentive_types = ",".join(preferences.incentiveTypes)
    
    db.commit()
    
    logger.info(f"用户 {current_user.id} 更新偏好设置")
    return {"message": "偏好设置已更新"}

@router.get("/")
async def list_users(db: Session = Depends(get_db)):
    """获取用户列表"""
    return {"message": "List users"}

@router.get("/{user_id}")
async def get_user(user_id: int, db: Session = Depends(get_db)):
    """获取用户详情"""
    return {"message": f"Get user {user_id}"}

@router.put("/{user_id}")
async def update_user(user_id: int, db: Session = Depends(get_db)):
    """更新用户信息"""
    return {"message": f"Update user {user_id}"}

@router.delete("/{user_id}")
async def delete_user(user_id: int, db: Session = Depends(get_db)):
    """删除用户"""
    return {"message": f"Delete user {user_id}"}
