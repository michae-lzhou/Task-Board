################################################################################
# crud/projects.py
# Purpose:  Implements CRUD operations for the Project model using SQLAlchemy.
#           Functions include creating, reading, adding/removing users, and
#           deleting projects. All operations are performed using project IDs to
#           ensure consistent and reliable access to records in the event of
#           database corruption.
################################################################################

# Libraries
from sqlalchemy.orm import Session

# Local files
from ..models import Project, User, Task
from ..schemas import ProjectCreate
from ..exceptions import *

################################################################################
###                                 Project                                  ###
################################################################################
# Create
def create_project(db: Session, project: ProjectCreate):
    # Handling duplicate names
    dupe = db.query(Project).filter(
                Project.name == project.name
           ).first()
    if dupe:
        raise DuplicateProjectName(project.name)

    db_project = Project(**project.model_dump())
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project

# Read
def get_project(db: Session, project_id: int):
    project = db.query(Project).filter(
                    Project.id == project_id
              ).first()
    if not project:
        raise ProjectNotFound(project_id)
    return project

def get_all_projects(db: Session):
    projects = db.query(Project).all()
    return projects

# Update
def add_user_to_project(db: Session, project_id: int, user_id: int):
    project = db.query(Project).filter(
                    Project.id == project_id
              ).first()
    user = db.query(User).filter(
                User.id == user_id
           ).first()

    # Ensure the project and the user exists
    if not project:
        raise ProjectNotFound(project_id)
    if not user:
        raise UserNotFound(user_id)

    if user not in project.members:
        project.members.append(user)
        db.commit()
        db.refresh(project)
        db.refresh(user)
    else:
        raise UserInProject(user.name, project.name)

    return user

def remove_user_from_project(db: Session, project_id: int, user_id: int):
    project = db.query(Project).filter(
                    Project.id == project_id
              ).first()
    user = db.query(User).filter(
                User.id == user_id
           ).first()

    # Ensure the project and the user exists
    if not project:
        raise ProjectNotFound(project_id)
    if not user:
        raise UserNotFound(user_id)

    if user in project.members:
        project.members.remove(user)

        # Find tasks in this project assigned to the user and reassign to NULL
        tasks = db.query(Task).filter(
                    Task.project_id == project_id,
                    Task.assigned_to == user_id
                ).all()

        for task in tasks:
            task.assigned_to = None
            task.assigned_user = None

        db.commit()
        db.refresh(project)
        db.refresh(user)  # Add this line
    else:
        raise UserNotInProject(user.name, project.name)

    return user


# Delete
def delete_project(db: Session, project_id: int):
    db_project = get_project(db, project_id)
    if not db_project:
        raise ProjectNotFound(project_id)
    db.delete(db_project)
    db.commit()
    return db_project
