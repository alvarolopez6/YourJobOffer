# AI Job Analyzer

Match job offers against CVs using AI-powered skill extraction.

## Overview

The system extracts skills from job descriptions and PDF resumes using a HuggingFace NER model (`feliponi/hirly-ner-multi`), then compares them to calculate a match score, matched skills, and missing skills.

### Architecture

```
backend/
├── controllers/     # FastAPI route handlers
│   ├── analysis.py  # POST /api/analysis/compare, GET /api/analysis/matches
│   ├── users.py     # CRUD /api/users
│   ├── job_offers.py# CRUD /api/jobs
│   └── resumes.py   # POST /api/resumes/upload, GET /api/resumes/{id}
├── services/        # Business logic (JobService, ResumeService, AnalysisService, UserService)
├── utils/           # Utilities (PdfExtractor, SkillExtractor, MatchEngine)
├── repositories/    # Database access layer
├── schemas/         # Pydantic request/response models
├── db/
│   ├── models/      # SQLModel table definitions
│   ├── seed.py      # Seed data (3 default users)
│   └── __init__.py  # Engine, session, table creation
├── data/
│   └── skill_taxonomy.py  # Skill categorization taxonomy
├── config.py        # Pydantic Settings
└── main.py          # FastAPI app, lifespan, router registration
```

### Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check |
| **Users** | | |
| GET | `/api/users/` | List users (paginated) |
| GET | `/api/users/{id}` | Get user by ID |
| POST | `/api/users/` | Create user |
| DELETE | `/api/users/{id}` | Delete user |
| **Jobs** | | |
| GET | `/api/jobs/` | List jobs (paginated) |
| GET | `/api/jobs/{id}` | Get job by ID |
| POST | `/api/jobs/` | Create job (auto-extracts skills) |
| PUT | `/api/jobs/{id}` | Update job |
| DELETE | `/api/jobs/{id}` | Delete job |
| **Resumes** | | |
| GET | `/api/resumes/{id}` | Get resume by ID |
| POST | `/api/resumes/upload` | Upload PDF resume (auto-extracts text + skills) |
| **Analysis** | | |
| POST | `/api/analysis/compare` | Compare resume vs job (creates match result) |
| GET | `/api/analysis/matches` | List all match results |

### Data flow

1. **Job creation**: A job offer is created via `POST /api/jobs/`. The service automatically extracts skills from the description using the NER model and caches them in `skills_data`.
2. **Resume upload**: A PDF is uploaded via `POST /api/resumes/upload`. The text is extracted with pypdf, then skills are extracted via the NER model and cached in `skills_data`.
3. **Comparison**: `POST /api/analysis/compare` loads the cached skills from both the job and resume, runs them through the `MatchEngine` (exact string comparison, case-insensitive), and persists the result.
4. **Match result** includes: score (0-100%), matched skills, missing skills.

## Prerequisites

- [Docker](https://docs.docker.com/engine/install/) + [Docker Compose](https://docs.docker.com/compose/install/)
- Or Python 3.12+ with PostgreSQL 16

## Quick start (Docker)

```bash
# Clone and enter the project
git clone <repo-url> && cd yourjoboffer

# Start both services
docker compose up --build
```

The API will be available at `http://localhost:8000`.

When the backend starts for the first time, it:
1. Creates all database tables
2. Seeds 3 default users (Alice, Bob, Carol)

### Verify it's running

```bash
curl http://localhost:8000/health
# {"status":"ok"}

curl http://localhost:8000/api/users/
# [{"id":1,"email":"alice@example.com","name":"Alice Johnson",...}, ...]
```

## Local development (without Docker)

### 1. Start PostgreSQL

```bash
# Using Docker just for the database
docker run -d --name yjo-postgres \
  -e POSTGRES_USER=user \
  -e POSTGRES_PASSWORD=pass \
  -e POSTGRES_DB=ai_job_analyzer \
  -p 5432:5432 \
  postgres:16-alpine
```

### 2. Set up Python environment

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Run the server

```bash
uvicorn backend.main:app --reload
```

The `.env` file at the project root is automatically read by `config.py` and provides the `DATABASE_URL`.

## Configuration

All settings are managed via `backend/config.py` and can be overridden through environment variables or `.env` file:

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `postgresql+psycopg2://user:pass@localhost:5432/ai_job_analyzer` | PostgreSQL connection string |
| `UPLOAD_DIR` | `uploads` | Directory for uploaded PDF files |
| `APP_NAME` | `AI Job Analyzer` | Application name |
| `DEBUG` | `True` | Enable debug mode |

## API examples

### Create a job

```bash
curl -X POST http://localhost:8000/api/jobs/ \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Python Backend Developer",
    "company": "TechCorp",
    "description": "We are looking for a Python developer with experience in Django, PostgreSQL, and AWS."
  }'
```

### Upload a resume

```bash
curl -X POST http://localhost:8000/api/resumes/upload \
  -F "file=@resume.pdf" \
  -F "user_id=1" \
  -F "title="Senior Python Developer"
```

### Compare resume vs job

```bash
curl -X POST http://localhost:8000/api/analysis/compare \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1,
    "resume_id": 1,
    "job_id": 1
  }'
# Response:
# {
#   "match_score": 66.67,
#   "matched_skills": ["python", "django"],
#   "missing_skills": ["aws", "postgresql"],
#   ...
# }
```

## Project status

- Backend API: complete
- NER skill extraction: operational (model: `feliponi/hirly-ner-multi`)
- Match engine: exact comparison (case-insensitive)
- Frontend: not started
- Tests: not written
