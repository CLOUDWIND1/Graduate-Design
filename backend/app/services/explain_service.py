"""解释服务"""
from sqlalchemy.orm import Session
from typing import Dict
from app.ml.predict import get_model
from app.ml.explainer import SHAPExplainer


class ExplainService:
    """推荐解释业务逻辑"""
    
    def __init__(self):
        self.model = get_model()
        self.explainer = SHAPExplainer()
        try:
            if self.model.model is not None:
                self.explainer.fit(self.model.model)
        except Exception:
            pass
    
    def explain_recommendation(self, db: Session, recommendation_id: int):
        """解释推荐理由"""
        return {"explanation": ""}
    
    def get_feature_importance(self, db: Session, recommendation_id: int):
        """获取特征重要性"""
        return {"features": {}}
    
    def get_explanation(self, db: Session, user_id: int, activity_id: int) -> Dict:
        """获取推荐解释详情"""
        from app.models import UserProfile, Activity
        from app.utils.logger import logger
        import numpy as np
        
        profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
        activity = db.query(Activity).filter(Activity.id == activity_id).first()
        
        if not profile or not activity:
            return {
                "score": 0.5,
                "explanation": "数据不足，无法生成详细解释",
                "feature_importance": [],
                "force_plot_data": {}
            }
        
        # 构建特征向量
        incentive_type_map = {"red_packet": 0, "points": 1, "coupon": 2}
        activity_type_map = {"invite": 0, "quiz": 1, "share": 2}
        
        features = np.array([[
            float(profile.factor_social or 0.5),
            float(profile.factor_psych or 0.5),
            float(profile.factor_incent or 0.5),
            float(profile.factor_tech or 0.5),
            float(profile.factor_env or 0.5),
            float(profile.factor_personal or 0.5),
            float(activity.incentive_amount or 0),
            incentive_type_map.get(activity.incentive_type, 0),
            activity_type_map.get(activity.type, 0)
        ]])
        
        score = self.model.predict_proba_single(features)
        
        # 生成详细解释文本
        explanation_text = self._generate_detailed_explanation(profile, activity, score)
        
        # 获取特征重要性
        feature_importance = self._get_formatted_feature_importance(profile)
        
        logger.info(f"为用户 {user_id} 生成活动 {activity_id} 的解释")
        
        return {
            "score": float(score),
            "explanation": explanation_text,
            "feature_importance": feature_importance,
            "force_plot_data": {}
        }
    
    def _generate_detailed_explanation(self, profile, activity, score: float) -> str:
        """生成详细的推荐解释文本"""
        explanations = []
        
        # 基于分数的总体评价
        if score > 0.7:
            explanations.append(f"根据您的用户画像分析，系统预测您有 {score*100:.1f}% 的概率接受此活动。")
        elif score > 0.5:
            explanations.append(f"基于您的偏好特征，此活动与您有 {score*100:.1f}% 的匹配度。")
        else:
            explanations.append(f"此活动与您的匹配度为 {score*100:.1f}%，您可以根据实际情况决定是否参与。")
        
        # 基于用户因子的解释
        factors = {
            'social': (profile.factor_social, '社交影响'),
            'psych': (profile.factor_psych, '心理激励'),
            'incent': (profile.factor_incent, '物质激励'),
            'tech': (profile.factor_tech, '技术接受'),
            'env': (profile.factor_env, '环境因素'),
            'personal': (profile.factor_personal, '个人偏好')
        }
        
        # 找出最高的因子
        sorted_factors = sorted(factors.items(), key=lambda x: x[1][0], reverse=True)
        top_factor = sorted_factors[0]
        
        if top_factor[1][0] > 0.6:
            explanations.append(f"您的「{top_factor[1][1]}」敏感度较高（{top_factor[1][0]*100:.0f}%），")
        
        # 基于活动特征的解释
        if activity.incentive_type == 'red_packet':
            if profile.factor_incent > 0.5:
                explanations.append("此活动提供红包奖励，符合您对物质激励的偏好。")
            else:
                explanations.append("此活动提供红包奖励。")
        elif activity.incentive_type == 'points':
            explanations.append("此活动提供积分奖励，可用于后续兑换。")
        elif activity.incentive_type == 'coupon':
            explanations.append("此活动提供优惠券奖励。")
        
        if activity.type == 'invite' and profile.factor_social > 0.5:
            explanations.append("作为社交活跃用户，邀请类活动非常适合您。")
        elif activity.type == 'share' and profile.factor_personal > 0.5:
            explanations.append("分享活动契合您的个性化表达特质。")
        elif activity.type == 'quiz' and profile.factor_tech > 0.5:
            explanations.append("答题活动符合您对技术和知识的兴趣。")
        
        return ''.join(explanations) if explanations else "根据您的综合画像，为您推荐此活动。"
    
    def _get_formatted_feature_importance(self, profile) -> list:
        """获取格式化的特征重要性列表"""
        features = [
            {"feature": "factor_social", "label": "社会因素", "importance": float(profile.factor_social or 0.5)},
            {"feature": "factor_psych", "label": "心理因素", "importance": float(profile.factor_psych or 0.5)},
            {"feature": "factor_incent", "label": "激励因素", "importance": float(profile.factor_incent or 0.5)},
            {"feature": "factor_tech", "label": "技术因素", "importance": float(profile.factor_tech or 0.5)},
            {"feature": "factor_env", "label": "环境因素", "importance": float(profile.factor_env or 0.5)},
            {"feature": "factor_personal", "label": "个人因素", "importance": float(profile.factor_personal or 0.5)},
        ]
        # 按重要性排序
        features.sort(key=lambda x: x["importance"], reverse=True)
        return features
    
    def get_global_feature_importance(self, db: Session) -> Dict:
        """获取全局特征重要性"""
        feature_importance = self.model.get_feature_importance()
        return {"features": feature_importance}


explain_service = ExplainService()
