from fastapi import APIRouter, Depends
from sqlmodel import Session

from backend.db import get_db
from backend.services.user_service import UserService
from backend.schemas.user import UserCreate, UserResponse

router = APIRouter(prefix="/api/users", tags=["Users"])


def get_service(db: Session = Depends(get_db)) -> UserService:
    return UserService(db)


@router.get("/", response_model=list[UserResponse], status_code=200)
def list_users(skip: int = 0, limit: int = 10,
               svc: UserService = Depends(get_service)):
    return svc.list(skip, limit)


@router.get("/{user_id}", response_model=UserResponse, status_code=200)
def get_user(user_id: int, svc: UserService = Depends(get_service)):
    return svc.get(user_id)


@router.post("/", response_model=UserResponse, status_code=201)
def create_user(payload: UserCreate, svc: UserService = Depends(get_service)):
    return svc.create(payload)


@router.delete("/{user_id}", status_code=204)
def delete_user(user_id: int, svc: UserService = Depends(get_service)):
    svc.delete(user_id)
