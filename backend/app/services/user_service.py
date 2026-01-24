"""用户服务"""
from sqlalchemy.orm import Session
from app.models.user import User

class UserService:
    """用户业务逻辑"""
    
    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> User:
        """根据ID获取用户"""
        return db.query(User).filter(User.id == user_id).first()
    
    @staticmethod
    def get_user_by_username(db: Session, username: str) -> User:
        """根据用户名获取用户"""
        return db.query(User).filter(User.username == username).first()
    
    @staticmethod
    def create_user(db: Session, username: str, password: str, email: str = None) -> User:
        """创建新用户"""
        user = User(username=username, password=password, email=email)
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
