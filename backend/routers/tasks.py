################################################################################
# routers/tasks.py
# Purpose:  Defines the API routes for task-related operations using FastAPI.
#           Includes endpoints to create, read, update, and delete tasks within
#           projects. Handles project and user validation, duplicate prevention,
#           and assignment rules. Integrates with WebSocketManager to emit real-
#           time task events, and raises meaningful HTTP exceptions for errors.
################################################################################

# Libraries
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from database import SessionLocal
import logging

# Local files
from exceptions import *
from crud import tasks
import schemas
from websocket_utils import WebSocketManager, convert_to_dict

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
@router.post("/", response_model=schemas.Task)
async def create_task(task: schemas.TaskCreate,
                      request: Request, db: Session = Depends(get_db)):
    try:
        new_task = tasks.create_task(db, task)
        
        # Emit WebSocket event
        ws_manager = WebSocketManager(request.app.state.sio)
        await ws_manager.emit_task_created(convert_to_dict(new_task))
        
        return new_task
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
async def update_task(task_id: int, updated: schemas.TaskCreate,
                      request: Request, db: Session = Depends(get_db)):
    try:
        updated_task = tasks.update_task(db, task_id, updated)
        
        # Emit WebSocket event
        ws_manager = WebSocketManager(request.app.state.sio)
        await ws_manager.emit_task_updated(convert_to_dict(updated_task))
        
        return updated_task
    except (TaskNotFound, ProjectNotFound, UserNotFound) as e:
        logging.warning(e.message)
        raise HTTPException(status_code=404, detail=e.message)
    except (MovingTaskToNewProject, AssigneeNotMember, DuplicateTaskName) as e:
        logging.warning(e.message)
        raise HTTPException(status_code=400, detail=e.message)

# Delete Task
# * Handle not found error
@router.delete("/{task_id}")
async def delete_task(task_id: int, request: Request,
                      db: Session = Depends(get_db)):
    try:
        task = tasks.delete_task(db, task_id)
        
        # Emit WebSocket event
        ws_manager = WebSocketManager(request.app.state.sio)
        await ws_manager.emit_task_deleted(task_id, task.title)
        
        return {"message": f"Task [{task.title}] deleted"}
    except TaskNotFound as e:
        logging.warning(e.message)
        raise HTTPException(status_code=404, detail=e.message)
