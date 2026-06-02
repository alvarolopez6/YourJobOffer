from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import date, datetime


class Job(SQLModel, table=True):
    __tablename__ = "jobs"

    id: Optional[int] = Field(default=None, primary_key=True)
    title: Optional[str] = Field(default=None)
    company: Optional[str] = None
    description: Optional[str] = None
    url: Optional[str] = None
    posted_date: Optional[date] = None
    location: Optional[str] = None
    salary_range: Optional[str] = None
    skills_data: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    match_results: List["MatchResult"] = Relationship(back_populates="job")
