from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from src.database.database import Base


def lazy_relationship(*args, **kwargs):
    return relationship(*args, uselist=True, **kwargs)


class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, index=True, unique=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    name = Column(String(16), unique=True, index=True)

    account = lazy_relationship("UserAccount", back_populates="user")


class UserAccount(Base):
    __tablename__ = "accounts"

    id = Column(String(36), primary_key=True, index=True, unique=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    username = Column(String(16), unique=True, index=True)
    password = Column(String(256))

    user_id = Column(String(36), ForeignKey("users.id"))
    user = lazy_relationship("User", back_populates="account")
