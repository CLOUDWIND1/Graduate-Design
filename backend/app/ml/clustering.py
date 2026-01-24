"""用户聚类模块"""
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from typing import Dict, List, Any, Optional
import joblib
import os

from app.utils.logger import logger


class UserClustering:
    """用户聚类类"""
    
    def __init__(self, n_clusters: int = 10, model_dir: str = "./data/models"):
        self.n_clusters = n_clusters
        self.model_dir = model_dir
        self.kmeans = None
        self.scaler = StandardScaler()
        self.cluster_labels = {
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
        os.makedirs(model_dir, exist_ok=True)
    
    def fit(self, data: np.ndarray) -> "UserClustering":
        """训练聚类模型
        
        Args:
            data: 用户特征数据，shape=(n_users, n_features)
        
        Returns:
            self
        """
        # 标准化数据
        data_scaled = self.scaler.fit_transform(data)
        
        # 训练KMeans
        self.kmeans = KMeans(
            n_clusters=self.n_clusters,
            random_state=42,
            n_init=10
        )
        self.kmeans.fit(data_scaled)
        
        logger.info(f"聚类模型训练完成，聚类数: {self.n_clusters}")
        
        return self
    
    def predict(self, data: np.ndarray) -> np.ndarray:
        """预测用户所属聚类
        
        Args:
            data: 用户特征数据
            
        Returns:
            聚类标签数组
        """
        if self.kmeans is None:
            raise ValueError("模型未训练，请先调用fit方法")
        
        data_scaled = self.scaler.transform(data)
        return self.kmeans.predict(data_scaled)
    
    def get_cluster_label(self, cluster_id: int) -> str:
        """获取聚类标签名称"""
        return self.cluster_labels.get(cluster_id, f"类型{cluster_id}")
    
    def get_cluster_centers(self) -> np.ndarray:
        """获取聚类中心"""
        if self.kmeans is None:
            raise ValueError("模型未训练")
        return self.kmeans.cluster_centers_
    
    def get_cluster_stats(self, data: np.ndarray, labels: np.ndarray) -> Dict[int, Dict[str, Any]]:
        """获取各聚类的统计信息
        
        Args:
            data: 原始特征数据
            labels: 聚类标签
            
        Returns:
            各聚类的统计信息
        """
        stats = {}
        for i in range(self.n_clusters):
            mask = labels == i
            cluster_data = data[mask]
            
            if len(cluster_data) > 0:
                stats[i] = {
                    "label": self.get_cluster_label(i),
                    "count": int(np.sum(mask)),
                    "mean": cluster_data.mean(axis=0).tolist(),
                    "std": cluster_data.std(axis=0).tolist()
                }
        
        return stats
    
    def save_model(self, filename: str = "clustering_model.pkl"):
        """保存模型"""
        model_path = os.path.join(self.model_dir, filename)
        scaler_path = os.path.join(self.model_dir, "clustering_scaler.pkl")
        
        joblib.dump(self.kmeans, model_path)
        joblib.dump(self.scaler, scaler_path)
        
        logger.info(f"聚类模型已保存: {model_path}")
    
    def load_model(self, filename: str = "clustering_model.pkl"):
        """加载模型"""
        model_path = os.path.join(self.model_dir, filename)
        scaler_path = os.path.join(self.model_dir, "clustering_scaler.pkl")
        
        if os.path.exists(model_path):
            self.kmeans = joblib.load(model_path)
            logger.info(f"聚类模型已加载: {model_path}")
        
        if os.path.exists(scaler_path):
            self.scaler = joblib.load(scaler_path)
