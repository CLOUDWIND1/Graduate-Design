"""
推荐服务
文件名：app/services/recommendation_service.py
"""

import numpy as np
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from datetime import datetime, timedelta
from functools import lru_cache
import hashlib
import time
import random

from app.models import Activity, Recommendation, UserProfile
from app.ml.predict import get_model
from app.ml.explainer import SHAPExplainer
from app.utils.logger import logger


# 简单内存缓存
_recommendation_cache: Dict[str, tuple] = {}
CACHE_TTL = 60  # 缓存60秒


def clear_recommendation_cache(user_id: int = None):
    """清除推荐缓存"""
    global _recommendation_cache
    if user_id:
        keys_to_remove = [k for k in _recommendation_cache if k.startswith(f"rec_{user_id}_")]
        for k in keys_to_remove:
            del _recommendation_cache[k]
    else:
        _recommendation_cache.clear()


class RecommendationService:
    """推荐服务类"""
    
    def __init__(self):
        # 使用全局模型实例（已加载预训练模型）
        self.model = get_model()
        self.explainer = SHAPExplainer()
        # 尝试拟合解释器
        try:
            if self.model.model is not None:
                self.explainer.fit(self.model.model)
                logger.info("✅ 推荐服务已使用预训练模型初始化")
        except Exception as e:
            logger.warning(f"SHAP解释器初始化失败: {e}")
    
    def get_recommendations(
        self, 
        db: Session, 
        user_id: int, 
        limit: int = 10,
        refresh: bool = False
    ) -> List[Dict]:
        """获取个性化推荐列表"""
        
        # 检查缓存 (如果不是刷新操作)
        cache_key = f"rec_{user_id}_{limit}"
        if not refresh and cache_key in _recommendation_cache:
            cached_data, cached_time = _recommendation_cache[cache_key]
            if time.time() - cached_time < CACHE_TTL:
                logger.info(f"用户 {user_id} 使用缓存推荐")
                return cached_data
        
        # 获取用户画像
        profile = db.query(UserProfile).filter(
            UserProfile.user_id == user_id
        ).first()
        
        if not profile:
            # 冷启动：返回热门活动
            logger.info(f"用户 {user_id} 无画像，使用冷启动推荐")
            return self._get_popular_activities(db, limit)
        
        # 获取候选活动（活跃状态）
        activities = db.query(Activity).filter(
            Activity.status == "active"
        ).all()
        
        if not activities:
            # 如果没有活跃活动，尝试获取所有活动
            activities = db.query(Activity).all()
        
        if not activities:
            logger.info("没有可推荐的活动")
            return self._get_popular_activities(db, limit)
        
        # 构建特征向量
        user_features = self._build_user_features(profile)
        
        # 对每个活动计算接受概率
        recommendations = []
        for activity in activities:
            # 构建活动特征
            activity_features = self._build_activity_features(activity)
            
            # 合并特征
            features = {**user_features, **activity_features}
            feature_vector = self._features_to_vector(features)
            
            # 预测接受概率
            probability = self.model.predict_proba_single(feature_vector)
            
            # 使用快速规则生成推荐理由（SHAP解释在详情页按需生成）
            reason = self._quick_reason(activity, profile, probability)
            
            recommendations.append({
                "activity_id": activity.id,
                "title": activity.title,
                "description": activity.description,
                "incentive_type": activity.incentive_type,
                "incentive_amount": float(activity.incentive_amount or 0),
                "score": float(probability),
                "reason": reason,
                "start_time": getattr(activity, 'start_time', None),
                "end_time": getattr(activity, 'end_time', None)
            })
        
        # 按分数排序
        recommendations.sort(key=lambda x: x["score"], reverse=True)
        
        # 如果是刷新，增加随机性：从Top N中随机选择
        if refresh and len(recommendations) > limit:
            # 取Top 2*limit个候选
            candidates = recommendations[:min(len(recommendations), limit * 3)]
            # 随机打乱
            random.shuffle(candidates)
            result = candidates[:limit]
            # 重新按分数排序以便展示
            result.sort(key=lambda x: x["score"], reverse=True)
        else:
            result = recommendations[:limit]
        
        # 缓存结果
        _recommendation_cache[cache_key] = (result, time.time())
        
        logger.info(f"为用户 {user_id} 生成 {len(result)} 条推荐 (Refresh={refresh})")
        return result
    
    def _quick_reason(self, activity: Activity, profile: UserProfile, probability: float) -> str:
        """快速生成推荐理由（不使用SHAP，提升性能）"""
        reasons = []
        
        # 基于激励类型匹配（降低阈值）
        if activity.incentive_type == 'red_packet':
            if profile.factor_incent > 0.5:
                reasons.append('红包奖励符合您的激励偏好')
            else:
                reasons.append('丰厚红包等您领取')
        elif activity.incentive_type == 'points':
            if profile.factor_psych > 0.5:
                reasons.append('积分奖励适合您的消费习惯')
            else:
                reasons.append('轻松获取积分奖励')
        elif activity.incentive_type == 'coupon':
            reasons.append('专属优惠券等您领取')
        
        # 基于活动类型匹配
        if activity.type == 'invite':
            if profile.factor_social > 0.5:
                reasons.append('邀请活动契合您的社交特质')
            else:
                reasons.append('邀请好友一起参与')
        elif activity.type == 'share':
            if profile.factor_personal > 0.5:
                reasons.append('分享活动适合您的个性')
            else:
                reasons.append('分享即可获得奖励')
        elif activity.type == 'quiz':
            if profile.factor_tech > 0.5:
                reasons.append('答题活动符合您的技术兴趣')
            else:
                reasons.append('趣味答题赢奖励')
        
        # 基于概率评分补充理由
        if not reasons:
            if probability > 0.7:
                reasons.append('系统预测您会非常喜欢')
            elif probability > 0.5:
                reasons.append('可能符合您的兴趣')
            else:
                reasons.append('为您精选推荐')
        
        return '；'.join(reasons[:2]) if reasons else '为您精选推荐'
    
    def _generate_reason(self, feature_vector: np.ndarray, probability: float) -> str:
        """生成详细推荐理由（使用SHAP，用于详情页）"""
        try:
            reason = self.explainer.explain_prediction(
                feature_vector, 
                self.model.feature_names
            )
            return reason
        except Exception as e:
            logger.warning(f"生成推荐理由失败: {e}")
            if probability > 0.7:
                return "根据您的偏好，强烈推荐此活动"
            elif probability > 0.5:
                return "此活动可能符合您的兴趣"
            else:
                return "为您推荐此活动"
    
    def _build_user_features(self, profile: UserProfile) -> Dict[str, float]:
        """构建用户特征"""
        return {
            "factor_social": float(profile.factor_social or 0.5),
            "factor_psych": float(profile.factor_psych or 0.5),
            "factor_incent": float(profile.factor_incent or 0.5),
            "factor_tech": float(profile.factor_tech or 0.5),
            "factor_env": float(profile.factor_env or 0.5),
            "factor_personal": float(profile.factor_personal or 0.5),
        }
    
    def _build_activity_features(self, activity: Activity) -> Dict[str, float]:
        """构建活动特征"""
        return {
            "incentive_amount": float(activity.incentive_amount or 0),
            "incentive_type_encoded": self._encode_incentive_type(activity.incentive_type),
            "activity_type_encoded": self._encode_activity_type(activity.type),
        }
    
    def _features_to_vector(self, features: Dict[str, float]) -> np.ndarray:
        """特征字典转为向量"""
        # 按照模型训练时的特征顺序
        feature_order = [
            "factor_social", "factor_psych", "factor_incent", 
            "factor_tech", "factor_env", "factor_personal",
            "incentive_amount", "incentive_type_encoded", "activity_type_encoded"
        ]
        return np.array([[features.get(f, 0) for f in feature_order]])
    
    def _encode_incentive_type(self, incentive_type: str) -> int:
        """编码激励类型"""
        type_mapping = {"red_packet": 0, "points": 1, "coupon": 2}
        return type_mapping.get(incentive_type, 0)
    
    def _encode_activity_type(self, activity_type: str) -> int:
        """编码活动类型"""
        type_mapping = {"invite": 0, "quiz": 1, "share": 2}
        return type_mapping.get(activity_type, 0)
    
    def _get_popular_activities(self, db: Session, limit: int) -> List[Dict]:
        """获取热门活动（冷启动）"""
        # 先尝试获取活跃活动
        activities = db.query(Activity).filter(
            Activity.status == "active"
        ).limit(limit).all()
        
        # 如果没有，获取所有活动
        if not activities:
            activities = db.query(Activity).limit(limit).all()
        
        return [{
            "activity_id": a.id,
            "title": a.title,
            "description": a.description,
            "activity_type": getattr(a, 'type', None),
            "incentive_type": getattr(a, 'incentive_type', None),
            "incentive_amount": float(a.incentive_amount or 0),
            "score": 0.5,  # 默认分数
            "reason": "热门活动推荐"
        } for a in activities]
    
    def _save_recommendation_log(
        self, 
        db: Session, 
        user_id: int, 
        recommendations: List[Dict]
    ):
        """保存推荐记录"""
        for rec in recommendations:
            log = Recommendation(
                user_id=user_id,
                activity_id=rec["activity_id"],
                score=rec["score"],
                reason=rec["reason"]
            )
            db.add(log)
        
        try:
            db.commit()
        except Exception as e:
            logger.error(f"保存推荐记录失败: {e}")
            db.rollback()
    
    def record_feedback(
        self, 
        db: Session, 
        user_id: int, 
        activity_id: int, 
        is_clicked: bool, 
        is_accepted: bool
    ):
        """记录用户反馈"""
        # 查找最近的推荐记录
        log = db.query(Recommendation).filter(
            Recommendation.user_id == user_id,
            Recommendation.activity_id == activity_id
        ).order_by(desc(Recommendation.created_at)).first()
        
        if log:
            log.is_clicked = 1 if is_clicked else 0
            log.is_accepted = 1 if is_accepted else 0
            db.commit()
            logger.info(f"更新推荐反馈: user={user_id}, activity={activity_id}")
        else:
            # 创建新的反馈记录
            new_log = Recommendation(
                user_id=user_id,
                activity_id=activity_id,
                score=0.5,
                reason="用户直接反馈",
                is_clicked=1 if is_clicked else 0,
                is_accepted=1 if is_accepted else 0
            )
            db.add(new_log)
            db.commit()
            logger.info(f"创建新反馈记录: user={user_id}, activity={activity_id}")
        
        # 触发用户画像更新
        from app.services.profile_service import profile_service
        profile_service.update_profile_from_feedback(
            db, user_id, activity_id, is_accepted
        )
    
    def get_recommendation_stats(self, db: Session, user_id: int = None) -> Dict:
        """获取推荐统计数据"""
        query = db.query(Recommendation)
        
        if user_id:
            query = query.filter(Recommendation.user_id == user_id)
        
        total = query.count()
        clicked = query.filter(Recommendation.is_clicked == 1).count()
        accepted = query.filter(Recommendation.is_accepted == 1).count()
        
        return {
            "total_recommendations": total,
            "click_rate": clicked / total if total > 0 else 0,
            "accept_rate": accepted / total if total > 0 else 0,
            "clicked_count": clicked,
            "accepted_count": accepted
        }


recommendation_service = RecommendationService()
