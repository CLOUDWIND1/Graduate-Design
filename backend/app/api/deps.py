"""
API依赖模块
文件名：app/api/deps.py
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from typing import Optional

from app.database import get_db
from app.config import settings
from app.models import User, UserRole
from app.utils.logger import logger


# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    验证JWT令牌并返回当前用户
    
    Args:
        token: JWT令牌
        db: 数据库会话
        
    Returns:
        当前登录的用户对象
        
    Raises:
        HTTPException: 令牌无效或用户不存在
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无效的认证令牌",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # logger.debug(f"[AUTH] Validating token fragment: {token[:10]}..." if token else "[AUTH] No token provided")
    
    try:
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        username: str = payload.get("sub")
        # logger.debug(f"[AUTH] Token decoded, username: {username}")
        if username is None:
            raise credentials_exception
    except JWTError as e:
        logger.warning(f"[AUTH] JWT Error: {e}")
        raise credentials_exception
    
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        logger.warning(f"[AUTH] User not found: {username}")
        raise credentials_exception
    
    if user.status != 1:  # UserStatus.ACTIVE
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用户已被禁用"
        )
    
    # logger.info(f"[AUTH] User authenticated: {user.username}")
    return user


def get_current_admin(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    验证当前用户是否为管理员
    
    Args:
        current_user: 当前登录用户
        
    Returns:
        管理员用户对象
        
    Raises:
        HTTPException: 用户不是管理员
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足，需要管理员权限"
        )
    return current_user


def get_optional_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User | None:
    """
    可选的用户认证，不强制要求登录
    
    Args:
        token: JWT令牌（可选）
        db: 数据库会话
        
    Returns:
        用户对象或None
    """
    if not token:
        return None
    
    try:
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        username: str = payload.get("sub")
        if username is None:
            return None
        
        user = db.query(User).filter(User.username == username).first()
        return user
    except JWTError:
        return None

