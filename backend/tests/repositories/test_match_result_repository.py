import json
import pytest
from backend.repositories.match_result_repository import MatchResultRepository
from backend.db.models.match_result import MatchResult


class TestMatchResultRepository:

    def test_create(self, db_session, sample_user, sample_resume, sample_job):
        repo = MatchResultRepository(db_session)
        result = repo.create({
            "user_id": sample_user.id,
            "resume_id": sample_resume.id,
            "job_id": sample_job.id,
            "match_score": 75.0,
            "matched_skills": json.dumps(["python"]),
            "missing_skills": json.dumps(["fastapi"]),
        })
        assert result.id is not None
        assert result.match_score == 75.0

    def test_get_all(self, db_session, sample_match):
        repo = MatchResultRepository(db_session)
        result = repo.get_all()
        assert len(result) == 1

    def test_get_all_pagination(self, db_session, sample_user, sample_resume, sample_job):
        repo = MatchResultRepository(db_session)
        for i in range(3):
            repo.create({
                "user_id": sample_user.id,
                "resume_id": sample_resume.id,
                "job_id": sample_job.id,
                "match_score": float(i * 10),
                "matched_skills": json.dumps([]),
                "missing_skills": json.dumps([]),
            })
        result = repo.get_all(skip=0, limit=2)
        assert len(result) == 2

    def test_get_by_resume_and_job(self, db_session, sample_match, sample_resume, sample_job):
        repo = MatchResultRepository(db_session)
        result = repo.get_by_resume_and_job(sample_resume.id, sample_job.id)
        assert result is not None
        assert result.match_score == 100.0

    def test_get_by_resume_and_job_not_found(self, db_session):
        repo = MatchResultRepository(db_session)
        result = repo.get_by_resume_and_job(9999, 9999)
        assert result is None
