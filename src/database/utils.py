from sqlalchemy.orm import Session

from src.crud.user import create_user
from src.database.database import SessionLocal


def add_test_data():
    db: Session = SessionLocal()
    create_user(db, "test-name", "test-username", "test-password", "test-user-id")


