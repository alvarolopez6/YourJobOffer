import json
import os
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi import UploadFile, HTTPException
from io import BytesIO

from backend.services.resume_service import ResumeService
from backend.db.models.resume import Resume


class TestResumeService:

    def test_get_resume_found(self, db_session, sample_resume):
        svc = ResumeService(db_session)
        result = svc.get(sample_resume.id)
        assert result.id == sample_resume.id

    def test_get_resume_not_found(self, db_session):
        svc = ResumeService(db_session)
        assert svc.get(9999) is None

    @patch("backend.services.resume_service.PdfExtractor")
    def test_extract_text(self, mock_pdf_cls, db_session, sample_resume):
        mock_pdf_cls.extract.return_value = "Extracted text content"

        svc = ResumeService(db_session)
        resume_no_text = Resume(
            user_id=sample_resume.user_id,
            title="No Text",
            file_path="/tmp/test.pdf",
        )
        db_session.add(resume_no_text)
        db_session.commit()
        db_session.refresh(resume_no_text)

        result = svc.extract_text(resume_no_text.id)
        assert result == "Extracted text content"

    def test_extract_text_caching(self, db_session, sample_resume):
        svc = ResumeService(db_session)
        result = svc.extract_text(sample_resume.id)
        assert result == sample_resume.extracted_text

    def test_extract_text_not_found(self, db_session):
        svc = ResumeService(db_session)
        assert svc.extract_text(9999) is None

    @patch("backend.services.resume_service.SkillExtractor")
    @patch("backend.services.resume_service.PdfExtractor")
    def test_extract_skills(self, mock_pdf_cls, mock_extractor_cls, db_session):
        mock_pdf_cls.extract.return_value = "Python developer"
        mock_extractor = MagicMock()
        mock_extractor.extract.return_value = {"languages": ["python"]}
        mock_extractor_cls.return_value = mock_extractor

        svc = ResumeService(db_session)
        resume = Resume(
            user_id=1,
            title="Test",
            file_path="/tmp/test.pdf",
            extracted_text="Python developer",
        )
        db_session.add(resume)
        db_session.commit()
        db_session.refresh(resume)

        result = svc.extract_skills(resume.id)
        assert result == {"languages": ["python"]}

    def test_extract_skills_caching(self, db_session, sample_resume):
        svc = ResumeService(db_session)
        result = svc.extract_skills(sample_resume.id)
        assert result is not None
        assert "python" in result["languages"]

    def test_extract_skills_not_found(self, db_session):
        svc = ResumeService(db_session)
        assert svc.extract_skills(9999) is None

    @patch("backend.services.resume_service.SkillExtractor")
    @patch("backend.services.resume_service.PdfExtractor")
    @patch("backend.services.resume_service.settings")
    def test_upload_rejects_non_pdf(self, mock_settings, mock_pdf_cls, mock_extractor_cls, db_session):
        mock_settings.UPLOAD_DIR = "/tmp/test_uploads"
        svc = ResumeService(db_session)
        file = MagicMock(spec=UploadFile)
        file.filename = "resume.txt"
        with pytest.raises(HTTPException) as exc_info:
            svc.upload(file, 1, "Test")
        assert exc_info.value.status_code == 400

    @patch("backend.services.resume_service.SkillExtractor")
    @patch("backend.services.resume_service.PdfExtractor")
    @patch("backend.services.resume_service.settings")
    @patch("backend.services.resume_service.Path")
    def test_upload_saves_file(self, mock_path_cls, mock_settings, mock_pdf_cls, mock_extractor_cls, db_session, sample_user):
        mock_settings.UPLOAD_DIR = "/tmp/test_uploads"
        mock_path_instance = MagicMock()
        mock_path_cls.return_value = mock_path_instance
        mock_path_instance.__truediv__ = MagicMock(return_value="/tmp/test_uploads/fake.pdf")
        mock_path_instance.mkdir = MagicMock()
        mock_path_instance.suffix = ".pdf"

        mock_pdf_cls.extract.return_value = "Resume text"
        mock_extractor = MagicMock()
        mock_extractor.extract.return_value = {"languages": []}
        mock_extractor_cls.return_value = mock_extractor

        svc = ResumeService(db_session)
        file = MagicMock(spec=UploadFile)
        file.filename = "resume.pdf"
        file.file = MagicMock()
        file.file.read.return_value = b"PDF content"

        with patch("builtins.open", MagicMock()):
            with patch("backend.services.resume_service.uuid.uuid4", return_value="fake-uuid"):
                result = svc.upload(file, sample_user.id, "My Resume")

        assert result.title == "My Resume"
        assert result.user_id == sample_user.id
