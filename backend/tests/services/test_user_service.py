import pytest
from unittest.mock import MagicMock
from fastapi import HTTPException

from backend.services.user_service import UserService
from backend.schemas.user import UserCreate
from backend.db.models.user import User


class TestUserService:

    def test_list_users(self, db_session):
        user1 = User(email="a@test.com", name="A")
        user2 = User(email="b@test.com", name="B")
        db_session.add_all([user1, user2])
        db_session.commit()

        svc = UserService(db_session)
        result = svc.list()
        assert len(result) == 2

    def test_list_users_pagination(self, db_session):
        users = [User(email=f"u{i}@test.com", name=f"U{i}") for i in range(5)]
        db_session.add_all(users)
        db_session.commit()

        svc = UserService(db_session)
        result = svc.list(skip=0, limit=2)
        assert len(result) == 2
        result = svc.list(skip=2, limit=2)
        assert len(result) == 2

    def test_get_user_found(self, db_session, sample_user):
        svc = UserService(db_session)
        result = svc.get(sample_user.id)
        assert result.id == sample_user.id
        assert result.email == "test@example.com"

    def test_get_user_not_found(self, db_session):
        svc = UserService(db_session)
        with pytest.raises(HTTPException) as exc_info:
            svc.get(9999)
        assert exc_info.value.status_code == 404

    def test_create_user(self, db_session):
        svc = UserService(db_session)
        data = UserCreate(email="new@test.com", name="New User")
        result = svc.create(data)
        assert result.email == "new@test.com"
        assert result.name == "New User"
        assert result.id is not None

    def test_create_user_duplicate_email(self, db_session, sample_user):
        svc = UserService(db_session)
        data = UserCreate(email="test@example.com", name="Another")
        with pytest.raises(HTTPException) as exc_info:
            svc.create(data)
        assert exc_info.value.status_code == 400

    def test_delete_user(self, db_session, sample_user):
        svc = UserService(db_session)
        svc.delete(sample_user.id)
        with pytest.raises(HTTPException):
            svc.get(sample_user.id)

    def test_delete_user_not_found(self, db_session):
        svc = UserService(db_session)
        with pytest.raises(HTTPException) as exc_info:
            svc.delete(9999)
        assert exc_info.value.status_code == 404
