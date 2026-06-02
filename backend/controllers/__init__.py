from backend.controllers.analysis import router as analysis_router
from backend.controllers.job_offers import router as job_offers_router
from backend.controllers.resumes import router as resumes_router
from backend.controllers.users import router as users_router

__all__ = [
    "analysis_router",
    "job_offers_router",
    "resumes_router",
    "users_router",
]
