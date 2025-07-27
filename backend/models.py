# Libraries
from sqlalchemy import Column, Integer, String, Enum, ForeignKey, Table
from sqlalchemy.orm import relationship
from database import Base
import enum

# Association table for many-to-many Project <-> User
project_members = Table(
    "project_members",
    Base.metadata,
    Column("project_id", ForeignKey("projects.id"), primary_key=True),
    Column("user_id", ForeignKey("users.id"), primary_key=True)
)

# Enum for task status
class TaskStatus(str, enum.Enum):
    todo = "todo"
    in_progress = "in-progress"
    done = "done"

# Project table
class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)

    # Link to tasks
    tasks = relationship("Task", back_populates="project", cascade="all, delete")

    # Many-to-many relationship to users
    members = relationship("User", secondary=project_members,
        back_populates="projects")

# Task table
class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String, nullable=True)
    status = Column(Enum(TaskStatus), default=TaskStatus.todo)

    # Foreign keys
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    assigned_to = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    # Relationships
    project = relationship("Project", back_populates="tasks")
    assigned_user = relationship("User")

# User/team member table
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)

    # Many-to-many relationship to projects
    projects = relationship("Project", secondary=project_members,
            back_populates="members")
