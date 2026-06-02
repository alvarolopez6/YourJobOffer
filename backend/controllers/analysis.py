from fastapi import APIRouter, Depends
from sqlmodel import Session

from backend.db import get_db
from backend.services.analysis_service import AnalysisService
from backend.schemas.analysis import CompareRequest, MatchResultResponse

router = APIRouter(prefix="/api/analysis", tags=["Analysis"])


def get_service(db: Session = Depends(get_db)) -> AnalysisService:
    return AnalysisService(db)


@router.post("/compare", response_model=MatchResultResponse, status_code=201)
def compare(payload: CompareRequest, svc: AnalysisService = Depends(get_service)):
    return svc.compare(payload.user_id, payload.resume_id, payload.job_id)


@router.get("/matches", response_model=list[MatchResultResponse], status_code=200)
def list_matches(skip: int = 0, limit: int = 10,
                 svc: AnalysisService = Depends(get_service)):
    return svc.list_matches(skip, limit)
