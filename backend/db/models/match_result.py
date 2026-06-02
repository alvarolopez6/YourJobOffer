from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from datetime import datetime


class MatchResult(SQLModel, table=True):
    __tablename__ = "match_results"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", nullable=False)
    resume_id: int = Field(foreign_key="resumes.id", nullable=False)
    job_id: int = Field(foreign_key="jobs.id", nullable=False)
    match_score: float = Field(nullable=False)
    matched_skills: str = Field(nullable=False)
    missing_skills: str = Field(nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    user: "User" = Relationship(back_populates="match_results")
    resume: "Resume" = Relationship(back_populates="match_results")
    job: "Job" = Relationship(back_populates="match_results")
