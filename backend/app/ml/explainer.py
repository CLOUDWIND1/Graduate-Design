"""
SHAP可解释性模块
文件名：app/ml/explainer.py
"""

import numpy as np
from typing import List, Dict, Tuple
import shap


class SHAPExplainer:
    """SHAP可解释性分析类"""
    
    def __init__(self):
        self.explainer = None
        self.model = None
        self.feature_names = [
            "factor_social", "factor_psych", "factor_incent", 
            "factor_tech", "factor_env", "factor_personal",
            "incentive_amount", "incentive_type_encoded", "activity_type_encoded"
        ]
        self.feature_labels = {
            "factor_social": "社会因素",
            "factor_psych": "心理因素",
            "factor_incent": "激励因素",
            "factor_tech": "技术因素",
            "factor_env": "环境因素",
            "factor_personal": "个人因素",
            "incentive_amount": "激励金额",
            "incentive_type_encoded": "激励类型",
            "activity_type_encoded": "活动类型"
        }
    
    def fit(self, model):
        """拟合解释器
        
        Args:
            model: 训练好的树模型
        """
        self.model = model
        self.explainer = shap.TreeExplainer(model)
    
    def explain_prediction(
        self, 
        X: np.ndarray, 
        feature_names: List[str] = None
    ) -> str:
        """解释单个预测结果
        
        Args:
            X: 特征向量 (1, n_features)
            feature_names: 特征名称列表
            
        Returns:
            自然语言解释
        """
        if self.explainer is None or X is None:
            return "基于您的画像为您推荐此活动"
        
        try:
            # 计算SHAP值
            shap_values = self.explainer.shap_values(X)
            
            # 获取正类的SHAP值（接受推荐）
            if isinstance(shap_values, list):
                shap_value = shap_values[1][0]
            else:
                shap_value = shap_values[0]
            
            # 找出影响最大的前2个特征（只取正向影响的）
            positive_indices = [(i, shap_value[i]) for i in range(len(shap_value)) if shap_value[i] > 0.01]
            positive_indices.sort(key=lambda x: x[1], reverse=True)
            top_positive = positive_indices[:2]
            
            # 生成更自然的解释文本
            if not top_positive:
                return self._generate_default_reason(X)
            
            names = feature_names or self.feature_names
            if X.ndim > 1:
                names = names[:X.shape[1]]
            reasons = []
            for idx, value in top_positive:
                feature = names[idx] if idx < len(names) else f"feature_{idx}"
                reason = self._get_feature_reason(feature, X[0, idx] if X.ndim > 1 else X[idx])
                if reason:
                    reasons.append(reason)
            
            if not reasons:
                return self._generate_default_reason(X)
            
            return "、".join(reasons[:2])
        except Exception as e:
            return self._generate_default_reason(X)
    
    def _get_feature_reason(self, feature: str, value: float) -> str:
        """根据特征生成具体的推荐理由"""
        reason_templates = {
            "factor_social": [
                "符合您的社交偏好",
                "适合喜欢互动的您",
                "社交属性与您匹配"
            ],
            "factor_psych": [
                "契合您的消费心理",
                "符合您的决策风格",
                "与您的偏好相符"
            ],
            "factor_incent": [
                "奖励丰厚值得参与",
                "激励方式适合您",
                "回报率符合您的期望"
            ],
            "factor_tech": [
                "操作简单易上手",
                "技术门槛适中",
                "适合您的使用习惯"
            ],
            "factor_env": [
                "当前热门活动",
                "参与人数众多",
                "口碑良好"
            ],
            "factor_personal": [
                "个性化推荐",
                "专属为您定制",
                "符合您的个人特点"
            ],
            "incentive_amount": [
                "奖励金额可观",
                "收益丰厚",
                "回报率高"
            ],
            "incentive_type_encoded": [
                "奖励类型适合您",
                "激励方式符合偏好"
            ],
            "activity_type_encoded": [
                "活动类型适合您",
                "参与方式简单"
            ]
        }
        
        import random
        templates = reason_templates.get(feature, ["推荐此活动"])
        return random.choice(templates)
    
    def _generate_default_reason(self, X: np.ndarray) -> str:
        """生成默认推荐理由"""
        import random
        default_reasons = [
            "根据您的兴趣推荐",
            "为您精选的活动",
            "符合您的偏好",
            "个性化推荐",
            "热门活动推荐",
            "高性价比活动"
        ]
        return random.choice(default_reasons)
    
    def explain_global(self, X: np.ndarray) -> Dict:
        """全局特征重要性解释
        
        Args:
            X: 特征矩阵
            
        Returns:
            全局特征重要性数据
        """
        if self.explainer is None:
            return {"message": "请先拟合解释器"}
        
        # 计算SHAP值
        shap_values = self.explainer.shap_values(X)
        
        # 计算平均绝对SHAP值
        if isinstance(shap_values, list):
            mean_shap = np.abs(shap_values[1]).mean(axis=0)
        else:
            mean_shap = np.abs(shap_values).mean(axis=0)
        
        # 排序
        sorted_indices = np.argsort(mean_shap)[::-1]
        
        feature_count = len(mean_shap)
        names = self.feature_names[:feature_count]
        return {
            "features": [
                {
                    "name": names[idx],
                    "label": self.feature_labels.get(names[idx], names[idx]),
                    "importance": float(mean_shap[idx])
                }
                for idx in sorted_indices
            ]
        }
    
    def generate_force_plot_data(self, X: np.ndarray) -> Dict:
        """生成力图数据（用于可视化）
        
        Args:
            X: 单个样本特征向量
            
        Returns:
            力图数据
        """
        if self.explainer is None:
            return {}
        
        shap_values = self.explainer.shap_values(X)
        
        if isinstance(shap_values, list):
            shap_value = shap_values[1][0]
        else:
            shap_value = shap_values[0]
        
        base_value = self.explainer.expected_value
        if isinstance(base_value, list):
            base_value = base_value[1]
        
        names = self.feature_names[:X.shape[1]] if X.ndim > 1 else self.feature_names[:len(X)]
        return {
            "base_value": float(base_value),
            "shap_values": [float(v) for v in shap_value],
            "feature_names": [self.feature_labels.get(f, f) for f in names],
            "feature_values": [float(X[0, i]) for i in range(len(names))]
        }