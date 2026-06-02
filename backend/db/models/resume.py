from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime


class Resume(SQLModel, table=True):
    __tablename__ = "resumes"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", nullable=False)
    title: str = Field(nullable=False)
    file_path: str = Field(nullable=False)
    extracted_text: Optional[str] = None
    skills_data: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    user: "User" = Relationship(back_populates="resumes")
    match_results: List["MatchResult"] = Relationship(back_populates="resume")
