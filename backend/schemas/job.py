from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime


class JobCreate(BaseModel):
    title: Optional[str] = None
    company: Optional[str] = None
    description: str
    url: Optional[str] = None
    location: Optional[str] = None


class JobUpdate(BaseModel):
    title: Optional[str] = None
    company: Optional[str] = None
    description: Optional[str] = None
    url: Optional[str] = None
    location: Optional[str] = None


class JobResponse(BaseModel):
    id: int
    title: Optional[str] = None
    company: Optional[str] = None
    description: str
    url: Optional[str] = None
    location: Optional[str] = None
    posted_date: Optional[date] = None
    salary_range: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}
