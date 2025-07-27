# Libraries
from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional, List
from enum import Enum

# Fixed itask status
class TaskStatus(str, Enum):
    todo = "todo"
    in_progress = "in-progress"
    done = "done"

# User Schemas
class UserBase(BaseModel):
    name: str
    email: EmailStr

    @field_validator('email')
    @classmethod
    def lowercase_email(cls, v):
        return v.lower()

class UserCreate(UserBase):
    pass

class User(UserBase):
    id: int

    model_config = {
        "from_attributes": True
    }

# Project Schemas
class ProjectBase(BaseModel):
    name: str

class ProjectCreate(ProjectBase):
    pass

class Project(ProjectBase):
    id: int
    members: List[User] = []

    model_config = {
        "from_attributes": True
    }

# Task Schemas
class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    status: TaskStatus = TaskStatus.todo
    project_id: int
    assigned_to: Optional[int] = None

class TaskCreate(TaskBase):
    pass

class Task(TaskBase):
    id: int
    project: Project = None
    assigned_user: Optional[User] = None

    model_config = {
        "from_attributes": True
    }

