import json
import pytest
from unittest.mock import patch, MagicMock
from fastapi import HTTPException

from backend.services.analysis_service import AnalysisService
from backend.db.models.match_result import MatchResult


class TestAnalysisService:

    def test_compare_success(self, db_session, sample_user, sample_resume, sample_job):
        svc = AnalysisService(db_session)
        result = svc.compare(sample_user.id, sample_resume.id, sample_job.id)
        assert result["match_score"] == 100.0
        assert "python" in result["matched_skills"]
        assert "fastapi" in result["matched_skills"]
        assert result["missing_skills"] == []

    def test_compare_caches_result(self, db_session, sample_user, sample_resume, sample_job):
        svc = AnalysisService(db_session)
        result1 = svc.compare(sample_user.id, sample_resume.id, sample_job.id)
        result2 = svc.compare(sample_user.id, sample_resume.id, sample_job.id)
        assert result1["id"] == result2["id"]
        assert result1["match_score"] == result2["match_score"]

    def test_compare_resume_not_found(self, db_session, sample_user, sample_job):
        svc = AnalysisService(db_session)
        with pytest.raises(HTTPException) as exc_info:
            svc.compare(sample_user.id, 9999, sample_job.id)
        assert exc_info.value.status_code == 404

    def test_compare_resume_wrong_user(self, db_session, sample_resume, sample_job):
        svc = AnalysisService(db_session)
        with pytest.raises(HTTPException) as exc_info:
            svc.compare(9999, sample_resume.id, sample_job.id)
        assert exc_info.value.status_code == 400

    def test_compare_job_not_found(self, db_session, sample_user, sample_resume):
        svc = AnalysisService(db_session)
        with pytest.raises(HTTPException) as exc_info:
            svc.compare(sample_user.id, sample_resume.id, 9999)
        assert exc_info.value.status_code == 404

    def test_compare_skills_missing(self, db_session, sample_user, sample_job):
        resume_no_skills = MagicMock()
        resume_no_skills.id = 999
        resume_no_skills.user_id = sample_user.id
        resume_no_skills.skills_data = None

        svc = AnalysisService(db_session)
        from backend.db.models.resume import Resume
        resume = Resume(
            user_id=sample_user.id,
            title="No Skills",
            file_path="/tmp/test.pdf",
            skills_data=None,
        )
        db_session.add(resume)
        db_session.commit()
        db_session.refresh(resume)

        with pytest.raises(HTTPException) as exc_info:
            svc.compare(sample_user.id, resume.id, sample_job.id)
        assert exc_info.value.status_code == 400

    def test_list_matches_empty(self, db_session):
        svc = AnalysisService(db_session)
        result = svc.list_matches()
        assert result == []

    def test_list_matches_with_data(self, db_session, sample_match):
        svc = AnalysisService(db_session)
        result = svc.list_matches()
        assert len(result) == 1
        assert result[0]["match_score"] == 100.0

    def test_list_matches_pagination(self, db_session, sample_user, sample_resume, sample_job):
        svc = AnalysisService(db_session)
        svc.compare(sample_user.id, sample_resume.id, sample_job.id)
        result = svc.list_matches(skip=0, limit=1)
        assert len(result) == 1
        result = svc.list_matches(skip=1, limit=1)
        assert len(result) == 0

    def test_compare_partial_match(self, db_session, sample_user, sample_job):
        from backend.db.models.resume import Resume
        resume = Resume(
            user_id=sample_user.id,
            title="Partial",
            file_path="/tmp/test.pdf",
            skills_data='{"languages": ["python"], "frameworks": []}',
        )
        db_session.add(resume)
        db_session.commit()
        db_session.refresh(resume)

        svc = AnalysisService(db_session)
        result = svc.compare(sample_user.id, resume.id, sample_job.id)
        assert result["match_score"] == 50.0
        assert result["matched_skills"] == ["python"]
        assert result["missing_skills"] == ["fastapi"]
