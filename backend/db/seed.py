from sqlmodel import Session, select

from backend.db.models.user import User


def seed_users(db: Session) -> None:
    existing = db.exec(select(User).limit(1)).first()
    if existing:
        return

    users = [
        User(email="alice@example.com", name="Alice Johnson"),
        User(email="bob@example.com", name="Bob Smith"),
        User(email="carol@example.com", name="Carol Martinez"),
    ]
    for user in users:
        db.add(user)
    db.commit()
