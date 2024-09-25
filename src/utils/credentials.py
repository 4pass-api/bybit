from datetime import datetime, timedelta, timezone
from typing import Annotated
from typing import Type

from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from src.database import models
from src.database.database import get_db
from src.utils.handler import handle_jwt_error, handle_error, handle_none_value

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = "c1b3e4b3-4b3c-4b3e-8b3c-4b3e4b3c4b3e"
ALGORITHM = "HS256"
EXPIRE_IN_MIN = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


@handle_none_value("User")
@handle_error
def get_user_by_username(db: Session, username: str) -> Type[models.User] | models.User | None:
    user = db.query(models.User).join(models.UserAccount).filter_by(username=username).first()
    return user


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def authenticate_user(db: Session, username: str, password: str) -> models.User:
    user = get_user_by_username(db, username)
    truth_password = user.account[0].password
    if not verify_password(password, truth_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    return user


def create_access_token(data: dict, period=timedelta(minutes=EXPIRE_IN_MIN)) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + period
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt


@handle_jwt_error
def decode_token(token: str) -> dict:
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])


async def get_current_user(
        token: Annotated[str, Depends(oauth2_scheme)],
        db: Session = Depends(get_db)
) -> models.User:
    payload = decode_token(token)
    username: str = payload.get("sub")
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Could not validate credentials (username) not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = get_user_by_username(db, username)

    return user
