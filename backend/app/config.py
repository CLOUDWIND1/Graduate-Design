"""
配置文件
文件名：app/config.py
"""

from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """应用配置"""
    # 应用配置
    APP_NAME: str = "全民获客智能推荐系统"
    DEBUG: bool = True
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24小时
    
    # 数据库配置
    DATABASE_URL: str = "mysql+pymysql://root:password@localhost:3306/recommendation_system"
    
    # Redis配置
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # CORS配置
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8080", "http://localhost:5173", "http://localhost:5174", "http://localhost:5175"]
    
    # 文件路径配置
    MODEL_DIR: str = "."  # 模型文件在backend根目录
    DATA_DIR: str = "data"
    LOG_DIR: str = "logs"
    
    class Config:
        env_file = ".env"


settings = Settings()