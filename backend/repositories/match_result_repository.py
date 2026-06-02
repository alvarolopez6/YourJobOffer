from sqlmodel import Session, select
from backend.db.models.match_result import MatchResult


class MatchResultRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self, skip: int = 0, limit: int = 10) -> list[MatchResult]:
        return self.db.exec(select(MatchResult).offset(skip).limit(limit)).all()

    def get_by_resume_and_job(self, resume_id: int, job_id: int) -> MatchResult | None:
        stmt = select(MatchResult).where(
            MatchResult.resume_id == resume_id,
            MatchResult.job_id == job_id,
        )
        return self.db.exec(stmt).first()

    def create(self, data: dict) -> MatchResult:
        result = MatchResult(**data)
        self.db.add(result)
        self.db.commit()
        self.db.refresh(result)
        return result
