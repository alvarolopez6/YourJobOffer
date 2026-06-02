from fastapi import HTTPException
from sqlmodel import Session

from backend.repositories import UserRepository
from backend.schemas.user import UserCreate


class UserService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = UserRepository(db)

    def list(self, skip: int = 0, limit: int = 10) -> list:
        return self.repo.get_all(skip, limit)

    def get(self, user_id: int):
        user = self.repo.get_by_id(user_id)
        if not user:
            raise HTTPException(404, detail="User not found")
        return user

    def create(self, data: UserCreate):
        existing = self.repo.get_by_email(data.email)
        if existing:
            raise HTTPException(400, detail="Email already registered")
        return self.repo.create(data.model_dump())

    def delete(self, user_id: int) -> None:
        user = self.repo.get_by_id(user_id)
        if not user:
            raise HTTPException(404, detail="User not found")
        self.repo.delete(user)
