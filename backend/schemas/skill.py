from pydantic import BaseModel


class SkillMatch(BaseModel):
    name: str
    importance: int | None = None
    proficiency: str | None = None
    matched: bool
