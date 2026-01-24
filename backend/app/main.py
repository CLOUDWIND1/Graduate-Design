"""
FastAPI应用入口文件
文件名：app/main.py
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import settings
from app.database import engine, Base
from app.api import auth, users, activities, recommendations, admin, rewards
from app.utils.logger import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时执行
    logger.info("🚀 启动全民获客智能推荐系统...")
    # 创建数据库表
    Base.metadata.create_all(bind=engine)
    logger.info("✅ 数据库初始化完成")
    yield
    # 关闭时执行
    logger.info("👋 关闭系统...")


# 创建FastAPI应用
app = FastAPI(
    title="全民获客智能推荐系统",
    description="基于用户行为分群的智能推荐系统",
    version="1.0.0",
    lifespan=lifespan
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth.router, prefix="/api/v1/auth", tags=["认证"])
app.include_router(users.router, prefix="/api/v1/users", tags=["用户"])
app.include_router(activities.router, prefix="/api/v1/activities", tags=["活动"])
app.include_router(recommendations.router, prefix="/api/v1/recommendations", tags=["推荐"])
app.include_router(rewards.router, prefix="/api/v1", tags=["奖励"])
app.include_router(admin.router, prefix="/api/v1/admin", tags=["管理"])


@app.get("/")
async def root():
    """根路径"""
    return {"message": "全民获客智能推荐系统", "version": "1.0.0"}


@app.get("/health")
@app.get("/api/v1/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy"}