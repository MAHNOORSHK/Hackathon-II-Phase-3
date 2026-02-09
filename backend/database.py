from sqlmodel import create_engine, Session
from contextlib import contextmanager
from .models import SQLModel
import os


# Database setup
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://username:password@localhost/todo_db")
engine = create_engine(DATABASE_URL)


def create_db_and_tables():
    """
    Create database tables
    """
    SQLModel.metadata.create_all(engine)


@contextmanager
def get_session():
    """
    Get database session
    """
    with Session(engine) as session:
        yield session