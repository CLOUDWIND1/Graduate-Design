from pydantic import BaseModel, Field
from typing import List

class QuestionnaireSubmit(BaseModel):
    """问卷提交数据"""
    answers: List[int] = Field(..., description="20个答案，每个1-5", min_items=20, max_items=20)
