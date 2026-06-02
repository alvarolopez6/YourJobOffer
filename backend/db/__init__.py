from sqlmodel import Session, SQLModel, create_engine
from fastapi import Depends

from backend.config import settings

engine = create_engine(settings.DATABASE_URL)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


def get_db(session: Session = Depends(get_session)) -> Session:
    return session
