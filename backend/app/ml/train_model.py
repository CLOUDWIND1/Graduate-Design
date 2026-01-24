"""模型训练模块"""
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, classification_report
from typing import Tuple, Dict, Any
import joblib
import os

from app.utils.logger import logger


class ModelTrainer:
    """模型训练类"""
    
    def __init__(self, model_dir: str = "./data/models"):
        self.model_dir = model_dir
        self.scaler = StandardScaler()
        os.makedirs(model_dir, exist_ok=True)
    
    def prepare_data(self, df: pd.DataFrame, target_col: str = "accepted") -> Tuple[np.ndarray, np.ndarray]:
        """准备训练数据"""
        feature_cols = [
            "factor_social", "factor_psych", "factor_incent",
            "factor_tech", "factor_env", "factor_personal",
            "incentive_amount", "incentive_type_encoded", "activity_type_encoded"
        ]
        
        X = df[feature_cols].values
        y = df[target_col].values
        
        return X, y
    
    def train_random_forest(self, X: np.ndarray, y: np.ndarray, **kwargs) -> Dict[str, Any]:
        """训练随机森林模型"""
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # 标准化
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # 训练模型
        model = RandomForestClassifier(
            n_estimators=kwargs.get("n_estimators", 100),
            max_depth=kwargs.get("max_depth", 10),
            random_state=42
        )
        model.fit(X_train_scaled, y_train)
        
        # 评估
        y_pred = model.predict(X_test_scaled)
        accuracy = accuracy_score(y_test, y_pred)
        
        # 保存模型
        model_path = os.path.join(self.model_dir, "rf_model.pkl")
        scaler_path = os.path.join(self.model_dir, "scaler.pkl")
        joblib.dump(model, model_path)
        joblib.dump(self.scaler, scaler_path)
        
        logger.info(f"随机森林模型训练完成，准确率: {accuracy:.4f}")
        
        return {
            "model": model,
            "accuracy": accuracy,
            "model_path": model_path,
            "scaler_path": scaler_path
        }
    
    def train_gradient_boosting(self, X: np.ndarray, y: np.ndarray, **kwargs) -> Dict[str, Any]:
        """训练梯度提升模型"""
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        model = GradientBoostingClassifier(
            n_estimators=kwargs.get("n_estimators", 100),
            max_depth=kwargs.get("max_depth", 5),
            random_state=42
        )
        model.fit(X_train_scaled, y_train)
        
        y_pred = model.predict(X_test_scaled)
        accuracy = accuracy_score(y_test, y_pred)
        
        model_path = os.path.join(self.model_dir, "gb_model.pkl")
        joblib.dump(model, model_path)
        
        logger.info(f"梯度提升模型训练完成，准确率: {accuracy:.4f}")
        
        return {
            "model": model,
            "accuracy": accuracy,
            "model_path": model_path
        }
    
    def cross_validate(self, model, X: np.ndarray, y: np.ndarray, cv: int = 5) -> Dict[str, float]:
        """交叉验证"""
        X_scaled = self.scaler.fit_transform(X)
        scores = cross_val_score(model, X_scaled, y, cv=cv)
        
        return {
            "mean_score": scores.mean(),
            "std_score": scores.std(),
            "scores": scores.tolist()
        }
