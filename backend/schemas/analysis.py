from pydantic import BaseModel
from datetime import datetime


class CompareRequest(BaseModel):
    user_id: int
    resume_id: int
    job_id: int


class MatchResultResponse(BaseModel):
    id: int
    user_id: int
    resume_id: int
    job_id: int
    match_score: float
    matched_skills: list[str]
    missing_skills: list[str]
    created_at: datetime

    model_config = {"from_attributes": True}
