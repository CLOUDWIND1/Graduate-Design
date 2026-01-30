"""用户API路由"""
from fastapi import APIRouter, Depends
from typing import Optional, List, Any
from sqlalchemy.orm import Session
from app.database import get_db
from app.api.deps import get_current_user
from app.models import User, UserProfile
from app.services.profile_service import profile_service
from app.services.recommendation_service import recommendation_service
from app.utils.logger import logger
from app.schemas.profile import UserPreferences, UserProfileUpdate, UserProfileResponse
from app.schemas.questionnaire import QuestionnaireSubmit
from app.schemas.user import UserResponse

router = APIRouter()


@router.post("/questionnaire/")
@router.post("/questionnaire")
def submit_questionnaire(
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
    
    # 使用服务层计算因子得分
    questionnaire_data = recommendation_service.calculate_factor_scores(answers)
    
    logger.info(f"用户 {current_user.id} 提交问卷，计算因子: {questionnaire_data}")
    
    # 更新用户画像
    profile = profile_service.calculate_user_profile(db, current_user.id, questionnaire_data)
    
    return {
        "message": "问卷提交成功",
        "profile": profile
    }


@router.get("/profile", response_model=UserProfileResponse)
def get_user_profile(
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
    return profile


@router.get("/me")
def get_current_user_info(
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
        "created_at": current_user.created_at,
        "preferences": {
            "frequency": profile.preference_frequency if profile and profile.preference_frequency else "daily",
            "activityTypes": profile.preference_activity_types.split(",") if profile and profile.preference_activity_types else [],
            "incentiveTypes": profile.preference_incentive_types.split(",") if profile and profile.preference_incentive_types else []
        }
    }


@router.put("/profile", response_model=UserProfileResponse)
def update_user_profile(
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
    return profile


@router.put("/me/preferences")
def update_user_preferences(
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
def list_users(db: Session = Depends(get_db)):
    """获取用户列表"""
    return {"message": "List users"}

@router.get("/{user_id}")
def get_user(user_id: int, db: Session = Depends(get_db)):
    """获取用户详情"""
    return {"message": f"Get user {user_id}"}

@router.put("/{user_id}")
def update_user(user_id: int, db: Session = Depends(get_db)):
    """更新用户信息"""
    return {"message": f"Update user {user_id}"}

@router.delete("/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    """删除用户"""
    return {"message": f"Delete user {user_id}"}

