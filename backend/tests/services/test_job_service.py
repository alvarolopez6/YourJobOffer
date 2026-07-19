import json
import pytest
from unittest.mock import patch, MagicMock

from backend.services.job_service import JobService
from backend.db.models.job import Job


MOCK_SKILLS = {"languages": ["python"], "frameworks": ["fastapi"]}


class TestJobService:

    @patch("backend.services.job_service.SkillExtractor")
    def test_create_job_extracts_skills(self, mock_extractor_cls, db_session):
        mock_extractor = MagicMock()
        mock_extractor.extract.return_value = MOCK_SKILLS
        mock_extractor_cls.return_value = mock_extractor

        svc = JobService(db_session)
        data = {
            "title": "Dev",
            "company": "Corp",
            "description": "Python developer",
        }
        job = svc.create(data)
        assert job.id is not None
        assert job.skills_data is not None
        mock_extractor.extract.assert_called_once_with("Python developer")

    def test_get_job_found(self, db_session, sample_job):
        svc = JobService(db_session)
        result = svc.get(sample_job.id)
        assert result.id == sample_job.id

    def test_get_job_not_found(self, db_session):
        svc = JobService(db_session)
        assert svc.get(9999) is None

    @patch("backend.services.job_service.SkillExtractor")
    def test_update_description_reextracts(self, mock_extractor_cls, db_session, sample_job):
        mock_extractor = MagicMock()
        mock_extractor.extract.return_value = MOCK_SKILLS
        mock_extractor_cls.return_value = mock_extractor

        svc = JobService(db_session)
        result = svc.update(sample_job.id, {"description": "New description"})
        assert result.description == "New description"

    @patch("backend.services.job_service.SkillExtractor")
    def test_update_without_description(self, mock_extractor_cls, db_session, sample_job):
        mock_extractor = MagicMock()
        mock_extractor_cls.return_value = mock_extractor

        svc = JobService(db_session)
        svc.update(sample_job.id, {"title": "New Title"})
        mock_extractor.extract.assert_not_called()

    def test_delete_job(self, db_session, sample_job):
        svc = JobService(db_session)
        assert svc.delete(sample_job.id) is True
        assert svc.get(sample_job.id) is None

    def test_delete_job_not_found(self, db_session):
        svc = JobService(db_session)
        assert svc.delete(9999) is False

    def test_list_jobs(self, db_session, sample_job):
        svc = JobService(db_session)
        result = svc.list()
        assert len(result) >= 1

    @patch("backend.services.job_service.SkillExtractor")
    def test_extract_skills_returns_cached(self, mock_extractor_cls, db_session, sample_job):
        mock_extractor_cls.return_value = MagicMock()

        svc = JobService(db_session)
        result = svc.extract_skills(sample_job.id)
        assert result is not None
        assert "python" in result["languages"]
