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
