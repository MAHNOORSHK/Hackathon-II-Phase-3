from sqlmodel import select
from typing import List, Optional
from datetime import datetime
from ..database import get_session
from ..models import Task
from .types import TaskInfo, AddTaskResult, TaskOperationResult


async def add_task_db(user_id: str, title: str, description: Optional[str] = None) -> AddTaskResult:
    """Add a new task to the database"""
    from ..database import engine
    from sqlmodel import Session
    
    with Session(engine) as session:
        task = Task(
            user_id=user_id,
            title=title,
            description=description,
            completed=False,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        session.add(task)
        session.commit()
        session.refresh(task)
        
        return AddTaskResult(
            task_id=task.id,
            status="created" if not task.completed else "completed",
            title=task.title
        )


async def list_tasks_db(user_id: str, status: Optional[str] = None) -> List[TaskInfo]:
    """List tasks for a user with optional status filter"""
    from ..database import engine
    from sqlmodel import Session
    
    with Session(engine) as session:
        query = select(Task).where(Task.user_id == user_id)
        
        if status:
            if status.lower() == "completed":
                query = query.where(Task.completed == True)
            elif status.lower() == "active":
                query = query.where(Task.completed == False)
        
        tasks = session.exec(query).all()
        
        results = []
        for task in tasks:
            results.append(
                TaskInfo(
                    task_id=task.id,
                    status="completed" if task.completed else "active",
                    title=task.title
                )
            )
        
        return results


async def complete_task_db(user_id: str, task_id: int) -> TaskOperationResult:
    """Mark a task as completed"""
    from ..database import engine
    from sqlmodel import Session
    
    with Session(engine) as session:
        task = session.get(Task, task_id)
        
        if not task or task.user_id != user_id:
            raise ValueError(f"Task with ID {task_id} not found or does not belong to user {user_id}")
        
        task.completed = True
        task.updated_at = datetime.utcnow()
        session.add(task)
        session.commit()
        session.refresh(task)
        
        return TaskOperationResult(
            task_id=task.id,
            status="completed",
            title=task.title
        )


async def delete_task_db(user_id: str, task_id: int) -> TaskOperationResult:
    """Delete a task from the database"""
    from ..database import engine
    from sqlmodel import Session
    
    with Session(engine) as session:
        task = session.get(Task, task_id)
        
        if not task or task.user_id != user_id:
            raise ValueError(f"Task with ID {task_id} not found or does not belong to user {user_id}")
        
        title = task.title
        session.delete(task)
        session.commit()
        
        return TaskOperationResult(
            task_id=task.id,
            status="deleted",
            title=title
        )


async def update_task_db(user_id: str, task_id: int, title: Optional[str] = None, description: Optional[str] = None) -> TaskOperationResult:
    """Update task details"""
    from ..database import engine
    from sqlmodel import Session
    
    with Session(engine) as session:
        task = session.get(Task, task_id)
        
        if not task or task.user_id != user_id:
            raise ValueError(f"Task with ID {task_id} not found or does not belong to user {user_id}")
        
        if title is not None:
            task.title = title
        if description is not None:
            task.description = description
        
        task.updated_at = datetime.utcnow()
        session.add(task)
        session.commit()
        session.refresh(task)
        
        return TaskOperationResult(
            task_id=task.id,
            status="completed" if task.completed else "active",
            title=task.title
        )