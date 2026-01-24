"""
推荐系统配置加载器
文件名：app/config_loader.py
"""

import json
import os
from typing import Any, Dict, Optional
from functools import lru_cache


class RecommendationConfig:
    """推荐系统配置管理类"""
    
    _instance: Optional['RecommendationConfig'] = None
    _config: Dict[str, Any] = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_config()
        return cls._instance
    
    def _load_config(self):
        """加载配置文件"""
        config_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'config',
            'recommendation_config.json'
        )
        
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                self._config = json.load(f)
        else:
            self._config = self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """返回默认配置"""
        return {
            "training": {
                "random_forest": {
                    "n_estimators": 100,
                    "max_depth": 10,
                    "random_state": 42
                },
                "threshold": {"default": 0.5}
            },
            "clustering": {"n_clusters": 10},
            "inference": {
                "cache": {"user_profile_ttl": 300},
                "timeout": {"total_request_ms": 2000}
            }
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        获取配置值，支持点号分隔的嵌套键
        例如: config.get("training.random_forest.n_estimators")
        """
        keys = key.split('.')
        value = self._config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    @property
    def training(self) -> Dict[str, Any]:
        return self._config.get('training', {})
    
    @property
    def clustering(self) -> Dict[str, Any]:
        return self._config.get('clustering', {})
    
    @property
    def inference(self) -> Dict[str, Any]:
        return self._config.get('inference', {})
    
    @property
    def cluster_strategies(self) -> Dict[str, Any]:
        return self._config.get('cluster_strategies', {})
    
    @property
    def explainability(self) -> Dict[str, Any]:
        return self._config.get('explainability', {})
    
    def get_cluster_strategy(self, cluster_id: int) -> Dict[str, Any]:
        """获取指定聚类的运营策略"""
        return self.cluster_strategies.get(str(cluster_id), {})
    
    def get_explanation_template(self, cluster_id: int, template_key: str) -> str:
        """获取解释模板"""
        strategy = self.get_cluster_strategy(cluster_id)
        templates = strategy.get('explanation_templates', {})
        return templates.get(template_key, "为您推荐「{activity_name}」")
    
    def get_feature_name(self, feature_key: str) -> str:
        """获取特征的中文名称"""
        feature_names = self.get('explainability.feature_names', {})
        return feature_names.get(feature_key, feature_key)
    
    def get_config(self) -> Dict[str, Any]:
        """获取完整配置"""
        return {
            "max_recommendations": self.get("inference.max_recommendations", 10),
            "cold_start_count": self.get("inference.cold_start_count", 5),
            "min_score": self.get("training.threshold.default", 0.3),
            "diversity_weight": self.get("inference.diversity_weight", 0.2)
        }
    
    def update_config(self, new_config: Dict[str, Any]) -> None:
        """更新配置"""
        # 更新内存中的配置
        if "max_recommendations" in new_config:
            if "inference" not in self._config:
                self._config["inference"] = {}
            self._config["inference"]["max_recommendations"] = new_config["max_recommendations"]
        
        if "cold_start_count" in new_config:
            if "inference" not in self._config:
                self._config["inference"] = {}
            self._config["inference"]["cold_start_count"] = new_config["cold_start_count"]
        
        if "min_score" in new_config:
            if "training" not in self._config:
                self._config["training"] = {}
            if "threshold" not in self._config["training"]:
                self._config["training"]["threshold"] = {}
            self._config["training"]["threshold"]["default"] = new_config["min_score"]
        
        if "diversity_weight" in new_config:
            if "inference" not in self._config:
                self._config["inference"] = {}
            self._config["inference"]["diversity_weight"] = new_config["diversity_weight"]
        
        # 保存到文件
        self._save_config()
    
    def _save_config(self) -> None:
        """保存配置到文件"""
        config_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'config',
            'recommendation_config.json'
        )
        
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(self._config, f, indent=2, ensure_ascii=False)


# 单例实例
@lru_cache()
def get_recommendation_config() -> RecommendationConfig:
    return RecommendationConfig()


# 便捷访问
config_loader = get_recommendation_config()
rec_config = config_loader  # 别名
