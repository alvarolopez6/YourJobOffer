from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI
from sqlmodel import Session

from backend.config import settings
from backend.db import engine, create_db_and_tables
from backend.db.seed import seed_users

from backend.controllers import analysis, job_offers, resumes, users


@asynccontextmanager
async def lifespan(app: FastAPI):
    Path(settings.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
    create_db_and_tables()
    with Session(engine) as session:
        seed_users(session)
    yield


app = FastAPI(title=settings.APP_NAME, debug=settings.DEBUG, lifespan=lifespan)

app.include_router(analysis.router)
app.include_router(users.router)
app.include_router(job_offers.router)
app.include_router(resumes.router)


@app.get("/health")
async def health():
    return {"status": "ok"}
