from pydantic import BaseModel
from typing import List


class TaskInfo(BaseModel):
    task_id: int
    status: str
    title: str


class AddTaskResult(BaseModel):
    task_id: int
    status: str
    title: str


class TaskListResult(BaseModel):
    tasks: List[TaskInfo]


class TaskOperationResult(BaseModel):
    task_id: int
    status: str
    title: str