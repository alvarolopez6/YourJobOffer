import json
from sqlmodel import Session
from backend.repositories import JobRepository
from backend.utils import SkillExtractor
from backend.db.models.job import Job


class JobService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = JobRepository(db)

    def list(self, skip: int = 0, limit: int = 10) -> list[Job]:
        return self.repo.get_all(skip, limit)

    def get(self, job_id: int) -> Job | None:
        return self.repo.get_by_id(job_id)

    def create(self, data: dict) -> Job:
        job = self.repo.create(data)
        self.extract_skills(job.id)
        return self.repo.get_by_id(job.id)

    def extract_skills(self, job_id: int) -> dict | None:
        job = self.repo.get_by_id(job_id)
        if not job:
            return None
        if job.skills_data:
            return json.loads(job.skills_data)
        skills = SkillExtractor().extract(job.description)
        self.repo.update(job, {"skills_data": json.dumps(skills)})
        return skills

    def update(self, job_id: int, data: dict) -> Job | None:
        job = self.repo.get_by_id(job_id)
        if not job:
            return None
        updated = self.repo.update(job, data)
        if "description" in data:
            self.repo.update(updated, {"skills_data": None})
            self.extract_skills(updated.id)
        return self.repo.get_by_id(job_id)

    def delete(self, job_id: int) -> bool:
        job = self.repo.get_by_id(job_id)
        if not job:
            return False
        self.repo.delete(job)
        return True
