from typing import Type

from sqlalchemy.orm import Session
from ulid import ULID

from src.database import models
from src.utils.credentials import hash_password
from src.utils.handler import handle_error, handle_none_value


@handle_none_value("User")
@handle_error
def get_user_by_id(db: Session, user_id: str) -> Type[models.User] | models.User | None:
    user = db.query(models.User).filter_by(id=user_id).first()
    return user


@handle_error
def create_user(
        db: Session,
        name: str,
        username: str,
        password: str,
        user_id: str = str(ULID())
) -> Type[models.User] | models.User | None:
    user = models.User(
        id=user_id,
        name=name
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    account = models.UserAccount(
        id=str(ULID()),
        username=username,
        password=hash_password(password),
        user_id=user.id
    )
    db.add(account)
    db.commit()
    db.refresh(account)
    db.refresh(user)

    return user
