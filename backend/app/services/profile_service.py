"""用户画像服务"""
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
from app.models import UserProfile, Activity
from app.utils.logger import logger


class ProfileService:
    """用户画像业务逻辑"""
    
    @staticmethod
    def calculate_user_profile(db: Session, user_id: int, questionnaire_data: Dict[str, Any]) -> UserProfile:
        """
        根据问卷数据计算用户画像
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            questionnaire_data: 问卷数据
            
        Returns:
            UserProfile 对象
        """
        profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
        
        if not profile:
            profile = UserProfile(user_id=user_id)
            db.add(profile)
        
        # 问卷数据映射到因子（假设问卷有以下问题）
        # social: 社交影响相关问题
        # psych: 心理激励相关问题
        # incent: 物质激励相关问题
        # tech: 技术接受度相关问题
        # env: 环境因素相关问题
        # personal: 个人偏好相关问题
        
        if 'social' in questionnaire_data:
            profile.factor_social = min(max(float(questionnaire_data['social']) / 5, 0), 1)
        if 'psych' in questionnaire_data:
            profile.factor_psych = min(max(float(questionnaire_data['psych']) / 5, 0), 1)
        if 'incent' in questionnaire_data:
            profile.factor_incent = min(max(float(questionnaire_data['incent']) / 5, 0), 1)
        if 'tech' in questionnaire_data:
            profile.factor_tech = min(max(float(questionnaire_data['tech']) / 5, 0), 1)
        if 'env' in questionnaire_data:
            profile.factor_env = min(max(float(questionnaire_data['env']) / 5, 0), 1)
        if 'personal' in questionnaire_data:
            profile.factor_personal = min(max(float(questionnaire_data['personal']) / 5, 0), 1)
        
        # 直接传入因子值（0-1范围）
        if 'factor_social' in questionnaire_data:
            profile.factor_social = float(questionnaire_data['factor_social'])
        if 'factor_psych' in questionnaire_data:
            profile.factor_psych = float(questionnaire_data['factor_psych'])
        if 'factor_incent' in questionnaire_data:
            profile.factor_incent = float(questionnaire_data['factor_incent'])
        if 'factor_tech' in questionnaire_data:
            profile.factor_tech = float(questionnaire_data['factor_tech'])
        if 'factor_env' in questionnaire_data:
            profile.factor_env = float(questionnaire_data['factor_env'])
        if 'factor_personal' in questionnaire_data:
            profile.factor_personal = float(questionnaire_data['factor_personal'])
        
        profile.questionnaire_completed = 1
        
        db.commit()
        db.refresh(profile)
        
        # 分配聚类
        ProfileService.assign_cluster(db, user_id)
        
        logger.info(f"用户 {user_id} 画像计算完成")
        return profile
    
    @staticmethod
    def update_user_profile(db: Session, user_id: int, factors: Dict[str, float]) -> Optional[UserProfile]:
        """
        更新用户画像因子
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            factors: 因子字典
            
        Returns:
            更新后的 UserProfile 对象
        """
        profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
        
        if not profile:
            logger.warning(f"用户 {user_id} 画像不存在")
            return None
        
        # 更新因子
        if 'factor_social' in factors:
            profile.factor_social = float(factors['factor_social'])
        if 'factor_psych' in factors:
            profile.factor_psych = float(factors['factor_psych'])
        if 'factor_incent' in factors:
            profile.factor_incent = float(factors['factor_incent'])
        if 'factor_tech' in factors:
            profile.factor_tech = float(factors['factor_tech'])
        if 'factor_env' in factors:
            profile.factor_env = float(factors['factor_env'])
        if 'factor_personal' in factors:
            profile.factor_personal = float(factors['factor_personal'])
        
        db.commit()
        db.refresh(profile)
        
        # 重新分配聚类
        ProfileService.assign_cluster(db, user_id)
        
        logger.info(f"用户 {user_id} 画像更新完成")
        return profile
    
    @staticmethod
    def assign_cluster(db: Session, user_id: int):
        """基于用户画像分配聚类"""
        profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
        if not profile:
            return None
        
        # Simple rule-based clustering (can be replaced with ML model)
        # Calculate dominant factor
        factors = {
            'social': float(profile.factor_social or 0),
            'psych': float(profile.factor_psych or 0),
            'incent': float(profile.factor_incent or 0),
            'tech': float(profile.factor_tech or 0),
            'env': float(profile.factor_env or 0),
            'personal': float(profile.factor_personal or 0),
        }
        
        dominant_factor = max(factors, key=factors.get)
        
        # 10类聚类映射（基于因子组合）
        cluster_mapping = {
            'social': (0, '社交活跃型'),
            'psych': (7, '积极响应型'),
            'incent': (3, '高价值型'),
            'tech': (4, '互动参与型'),
            'env': (2, '观望保守型'),
            'personal': (1, '品牌忠诚型'),
        }
        
        # 根据次要因子进一步细分
        sorted_factors = sorted(factors.items(), key=lambda x: x[1], reverse=True)
        cluster_id, cluster_tag = cluster_mapping.get(dominant_factor, (0, '社交活跃型'))
        
        if len(sorted_factors) >= 2:
            factor_value = sorted_factors[0][1]
            
            # 高价值用户特征
            if factor_value > 0.7 and factors.get('incent', 0) > 0.6:
                cluster_id, cluster_tag = 3, '高价值型'
            # 深度粘性用户
            elif factors.get('social', 0) > 0.6 and factors.get('personal', 0) > 0.6:
                cluster_id, cluster_tag = 9, '深度粘性型'
            # 稳定忠实用户
            elif factors.get('psych', 0) > 0.5 and factors.get('env', 0) > 0.5:
                cluster_id, cluster_tag = 6, '稳定忠实型'
            # 低频使用者
            elif factor_value < 0.4:
                cluster_id, cluster_tag = 5, '低频使用型'
            # 潜在流失用户
            elif factors.get('env', 0) < 0.3 and factors.get('psych', 0) < 0.4:
                cluster_id, cluster_tag = 8, '潜在流失型'
        
        profile.cluster_id = cluster_id
        profile.cluster_tag = cluster_tag
        db.commit()
        
        logger.info(f"用户 {user_id} 分配到聚类 {cluster_id}: {cluster_tag}")
        return cluster_tag
    
    @staticmethod
    def update_profile_from_feedback(db: Session, user_id: int, activity_id: int, is_accepted: bool):
        """
        根据用户反馈增量更新画像
        
        当用户接受某个活动时，根据活动类型适当增加相关因子
        当用户拒绝某个活动时，适当降低相关因子
        """
        from app.models import Activity
        
        profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
        if not profile:
            return
        
        activity = db.query(Activity).filter(Activity.id == activity_id).first()
        if not activity:
            return
        
        # 增量更新系数
        delta = 0.05 if is_accepted else -0.02
        
        # 根据激励类型更新因子
        incentive_type = activity.incentive_type
        if incentive_type == "red_packet":
            profile.factor_incent = min(max(profile.factor_incent + delta, 0), 1)
        elif incentive_type == "points":
            profile.factor_psych = min(max(profile.factor_psych + delta, 0), 1)
        elif incentive_type == "coupon":
            profile.factor_incent = min(max(profile.factor_incent + delta * 0.5, 0), 1)
            profile.factor_psych = min(max(profile.factor_psych + delta * 0.5, 0), 1)
        
        # 根据活动类型更新因子
        activity_type = activity.type
        if activity_type == "invite":
            profile.factor_social = min(max(profile.factor_social + delta, 0), 1)
        elif activity_type == "quiz":
            profile.factor_tech = min(max(profile.factor_tech + delta, 0), 1)
        elif activity_type == "share":
            profile.factor_social = min(max(profile.factor_social + delta * 0.5, 0), 1)
            profile.factor_personal = min(max(profile.factor_personal + delta * 0.5, 0), 1)
        
        try:
            db.commit()
            logger.info(f"用户 {user_id} 画像根据反馈更新完成")
        except Exception as e:
            logger.error(f"更新用户画像失败: {e}")
            db.rollback()


profile_service = ProfileService()
