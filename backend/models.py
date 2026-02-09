from sqlmodel import SQLModel, Field, create_engine, Session
from datetime import datetime
from typing import Optional
import os


class Task(SQLModel, table=True):
    """
    Task model representing a user's task
    """
    user_id: str = Field(index=True)
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    description: Optional[str] = None
    completed: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class Conversation(SQLModel, table=True):
    """
    Conversation model representing a conversation thread
    """
    user_id: str = Field(index=True)
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class Message(SQLModel, table=True):
    """
    Message model representing a message in a conversation
    """
    user_id: str = Field(index=True)
    id: Optional[int] = Field(default=None, primary_key=True)
    conversation_id: int = Field(foreign_key="conversation.id")
    role: str = Field(regex="^(user|assistant)$")  # "user" or "assistant"
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow)


# Database setup
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://username:password@localhost/todo_db")
engine = create_engine(DATABASE_URL)


def create_db_and_tables():
    """
    Create database tables
    """
    SQLModel.metadata.create_all(engine)


def get_session():
    """
    Get database session
    """
    with Session(engine) as session:
        yield session