from pydantic import BaseModel
from typing import Optional, List

class UserPreferences(BaseModel):
    frequency: str = "daily"
    activityTypes: List[str] = ["invite", "quiz", "share"]
    incentiveTypes: List[str] = ["red_packet", "points", "coupon"]

class UserProfileUpdate(BaseModel):
    factor_social: Optional[float] = None
    factor_psych: Optional[float] = None
    factor_incent: Optional[float] = None
    factor_tech: Optional[float] = None
    factor_env: Optional[float] = None
    factor_personal: Optional[float] = None
    cluster_id: Optional[int] = None
    cluster_tag: Optional[str] = None
    questionnaire_completed: Optional[int] = None

class UserProfileResponse(BaseModel):
    user_id: int
    factor_social: Optional[float]
    factor_psych: Optional[float]
    factor_incent: Optional[float]
    factor_tech: Optional[float]
    factor_env: Optional[float]
    factor_personal: Optional[float]
    cluster_id: Optional[int]
    cluster_tag: Optional[str]
    questionnaire_completed: int
    preference_frequency: Optional[str] = None
    preference_activity_types: Optional[str] = None
    preference_incentive_types: Optional[str] = None

    model_config = {"from_attributes": True}

    def to_dict(self):
        # 为了兼容现有代码，保留to_dict方法（Pydantic模型本身有dict()方法）
        return self.model_dump()

