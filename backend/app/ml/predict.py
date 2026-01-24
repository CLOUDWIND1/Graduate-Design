"""
推荐预测模型
文件名：app/ml/predict.py
"""

import joblib
import numpy as np
import pandas as pd
from typing import List, Dict, Optional
import os

from app.utils.logger import logger


class RecommenderModel:
    """推荐预测模型类"""
    
    def __init__(self):
        self.model = None
        self.scaler = None
        self.factor_analyzer = None
        self.feature_names = [
            "factor_social", "factor_psych", "factor_incent", 
            "factor_tech", "factor_env", "factor_personal",
            "incentive_amount", "incentive_type_encoded", "activity_type_encoded"
        ]
        self._load_model()
    
    def _load_model(self):
        """加载模型"""
        # 优先加载预训练的随机森林模型
        rf_model_path = "./best_rf_model.pkl"
        scaler_path = "./scaler.pkl"
        fa_path = "./factor_analyzer.pkl"
        
        try:
            if os.path.exists(rf_model_path):
                self.model = joblib.load(rf_model_path)
                logger.info(f"成功加载预训练模型: {rf_model_path}")
            
            if os.path.exists(scaler_path):
                self.scaler = joblib.load(scaler_path)
                logger.info(f"成功加载标准化器: {scaler_path}")
            
            if os.path.exists(fa_path):
                self.factor_analyzer = joblib.load(fa_path)
                logger.info(f"成功加载因子分析器: {fa_path}")
        except Exception as e:
            logger.warning(f"加载预训练模型失败: {e}")
        
        # 如果没有加载到模型，创建默认模型
        if self.model is None:
            self.model = self._create_default_model()
            logger.info("使用默认模型")
    
    def _create_default_model(self):
        """创建默认模型（用于冷启动）"""
        from sklearn.ensemble import RandomForestClassifier
        return RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            n_jobs=-1
        )
    
    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """预测概率"""
        if self.model is None:
            return np.array([[0.5, 0.5]])
        
        try:
            # 检查模型期望的特征数并对齐
            expected = self._get_expected_features()
            X_aligned = self._align_features(X, expected)
            return self.model.predict_proba(X_aligned)
        except Exception as e:
            logger.error(f"predict_proba失败: {e}")
            return np.array([[0.5, 0.5]])
    
    def _get_expected_features(self) -> int:
        """获取模型期望的特征数"""
        if self.model is None:
            return 9
        return getattr(self.model, 'n_features_in_', None) or getattr(self.model, 'n_features_', 9)
    
    def _align_features(self, X: np.ndarray, expected: int) -> np.ndarray:
        """将输入特征对齐到模型期望维度"""
        if X.ndim == 1:
            X = X.reshape(1, -1)
        actual = X.shape[1]
        
        if actual == expected:
            return X
        
        # 模型期望3维（因子分析后的模型）
        if expected == 3:
            if self.factor_analyzer is not None and actual >= 6:
                try:
                    return self.factor_analyzer.transform(X[:, :6])
                except Exception:
                    pass
            # 手动降维：将6个用户因子分组平均
            if actual >= 6:
                f1 = (X[0, 0] + X[0, 1]) / 2  # 社会+心理
                f2 = (X[0, 2] + X[0, 3]) / 2  # 激励+技术
                f3 = (X[0, 4] + X[0, 5]) / 2  # 环境+个人
                return np.array([[f1, f2, f3]])
        
        # 截断或补零
        if actual > expected:
            return X[:, :expected]
        else:
            pad = np.zeros((X.shape[0], expected - actual))
            return np.concatenate([X, pad], axis=1)
    
    def predict_proba_single(self, X: np.ndarray) -> float:
        """单样本预测概率
        
        Args:
            X: 单样本特征向量 (1, n_features)
            
        Returns:
            正类（接受推荐）的概率
        """
        try:
            # 检查模型是否存在
            if self.model is None:
                return self._rule_based_score(X)
            
            # 检查模型是否已经拟合
            if not hasattr(self.model, 'classes_'):
                logger.warning("模型未训练，使用规则评分")
                return self._rule_based_score(X)
            
            # 使用统一的特征对齐方法
            proba = self.predict_proba(X)
            return float(proba[0][1])  # 返回接受推荐的概率
            
        except Exception as e:
            logger.error(f"预测失败: {e}")
            return self._rule_based_score(X)
    
    def _rule_based_score(self, X: np.ndarray) -> float:
        """基于规则的评分（模型不可用时的回退方案）"""
        if X is None:
            return 0.5
        if X.ndim == 1:
            X = X.reshape(1, -1)
        # 用户因子越高，接受概率越高
        user_factors = X[0, :6] if X.shape[1] >= 6 else X[0]
        base_score = float(np.mean(user_factors))
        # 激励金额加成（如果有）
        if X.shape[1] > 6:
            incentive = X[0, 6] if X.shape[1] > 6 else 0
            bonus = min(incentive / 100, 0.2)  # 最多加0.2
            base_score = min(base_score + bonus, 0.95)
        return max(0.1, min(0.95, base_score))
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """预测类别"""
        if self.model is None:
            return np.zeros(X.shape[0])
        return self.model.predict(X)
    
    def get_feature_importance(self) -> List[Dict]:
        """获取特征重要性"""
        if self.model is None:
            return []
        
        if not hasattr(self.model, 'feature_importances_'):
            return []
        
        importance = self.model.feature_importances_
        # 根据实际特征数量返回
        names = self.feature_names[:len(importance)] if len(importance) <= len(self.feature_names) else [f"feature_{i}" for i in range(len(importance))]
        return [
            {"feature": name, "importance": float(imp)}
            for name, imp in zip(names, importance)
        ]


# 全局模型实例
_model_instance = None

def get_model() -> RecommenderModel:
    """获取全局模型实例"""
    global _model_instance
    if _model_instance is None:
        _model_instance = RecommenderModel()
    return _model_instance
