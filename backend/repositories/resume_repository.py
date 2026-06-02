from sqlmodel import Session
from backend.db.models.resume import Resume


class ResumeRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, resume_id: int) -> Resume | None:
        return self.db.get(Resume, resume_id)

    def update(self, resume: Resume, data: dict) -> Resume:
        resume.sqlmodel_update(data)
        self.db.commit()
        self.db.refresh(resume)
        return resume

    def create(self, data: dict) -> Resume:
        resume = Resume(**data)
        self.db.add(resume)
        self.db.commit()
        self.db.refresh(resume)
        return resume
