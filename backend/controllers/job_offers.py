from fastapi import APIRouter, Depends, Form, HTTPException
from sqlmodel import Session

from backend.db import get_db
from backend.services.job_service import JobService
from backend.schemas.job import JobResponse

router = APIRouter(prefix="/api/jobs", tags=["Jobs"])


def get_service(db: Session = Depends(get_db)) -> JobService:
    return JobService(db)


@router.get("/", response_model=list[JobResponse], status_code=200)
def list_jobs(skip: int = 0, limit: int = 10,
              svc: JobService = Depends(get_service)):
    return svc.list(skip, limit)


@router.get("/{job_id}", response_model=JobResponse, status_code=200)
def get_job(job_id: int, svc: JobService = Depends(get_service)):
    job = svc.get(job_id)
    if not job:
        raise HTTPException(404, detail="Job not found")
    return job


@router.post("/", response_model=JobResponse, status_code=201)
def create_job(
    title: str = Form(None),
    company: str = Form(None),
    description: str = Form(...),
    url: str = Form(None),
    location: str = Form(None),
    svc: JobService = Depends(get_service),
):
    data = {
        "title": title,
        "company": company,
        "description": description,
        "url": url,
        "location": location,
    }
    return svc.create(data)


@router.put("/{job_id}", response_model=JobResponse, status_code=200)
def update_job(
    job_id: int,
    title: str = Form(None),
    company: str = Form(None),
    description: str = Form(None),
    url: str = Form(None),
    location: str = Form(None),
    svc: JobService = Depends(get_service),
):
    data = {}
    if title is not None: data["title"] = title
    if company is not None: data["company"] = company
    if description is not None: data["description"] = description
    if url is not None: data["url"] = url
    if location is not None: data["location"] = location
    job = svc.update(job_id, data)
    if not job:
        raise HTTPException(404, detail="Job not found")
    return job


@router.delete("/{job_id}", status_code=204)
def delete_job(job_id: int, svc: JobService = Depends(get_service)):
    if not svc.delete(job_id):
        raise HTTPException(404, detail="Job not found")
