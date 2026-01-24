"""用户聚类服务"""
from sqlalchemy.orm import Session
from sqlalchemy import func
import numpy as np
from sklearn.cluster import KMeans
from typing import List, Dict, Any
import json
import os
from app.models import UserProfile, User
from app.utils.logger import logger


# 从配置文件加载聚类标签
def _load_cluster_labels() -> Dict[int, str]:
    """从配置文件加载聚类标签"""
    config_path = os.path.join(os.path.dirname(__file__), '../../config/recommendation_config.json')
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        labels = config.get('clustering', {}).get('cluster_labels', {})
        return {int(k): v for k, v in labels.items()}
    except Exception as e:
        logger.warning(f"加载聚类配置失败: {e}，使用默认标签")
        return {
            0: "社交活跃型",
            1: "品牌忠诚型",
            2: "观望保守型",
            3: "高价值型",
            4: "互动参与型",
            5: "低频使用型",
            6: "稳定忠实型",
            7: "积极响应型",
            8: "潜在流失型",
            9: "深度粘性型"
        }


# 聚类标签映射（10类）
CLUSTER_LABELS = _load_cluster_labels()
DEFAULT_N_CLUSTERS = 10


class ClusteringService:
    """用户聚类业务逻辑"""
    
    @staticmethod
    def cluster_users(db: Session, n_clusters: int = DEFAULT_N_CLUSTERS) -> Dict[str, Any]:
        """
        执行用户聚类
        
        Args:
            db: 数据库会话
            n_clusters: 聚类数量
            
        Returns:
            聚类结果统计
        """
        try:
            # 获取所有用户画像
            profiles = db.query(UserProfile).all()
            
            if len(profiles) < n_clusters:
                logger.warning(f"用户数量({len(profiles)})少于聚类数量({n_clusters})")
                return {"message": "用户数量不足，无法执行聚类", "clusters": []}
            
            # 构建特征矩阵
            feature_matrix = np.array([
                profile.get_factors_vector() for profile in profiles
            ])
            
            # K-means 聚类
            kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
            cluster_labels = kmeans.fit_predict(feature_matrix)
            
            # 更新用户画像聚类信息
            cluster_counts = {}
            for i, profile in enumerate(profiles):
                cluster_id = int(cluster_labels[i])
                profile.cluster_id = cluster_id
                profile.cluster_tag = CLUSTER_LABELS.get(cluster_id, f"聚类{cluster_id}")
                
                # 统计
                cluster_counts[cluster_id] = cluster_counts.get(cluster_id, 0) + 1
            
            db.commit()
            
            # 返回结果
            return {
                "message": "聚类完成",
                "total_users": len(profiles),
                "n_clusters": n_clusters,
                "clusters": [
                    {
                        "cluster_id": cid,
                        "label": CLUSTER_LABELS.get(cid, f"聚类{cid}"),
                        "count": count
                    }
                    for cid, count in sorted(cluster_counts.items())
                ]
            }
            
        except Exception as e:
            logger.error(f"聚类失败: {e}")
            db.rollback()
            return {"error": str(e), "clusters": []}
    
    @staticmethod
    def get_user_cluster(db: Session, user_id: int) -> Dict[str, Any]:
        """
        获取用户所属聚类
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            
        Returns:
            用户聚类信息
        """
        profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
        
        if not profile:
            return {"cluster_id": 0, "cluster_tag": "未分类"}
        
        return {
            "cluster_id": profile.cluster_id,
            "cluster_tag": profile.cluster_tag,
            "factors": profile.get_factors_vector()
        }
    
    @staticmethod
    def get_cluster_stats(db: Session) -> List[Dict[str, Any]]:
        """
        获取聚类统计信息
        
        Returns:
            各聚类的统计数据
        """
        stats = db.query(
            UserProfile.cluster_tag,
            func.count(UserProfile.id).label("count"),
            func.avg(UserProfile.factor_social).label("avg_social"),
            func.avg(UserProfile.factor_psych).label("avg_psych"),
            func.avg(UserProfile.factor_incent).label("avg_incent"),
            func.avg(UserProfile.factor_tech).label("avg_tech"),
            func.avg(UserProfile.factor_env).label("avg_env"),
            func.avg(UserProfile.factor_personal).label("avg_personal")
        ).group_by(UserProfile.cluster_tag).all()
        
        return [
            {
                "cluster_tag": stat[0] or "未分类",
                "count": stat[1],
                "avg_factors": {
                    "social": round(float(stat[2] or 0), 2),
                    "psych": round(float(stat[3] or 0), 2),
                    "incent": round(float(stat[4] or 0), 2),
                    "tech": round(float(stat[5] or 0), 2),
                    "env": round(float(stat[6] or 0), 2),
                    "personal": round(float(stat[7] or 0), 2)
                }
            }
            for stat in stats
        ]
