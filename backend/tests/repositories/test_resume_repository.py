import pytest
from backend.repositories.resume_repository import ResumeRepository
from backend.db.models.resume import Resume


class TestResumeRepository:

    def test_create(self, db_session, sample_user):
        repo = ResumeRepository(db_session)
        resume = repo.create({
            "user_id": sample_user.id,
            "title": "Test Resume",
            "file_path": "/tmp/test.pdf",
        })
        assert resume.id is not None
        assert resume.title == "Test Resume"

    def test_get_by_id(self, db_session, sample_resume):
        repo = ResumeRepository(db_session)
        result = repo.get_by_id(sample_resume.id)
        assert result is not None
        assert result.title == "My Resume"

    def test_get_by_id_not_found(self, db_session):
        repo = ResumeRepository(db_session)
        assert repo.get_by_id(9999) is None

    def test_update(self, db_session, sample_resume):
        repo = ResumeRepository(db_session)
        updated = repo.update(sample_resume, {"title": "Updated Resume"})
        assert updated.title == "Updated Resume"

    def test_update_skills_data(self, db_session, sample_resume):
        repo = ResumeRepository(db_session)
        import json
        skills = json.dumps({"languages": ["python"]})
        updated = repo.update(sample_resume, {"skills_data": skills})
        assert updated.skills_data == skills
