from sqlmodel import Session, select
from backend.db.models.job import Job


class JobRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self, skip: int = 0, limit: int = 10) -> list[Job]:
        return self.db.exec(select(Job).offset(skip).limit(limit)).all()

    def get_by_id(self, job_id: int) -> Job | None:
        return self.db.get(Job, job_id)

    def create(self, data: dict) -> Job:
        job = Job(**data)
        self.db.add(job)
        self.db.commit()
        self.db.refresh(job)
        return job

    def update(self, job: Job, data: dict) -> Job:
        job.sqlmodel_update(data)
        self.db.commit()
        self.db.refresh(job)
        return job

    def delete(self, job: Job) -> None:
        self.db.delete(job)
        self.db.commit()
