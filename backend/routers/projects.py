# routers/projects.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
import logging
# Local files
from exceptions import *
from crud import projects, users
import schemas

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create Project
# * Cannot have duplicate project names
# * Has a list of users associated with each project (not required on creation)
@router.post("/", response_model=schemas.Project)
def create_project(project: schemas.ProjectCreate,
                   db: Session = Depends(get_db)):
    try:
        return projects.create_project(db, project)
    except DuplicateProjectName as e:
        logging.warning(e.message)
        raise HTTPException(status_code=400, detail=e.message)

# Get Project by ID
# * Handle not found error
@router.get("/{project_id}", response_model=schemas.Project)
def read_project(project_id: int, db: Session = Depends(get_db)):
    try:
        return projects.get_project(db, project_id)
    except ProjectNotFound as e:
        logging.warning(e.message)
        raise HTTPException(status_code=404, detail=e.message)

# Add Member to Project
# * Handle not found error
# * Creates a new user if the user doesn't exist already
# * Cannot have duplicate user email here either
# * Friendly message if user is already in the project
@router.post("/{project_id}/add-member", response_model=schemas.User)
def add_member(project_id: int, user: schemas.UserCreate, db: Session = Depends(get_db)):
    # Get the user's id from the name and email
    try:
        # The following line is purely to raise ProjectNotFound before
        # DuplicateUserEmail (makes more sense to me)
        project = projects.get_project(db, project_id)
        curr_user = users.find_user_by_email(db, user.name, user.email)
        return projects.add_user_to_project(db, project_id, curr_user.id)
    except (UserNotFound, ProjectNotFound) as e:
        logging.warning(e.message)
        raise HTTPException(status_code=404, detail=e.message)
    except DuplicateUserEmail as e:
        logging.warning(e.message)
        raise HTTPException(status_code=400, detail=e.message)
    except UserInProject as e:
        logging.info(e.message)
        raise HTTPException(status_code=400, detail=e.message)

# Remove Member from Project
# * Handle not found error
# * Raise error if user is not in the project
@router.post("/{project_id}/remove-member", response_model=schemas.User)
def remove_member(project_id: int, user: schemas.UserCreate, db: Session = Depends(get_db)):
    try:
        project = projects.get_project(db, project_id)
        user = users.find_user_by_email(db, user.name, user.email)
        return projects.remove_user_from_project(db, project_id, user.id)
    except (UserNotFound, ProjectNotFound) as e:
        logging.warning(e.message)
        raise HTTPException(status_code=404, detail=e.message)
    except UserNotInProject as e:
        logging.info(e.message)
        raise HTTPException(status_code=400, detail=e.message)

# Get All Projects
@router.get("/", response_model=list[schemas.Project])
def read_all_projects(db: Session = Depends(get_db)):
    return projects.get_all_projects(db)

# Delete Project
# * Handle not found error
@router.delete("/{project_id}")
def delete_project(project_id: int, db: Session = Depends(get_db)):
    try:
        project = projects.delete_project(db, project_id)
        return {"message": f"Project [{project.name}] deleted"}
    except ProjectNotFound as e:
        logging.warning(e.message)
        raise HTTPException(status_code=404, detail=e.message)

# Get All Tasks for Project
# * Handle not found error
@router.get("/{project_id}/tasks", response_model=list[schemas.Task])
def read_tasks_by_project(project_id: int, db: Session = Depends(get_db)):
    try:
        from crud import tasks
        return tasks.get_tasks_by_project(db, project_id)
    except ProjectNotFound as e:
        logging.warning(e.message)
        raise HTTPException(status_code=404, detail=e.message)

# Get All Users for Project
# * Handle not found error
@router.get("/{project_id}/users", response_model=list[schemas.User])
def read_users_by_project(project_id: int, db: Session = Depends(get_db)):
    try:
        return users.get_users_by_project(db, project_id)
    except ProjectNotFound as e:
        logging.warning(e.message)
        raise HTTPException(status_code=404, detail=e.message)

