"""认证API路由"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime, timedelta
from jose import jwt

from app.database import get_db
from app.schemas.user import UserCreate
from app.models import User, UserProfile
from app.config import settings
from app.utils.auth import verify_password, get_password_hash


router = APIRouter()


class LoginRequest(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


def create_access_token(data: dict, expires_delta: timedelta = None):
    """创建JWT令牌，默认使用配置的分钟数"""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)



@router.post("/login", response_model=Token)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    """用户登录"""
    user = db.query(User).filter(User.username == request.username).first()
    
    if not user or not verify_password(request.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if user.status != 1:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用户已被禁用"
        )
    
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    """用户注册"""
    # 检查用户名是否已存在
    existing_user = db.query(User).filter(User.username == user.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在"
        )
    
    # 创建用户
    new_user = User(
        username=user.username,
        password=get_password_hash(user.password),
        email=user.email,
        phone=user.phone,
        role="user",
        status=1
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # 创建默认用户画像
    profile = UserProfile(
        user_id=new_user.id,
        factor_social=0.5,
        factor_psych=0.5,
        factor_incent=0.5,
        factor_tech=0.5,
        factor_env=0.5,
        factor_personal=0.5,
        cluster_id=0,
        cluster_tag="新用户",
        questionnaire_completed=0
    )
    db.add(profile)
    db.commit()
    
    return {"message": "注册成功", "user_id": new_user.id}


@router.post("/logout")
def logout():
    """用户登出"""
    return {"message": "登出成功"}

