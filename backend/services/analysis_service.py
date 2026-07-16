import json
from fastapi import HTTPException
from sqlmodel import Session

from backend.repositories import MatchResultRepository, ResumeRepository, JobRepository
from backend.utils import MatchEngine


class AnalysisService:
    def __init__(self, db: Session):
        self.db = db
        self.match_repo = MatchResultRepository(db)
        self.resume_repo = ResumeRepository(db)
        self.job_repo = JobRepository(db)

    def compare(self, user_id: int, resume_id: int, job_id: int):
        resume = self.resume_repo.get_by_id(resume_id)
        if not resume:
            raise HTTPException(404, detail="Resume not found")
        if resume.user_id != user_id:
            raise HTTPException(400, detail="Resume does not belong to this user")

        job = self.job_repo.get_by_id(job_id)
        if not job:
            raise HTTPException(404, detail="Job not found")

        existing = self.match_repo.get_by_resume_and_job(resume_id, job_id)
        if existing:
            return {
                "id": existing.id,
                "user_id": existing.user_id,
                "resume_id": existing.resume_id,
                "job_id": existing.job_id,
                "match_score": existing.match_score,
                "matched_skills": json.loads(existing.matched_skills),
                "missing_skills": json.loads(existing.missing_skills),
                "created_at": existing.created_at,
            }

        if not resume.skills_data or not job.skills_data:
            raise HTTPException(400, detail="Skills data missing. Ensure both resume and job have extracted skills.")

        resume_skills = json.loads(resume.skills_data)
        job_skills = json.loads(job.skills_data)

        result = MatchEngine.match(job_skills, resume_skills)

        record = self.match_repo.create({
            "user_id": user_id,
            "resume_id": resume_id,
            "job_id": job_id,
            "match_score": result["match_score"],
            "matched_skills": json.dumps(result["matched_skills"]),
            "missing_skills": json.dumps(result["missing_skills"]),
        })

        return {
            "id": record.id,
            "user_id": record.user_id,
            "resume_id": record.resume_id,
            "job_id": record.job_id,
            "match_score": record.match_score,
            "matched_skills": result["matched_skills"],
            "missing_skills": result["missing_skills"],
            "created_at": record.created_at,
        }

    def list_matches(self, skip: int = 0, limit: int = 10) -> list[dict]:
        records = self.match_repo.get_all(skip, limit)
        result = []
        for r in records:
            result.append({
                "id": r.id,
                "user_id": r.user_id,
                "resume_id": r.resume_id,
                "job_id": r.job_id,
                "match_score": r.match_score,
                "matched_skills": json.loads(r.matched_skills),
                "missing_skills": json.loads(r.missing_skills),
                "created_at": r.created_at,
            })
        return result
