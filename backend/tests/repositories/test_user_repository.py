import pytest
from backend.repositories.user_repository import UserRepository
from backend.db.models.user import User


class TestUserRepository:

    def test_create(self, db_session):
        repo = UserRepository(db_session)
        user = repo.create({"email": "repo@test.com", "name": "Repo User"})
        assert user.id is not None
        assert user.email == "repo@test.com"

    def test_get_by_id(self, db_session, sample_user):
        repo = UserRepository(db_session)
        result = repo.get_by_id(sample_user.id)
        assert result is not None
        assert result.email == "test@example.com"

    def test_get_by_id_not_found(self, db_session):
        repo = UserRepository(db_session)
        assert repo.get_by_id(9999) is None

    def test_get_by_email(self, db_session, sample_user):
        repo = UserRepository(db_session)
        result = repo.get_by_email("test@example.com")
        assert result is not None
        assert result.id == sample_user.id

    def test_get_by_email_not_found(self, db_session):
        repo = UserRepository(db_session)
        assert repo.get_by_email("nonexistent@test.com") is None

    def test_get_all(self, db_session):
        repo = UserRepository(db_session)
        repo.create({"email": "a@test.com", "name": "A"})
        repo.create({"email": "b@test.com", "name": "B"})
        result = repo.get_all()
        assert len(result) == 2

    def test_get_all_pagination(self, db_session):
        repo = UserRepository(db_session)
        for i in range(5):
            repo.create({"email": f"u{i}@test.com", "name": f"U{i}"})
        result = repo.get_all(skip=0, limit=2)
        assert len(result) == 2
        result = repo.get_all(skip=4, limit=10)
        assert len(result) == 1

    def test_delete(self, db_session, sample_user):
        repo = UserRepository(db_session)
        repo.delete(sample_user)
        assert repo.get_by_id(sample_user.id) is None
