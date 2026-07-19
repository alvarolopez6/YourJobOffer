import json
import pytest
from unittest.mock import patch, MagicMock

from backend.db.models.user import User
from backend.db.models.job import Job
from backend.db.models.resume import Resume
from backend.db.models.match_result import MatchResult


MOCK_SKILLS = {"languages": ["python"], "frameworks": ["fastapi"]}


class TestHealthEndpoint:

    def test_health(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


class TestUsersEndpoints:

    def test_list_users(self, client, sample_user):
        response = client.get("/api/users/")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1

    def test_get_user(self, client, sample_user):
        response = client.get(f"/api/users/{sample_user.id}")
        assert response.status_code == 200
        assert response.json()["email"] == "test@example.com"

    def test_get_user_not_found(self, client):
        response = client.get("/api/users/9999")
        assert response.status_code == 404

    def test_create_user(self, client):
        response = client.post("/api/users/", json={
            "email": "new@test.com",
            "name": "New User",
        })
        assert response.status_code == 201
        assert response.json()["email"] == "new@test.com"

    def test_create_user_duplicate_email(self, client, sample_user):
        response = client.post("/api/users/", json={
            "email": "test@example.com",
            "name": "Duplicate",
        })
        assert response.status_code == 400

    def test_delete_user(self, client, sample_user):
        response = client.delete(f"/api/users/{sample_user.id}")
        assert response.status_code == 204

    def test_delete_user_not_found(self, client):
        response = client.delete("/api/users/9999")
        assert response.status_code == 404


class TestJobsEndpoints:

    @patch("backend.services.job_service.SkillExtractor")
    def test_create_job(self, mock_extractor_cls, client):
        mock_extractor = MagicMock()
        mock_extractor.extract.return_value = MOCK_SKILLS
        mock_extractor_cls.return_value = mock_extractor

        response = client.post("/api/jobs/", data={
            "title": "Test Job",
            "company": "Test Corp",
            "description": "Python developer needed",
        })
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Test Job"

    def test_list_jobs(self, client, sample_job):
        response = client.get("/api/jobs/")
        assert response.status_code == 200
        assert len(response.json()) >= 1

    def test_get_job(self, client, sample_job):
        response = client.get(f"/api/jobs/{sample_job.id}")
        assert response.status_code == 200
        assert response.json()["title"] == "Backend Developer"

    def test_get_job_not_found(self, client):
        response = client.get("/api/jobs/9999")
        assert response.status_code == 404

    def test_delete_job(self, client, sample_job):
        response = client.delete(f"/api/jobs/{sample_job.id}")
        assert response.status_code == 204

    def test_delete_job_not_found(self, client):
        response = client.delete("/api/jobs/9999")
        assert response.status_code == 404


class TestResumesEndpoints:

    def test_get_resume(self, client, sample_resume):
        response = client.get(f"/api/resumes/{sample_resume.id}")
        assert response.status_code == 200
        assert response.json()["title"] == "My Resume"

    def test_get_resume_not_found(self, client):
        response = client.get("/api/resumes/9999")
        assert response.status_code == 404

    @patch("backend.services.resume_service.SkillExtractor")
    @patch("backend.services.resume_service.PdfExtractor")
    def test_upload_resume(self, mock_pdf_cls, mock_extractor_cls, client, sample_user):
        mock_pdf_cls.extract.return_value = "Resume text"
        mock_extractor = MagicMock()
        mock_extractor.extract.return_value = MOCK_SKILLS
        mock_extractor_cls.return_value = mock_extractor

        import io
        pdf_content = b"%PDF-1.4 fake content"
        response = client.post(
            "/api/resumes/upload",
            files={"file": ("resume.pdf", io.BytesIO(pdf_content), "application/pdf")},
            data={"user_id": sample_user.id, "title": "My Resume"},
        )
        assert response.status_code == 201
        assert response.json()["title"] == "My Resume"


class TestAnalysisEndpoints:

    def test_compare(self, client, sample_user, sample_resume, sample_job):
        response = client.post("/api/analysis/compare", json={
            "user_id": sample_user.id,
            "resume_id": sample_resume.id,
            "job_id": sample_job.id,
        })
        assert response.status_code == 201
        data = response.json()
        assert data["match_score"] == 100.0

    def test_compare_not_found(self, client, sample_user):
        response = client.post("/api/analysis/compare", json={
            "user_id": sample_user.id,
            "resume_id": 9999,
            "job_id": 1,
        })
        assert response.status_code == 404

    def test_list_matches_empty(self, client):
        response = client.get("/api/analysis/matches")
        assert response.status_code == 200
        assert response.json() == []

    def test_list_matches_with_data(self, client, sample_match):
        response = client.get("/api/analysis/matches")
        assert response.status_code == 200
        assert len(response.json()) == 1
