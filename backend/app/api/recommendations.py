"""
推荐API路由
文件名：app/api/recommendations.py
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.services.recommendation_service import recommendation_service
from app.services.explain_service import explain_service
from app.services.profile_service import profile_service
from app.api.deps import get_current_user
from app.schemas import recommendation as schemas
from app.models import User


router = APIRouter()


@router.get("/", response_model=List[schemas.RecommendationResponse])
async def get_recommendations(
    limit: int = 10,
    refresh: bool = False,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取个性化推荐列表
    
    - **limit**: 返回的推荐数量（默认10）
    
    返回按接受概率排序的活动推荐列表
    """
    from app.utils.logger import logger
    
    try:
        # 使用推荐服务获取个性化推荐
        recommendations = recommendation_service.get_recommendations(
            db=db,
            user_id=current_user.id,
            limit=limit,
            refresh=refresh
        )
        logger.info(f"[API] 用户ID: {current_user.id}, 返回推荐数量: {len(recommendations)}")
        return recommendations
        
    except Exception as e:
        import traceback
        logger.error(f"获取推荐失败: {str(e)}\n{traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取推荐失败: {str(e)}"
        )


@router.post("/{activity_id}/feedback")
async def record_feedback(
    activity_id: int,
    feedback: schemas.FeedbackRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    记录用户反馈
    
    - **activity_id**: 活动ID
    - **is_clicked**: 是否点击
    - **is_accepted**: 是否接受/参与
    
    反馈会触发用户画像更新
    """
    try:
        recommendation_service.record_feedback(
            db,
            user_id=current_user.id,
            activity_id=activity_id,
            is_clicked=feedback.is_clicked,
            is_accepted=feedback.is_accepted
        )
        return {"message": "反馈记录成功"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"记录反馈失败: {str(e)}"
        )


@router.post("/{activity_id}/click")
async def record_click(
    activity_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    记录点击事件
    
    简化的反馈接口，只记录点击
    """
    try:
        recommendation_service.record_feedback(
            db,
            user_id=current_user.id,
            activity_id=activity_id,
            is_clicked=True,
            is_accepted=False
        )
        return {"message": "点击记录成功"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"记录点击失败: {str(e)}"
        )


@router.post("/{activity_id}/accept")
async def record_accept(
    activity_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    记录接受/参与事件
    
    简化的反馈接口，记录用户接受推荐
    """
    try:
        recommendation_service.record_feedback(
            db,
            user_id=current_user.id,
            activity_id=activity_id,
            is_clicked=True,
            is_accepted=True
        )
        return {"message": "接受记录成功"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"记录接受失败: {str(e)}"
        )


@router.get("/explain/{activity_id}")
async def get_recommendation_explain(
    activity_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取推荐解释详情
    
    返回为什么推荐这个活动的详细解释，包括：
    - 预测分数
    - 特征重要性
    - 自然语言解释
    - 用户画像因子
    """
    try:
        explain_data = explain_service.get_explanation(
            db,
            user_id=current_user.id,
            activity_id=activity_id
        )
        return explain_data
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取解释失败: {str(e)}"
        )


@router.get("/stats", response_model=schemas.StatisticsResponse)
async def get_recommendation_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取当前用户的推荐统计
    
    返回用户的推荐历史统计数据
    """
    try:
        stats = recommendation_service.get_recommendation_stats(db, current_user.id)
        
        # 获取特征重要性
        try:
            feature_importance = explain_service.get_global_feature_importance(db)
            top_features = feature_importance.get("features", [])[:5]
        except Exception:
            top_features = []
        
        return schemas.StatisticsResponse(
            total_recommendations=stats["total_recommendations"],
            click_rate=stats["click_rate"],
            accept_rate=stats["accept_rate"],
            top_features=top_features
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取统计失败: {str(e)}"
        )


@router.get("/history")
async def get_recommendation_history(
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取推荐历史记录
    
    返回用户的历史推荐记录
    """
    from app.models import Recommendation, Activity
    from sqlalchemy import desc
    
    try:
        records = db.query(Recommendation).filter(
            Recommendation.user_id == current_user.id
        ).order_by(desc(Recommendation.created_at)).offset(skip).limit(limit).all()
        
        result = []
        for rec in records:
            activity = db.query(Activity).filter(
                Activity.id == rec.activity_id
            ).first()
            
            result.append({
                "id": rec.id,
                "activity_id": rec.activity_id,
                "activity_title": activity.title if activity else "未知活动",
                "score": float(rec.score) if rec.score else 0,
                "reason": rec.reason,
                "is_clicked": bool(rec.is_clicked),
                "is_accepted": bool(rec.is_accepted),
                "created_at": rec.created_at.isoformat() if rec.created_at else None
            })
        
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取历史记录失败: {str(e)}"
        )
