import json
import uuid
from pathlib import Path
from fastapi import UploadFile, HTTPException
from sqlmodel import Session

from backend.config import settings
from backend.repositories import ResumeRepository
from backend.utils import PdfExtractor, SkillExtractor
from backend.db.models.resume import Resume


class ResumeService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = ResumeRepository(db)

    def get(self, resume_id: int) -> Resume | None:
        return self.repo.get_by_id(resume_id)

    def extract_text(self, resume_id: int) -> str | None:
        resume = self.repo.get_by_id(resume_id)
        if not resume:
            return None
        if resume.extracted_text:
            return resume.extracted_text
        text = PdfExtractor.extract(resume.file_path)
        self.repo.update(resume, {"extracted_text": text})
        return text

    def extract_skills(self, resume_id: int) -> dict | None:
        resume = self.repo.get_by_id(resume_id)
        if not resume:
            return None
        if resume.skills_data:
            return json.loads(resume.skills_data)
        text = self.extract_text(resume_id)
        if not text:
            return None
        try:
            skills = SkillExtractor().extract(text)
            self.repo.update(resume, {"skills_data": json.dumps(skills)})
            return skills
        except Exception:
            return None

    def upload(self, file: UploadFile, user_id: int, title: str) -> Resume:
        if not file.filename or not file.filename.lower().endswith(".pdf"):
            raise HTTPException(400, detail="Only PDF files are allowed")

        upload_dir = Path(settings.UPLOAD_DIR)
        upload_dir.mkdir(parents=True, exist_ok=True)

        ext = Path(file.filename).suffix
        filename = f"{uuid.uuid4()}{ext}"
        file_path = str(upload_dir / filename)

        content = file.file.read()
        with open(file_path, "wb") as f:
            f.write(content)

        text = PdfExtractor.extract(file_path)
        resume = self.repo.create({
            "user_id": user_id,
            "title": title,
            "file_path": file_path,
            "extracted_text": text,
        })
        try: 
            self.extract_skills(resume.id)
        except Exception:
            pass

        return self.repo.get_by_id(resume.id)
