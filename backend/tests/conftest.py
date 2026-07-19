import os
os.environ["DATABASE_URL"] = "sqlite://"

import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, Session, create_engine
from sqlmodel.pool import StaticPool

from backend.main import app
from backend.db import get_session
from backend.db.models.user import User
from backend.db.models.job import Job
from backend.db.models.resume import Resume
from backend.db.models.match_result import MatchResult


@pytest.fixture(name="engine")
def engine_fixture():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    yield engine
    SQLModel.metadata.drop_all(engine)


@pytest.fixture(name="db_session")
def db_session_fixture(engine):
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(engine):
    def override_session():
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_session] = override_session
    with TestClient(app, raise_server_exceptions=False) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture(name="sample_user")
def sample_user_fixture(db_session):
    user = User(email="test@example.com", name="Test User")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture(name="sample_job")
def sample_job_fixture(db_session):
    job = Job(
        title="Backend Developer",
        company="TechCorp",
        description="We need a Python developer with FastAPI experience.",
        skills_data='{"languages": ["python"], "frameworks": ["fastapi"]}',
    )
    db_session.add(job)
    db_session.commit()
    db_session.refresh(job)
    return job


@pytest.fixture(name="sample_resume")
def sample_resume_fixture(db_session, sample_user):
    resume = Resume(
        user_id=sample_user.id,
        title="My Resume",
        file_path="/tmp/test_resume.pdf",
        extracted_text="Python developer with FastAPI experience.",
        skills_data='{"languages": ["python"], "frameworks": ["fastapi"]}',
    )
    db_session.add(resume)
    db_session.commit()
    db_session.refresh(resume)
    return resume


@pytest.fixture(name="sample_match")
def sample_match_fixture(db_session, sample_user, sample_resume, sample_job):
    import json
    match = MatchResult(
        user_id=sample_user.id,
        resume_id=sample_resume.id,
        job_id=sample_job.id,
        match_score=100.0,
        matched_skills=json.dumps(["python", "fastapi"]),
        missing_skills=json.dumps([]),
    )
    db_session.add(match)
    db_session.commit()
    db_session.refresh(match)
    return match
