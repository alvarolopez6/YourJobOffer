import pytest
from backend.repositories.job_repository import JobRepository
from backend.db.models.job import Job


class TestJobRepository:

    def test_create(self, db_session):
        repo = JobRepository(db_session)
        job = repo.create({
            "title": "Test Job",
            "company": "Test Corp",
            "description": "A test job",
        })
        assert job.id is not None
        assert job.title == "Test Job"

    def test_get_by_id(self, db_session, sample_job):
        repo = JobRepository(db_session)
        result = repo.get_by_id(sample_job.id)
        assert result is not None
        assert result.title == "Backend Developer"

    def test_get_by_id_not_found(self, db_session):
        repo = JobRepository(db_session)
        assert repo.get_by_id(9999) is None

    def test_get_all(self, db_session):
        repo = JobRepository(db_session)
        repo.create({"description": "Job 1"})
        repo.create({"description": "Job 2"})
        result = repo.get_all()
        assert len(result) == 2

    def test_get_all_pagination(self, db_session):
        repo = JobRepository(db_session)
        for i in range(5):
            repo.create({"description": f"Job {i}"})
        result = repo.get_all(skip=0, limit=2)
        assert len(result) == 2

    def test_update(self, db_session, sample_job):
        repo = JobRepository(db_session)
        updated = repo.update(sample_job, {"title": "Updated Title"})
        assert updated.title == "Updated Title"

    def test_delete(self, db_session, sample_job):
        repo = JobRepository(db_session)
        repo.delete(sample_job)
        assert repo.get_by_id(sample_job.id) is None
