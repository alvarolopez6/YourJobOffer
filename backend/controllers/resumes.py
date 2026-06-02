from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlmodel import Session

from backend.db import get_db
from backend.services.resume_service import ResumeService
from backend.schemas.resume import ResumeResponse

router = APIRouter(prefix="/api/resumes", tags=["Resumes"])


def get_service(db: Session = Depends(get_db)) -> ResumeService:
    return ResumeService(db)


@router.get("/{resume_id}", response_model=ResumeResponse, status_code=200)
def get_resume(resume_id: int, svc: ResumeService = Depends(get_service)):
    resume = svc.get(resume_id)
    if not resume:
        raise HTTPException(404, detail="Resume not found")
    return resume


@router.post("/upload", response_model=ResumeResponse, status_code=201)
def upload_resume(
    file: UploadFile = File(...),
    user_id: int = Form(...),
    title: str = Form(...),
    svc: ResumeService = Depends(get_service),
):
    return svc.upload(file, user_id, title)
