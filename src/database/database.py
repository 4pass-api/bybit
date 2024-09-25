import os

from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DB_HOST = os.getenv("DB_HOST", "mysql")
DB_USER = os.getenv("DB_USER", "admin")
DB_PASS = os.getenv("DB_PASS", "admin1234")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_NAME = os.getenv("DB_NAME", "template_db")


def get_database_url(user, password, host, port, db_name=None):
    base_url = f"mysql+pymysql://{user}:{password}@{host}:{port}"
    return f"{base_url}/{db_name}?charset=utf8mb4" if db_name else base_url


def drop_database(url, db_name):
    try:
        with create_engine(url).connect() as connection:
            connection.execute(text(f"DROP DATABASE IF EXISTS {db_name}"))
    except OperationalError as e:
        print(f"Error dropping database: {e}")


# Function to create database if it does not exist
def create_database_if_not_exists(url, db_name):
    try:
        with create_engine(url).connect() as connection:
            connection.execute(text(f"CREATE DATABASE IF NOT EXISTS {db_name}"))
    except OperationalError as e:
        print(f"Error creating database: {e}")


def drop_all_tables(_engine=None):
    try:
        Base.metadata.drop_all(bind=_engine)
        print("All tables dropped successfully.")
    except OperationalError as e:
        print(f"Error dropping tables: {e}")


# Function to create all tables
def create_all_tables(_engine=None):
    try:
        Base.metadata.create_all(bind=_engine)
        print("All tables created successfully.")
    except OperationalError as e:
        print(f"Error creating tables: {e}")


# Construct URLs
TRIAL_URL = get_database_url(DB_USER, DB_PASS, DB_HOST, DB_PORT)
SQLALCHEMY_DATABASE_URL = get_database_url(DB_USER, DB_PASS, DB_HOST, DB_PORT, DB_NAME)

# Create the database if it doesn't exist
create_database_if_not_exists(TRIAL_URL, DB_NAME)

# Create engine with connection pooling options
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=1800,
    pool_size=20,  # Adjust pool size as needed
    max_overflow=10  # Adjust as needed
)

# Create a configured "Session" class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create a base class for declarative models
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
