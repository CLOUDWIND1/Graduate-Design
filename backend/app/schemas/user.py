"""用户数据验证schema"""
from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class UserBase(BaseModel):
    """用户基础schema"""
    username: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None

class UserCreate(UserBase):
    """用户创建schema"""
    password: str

class UserUpdate(BaseModel):
    """用户更新schema"""
    email: Optional[EmailStr] = None
    phone: Optional[str] = None

class UserResponse(UserBase):
    """用户响应schema"""
    id: int
    role: str
    status: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
