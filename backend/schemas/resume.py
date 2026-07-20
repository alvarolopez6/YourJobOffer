from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ResumeCreate(BaseModel):
    title: str


class ResumeResponse(BaseModel):
    id: int
    user_id: int
    title: str
    extracted_text: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}
