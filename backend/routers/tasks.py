# routers/tasks.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
import logging
# Local files
from exceptions import *
from crud import tasks
import schemas

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create Task
# * Each task created should be fixed to the project the user is currently
#   viewing
# * Disallows task creation if there are no projects
# * Cannot have duplicate task names in the same project
# TODO: THIS SHOULD BE FIXED TO WHICHEVER PROJECT YOU ARE CURRENTLY VIEWING
# TODO: an extension of above: each tasks needs a project ID, so disallow any
# task creation if there are no projects (bullet proof the operations)
@router.post("/", response_model=schemas.Task)
def create_task(task: schemas.TaskCreate, db: Session = Depends(get_db)):
    try:
        return tasks.create_task(db, task)
    except ProjectNotFound as e:
        logging.warning(e.message)
        raise HTTPException(status_code=404, detail=e.message)
    except DuplicateTaskName as e:
        logging.warning(e.message)
        raise HTTPException(status_code=400, detail=e.message)

# Get Task by ID
# * Handle not found error
@router.get("/{task_id}", response_model=schemas.Task)
def read_task(task_id: int, db: Session = Depends(get_db)):
    try:
        return tasks.get_task(db, task_id)
    except TaskNotFound as e:
        logging.warning(e.message)
        raise HTTPException(status_code=404, detail=e.message)

# Update Task
# * Each task is fixed to a project and cannot be changed
# * Handle not found error
# * Can only assign to a current member in the project
# * Again, cannot update a task to have duplicate task name
@router.put("/{task_id}", response_model=schemas.Task)
def update_task(task_id: int, updated: schemas.TaskCreate, db: Session = Depends(get_db)):
    try:
        return tasks.update_task(db, task_id, updated)
    except (TaskNotFound, ProjectNotFound, UserNotFound) as e:
        logging.warning(e.message)
        raise HTTPException(status_code=404, detail=e.message)
    except (MovingTaskToNewProject, AssigneeNotMember, DuplicateTaskName) as e:
        logging.warning(e.message)
        raise HTTPException(status_code=400, detail=e.message)

# Delete Task
# * Handle not found error
@router.delete("/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db)):
    try:
        task = tasks.delete_task(db, task_id)
        return {"message": f"Task [{task.title}] deleted"}
    except TaskNotFound as e:
        logging.warning(e.message)
        raise HTTPException(status_code=404, detail=e.message)
