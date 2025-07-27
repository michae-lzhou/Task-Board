# Libraries
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database import Base, engine, SessionLocal
from pydantic import BaseModel
import logging

# Local files
from exceptions import *
from crud import projects_crud as project, \
                 tasks_crud as task,       \
                 users_crud as user
import schemas
import models

# Set up basic logging for errors
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s - %(levelname)s - %(message)s")

app = FastAPI()

# Allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Hello from backend"}

models.Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Middleware that catches all unexpected exceptions (hopefully never needed!)
@app.middleware("http")
async def catch_exceptions_middleware(request: Request, call_next):
    try:
        response = await call_next(request)
        return response
    except Exception as e:
        logging.exception("Unhandled exception occurred")
        return JSONResponse(
            status_code=500,
            content={"detail": "An unexpected error occurred"},
        )

################################################################################
###                               Project                                    ###
################################################################################

# Create Project
# * Cannot have duplicate project names
# * Has a list of users associated with each project (not required on creation)
@app.post("/projects/", response_model=schemas.Project)
def create_project(project: schemas.ProjectCreate,
                   db: Session = Depends(get_db)):
    try:
        return project.create_project(db, project)
    except DuplicateProjectName as e:
        logging.warning(e.message)
        raise HTTPException(status_code=400, detail=e.message)

# Get Project by ID
# * Handle not found error
@app.get("/projects/{project_id}", response_model=schemas.Project)
def read_project(project_id = int, db: Session = Depends(get_db)):
    try:
        return project.get_project(db, project_id)
    except ProjectNotFound as e:
        logging.warning(e.message)
        raise HTTPException(status_code=404, detail=e.message)

# Add Member to Project
# * Handle not found error
# * Creates a new user if the user doesn't exist already
# * Cannot have duplicate user email here either
# * Friendly message if user is already in the project
@app.post("/projects/{project_id}/add-member")
def add_member(project_id: int, user: schemas.UserCreate, db: Session =
        Depends(get_db)):
    # Get the user's id from the name and email
    try:
        # The following line is purely to raise ProjectNotFound before
        # DuplicateUserEmail (makes more sense to me)
        project = project.get_project(db, project_id)
        curr_user = user.find_user_by_email(db, user.name, user.email)
        return project.add_user_to_project(db, project_id, curr_user.id)
    except ProjectNotFound as e:
        logging.warning(e.message)
        raise HTTPException(status_code=404, detail=e.message)
    except DuplicateUserEmail as e:
        logging.warning(e.message)
        raise HTTPException(status_code=400, detail=e.message)
    except UserInProject as e:
        logging.info(e.message)

# Get All Projects
@app.get("/projects/", response_model=list[schemas.Project])
def read_all_projects(db: Session = Depends(get_db)):
    return project.get_all_projects(db)

# Delete Project
# * Handle not found error
@app.delete("/projects/{project_id}")
def delete_project(project_id: int, db: Session = Depends(get_db)):
    try:
        project = project.delete_project(db, project_id)
        return {"message": f"Project {project_id} deleted"}
    except ProjectNotFound as e:
        logging.warning(e.message)
        raise HTTPException(status_code=404, detail=e.message)

################################################################################
###                                 Task                                     ###
################################################################################

# Create Task
# * Each task created should be fixed to the project the user is currently
#   viewing
# * Disallows task creation if there are no projects
# * Cannot have duplicate task names in the same project
# TODO: THIS SHOULD BE FIXED TO WHICHEVER PROJECT YOU ARE CURRENTLY VIEWING
# TODO: an extension of above: each tasks needs a project ID, so disallow any
# task creation if there are no projects (bullet proof the operations)
@app.post("/tasks/", response_model=schemas.Task)
def create_task(task: schemas.TaskCreate, db: Session = Depends(get_db)):
    try:
        return task.create_task(db, task)
    except ProjectNotFound as e:
        logging.warning(e.message)
        raise HTTPException(status_code=404, detail=e.message)
    except DuplicateTaskName as e:
        logging.warning(e.message)
        raise HTTPException(status_code=400, detail=e.message)

# Get Task by ID
# * Handle not found error
@app.get("/tasks/{task_id}", response_model=schemas.Task)
def read_task(task_id: int, db: Session = Depends(get_db)):
    try:
        return task.get_task(db, task_id)
    except TaskNotFound as e:
        logging.warning(e.message)
        raise HTTPException(status_code=404, detail=e.message)

# Get All Tasks for Project
# * Handle not found error
@app.get("/projects/{project_id}/tasks", response_model=list[schemas.Task])
def read_tasks_by_project(project_id: int, db: Session = Depends(get_db)):
    try:
        return task.get_tasks_by_project(db, project_id)
    except ProjectNotFound as e:
        logging.warning(e.message)
        raise HTTPException(status_code=404, detail=e.message)

# Update Task
# * Each task is fixed to a project and cannot be changed
# * Handle not found error
# * Can only assign to a current member in the project
# * Again, cannot update a task to have duplicate task name
@app.put("/tasks/{task_id}", response_model=schemas.Task)
def update_task(task_id: int, updated: schemas.TaskCreate, db: Session =
        Depends(get_db)):
    try:
        return task.update_task(db, task_id, updated)
    except (TaskNotFound, ProjectNotFound, UserNotFound) as e:
        logging.warning(e.message)
        raise HTTPException(status_code=404, detail=e.message)
    except (MovingTaskToNewProject, AssigneeNotMember, DuplicateTaskName) as e:
        logging.warning(e.message)
        raise HTTPException(status_code=400, detail=e.message)

# Delete Task
# * Handle not found error
@app.delete("/tasks/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db)):
    try:
        task = task.delete_task(db, task_id)
        return {"message": f"Task {task_id} deleted"}
    except TaskNotFound as e:
        logging.warning(e.message)
        raise HTTPException(status_code=404, detail=e.message)

################################################################################
###                                 User                                     ###
################################################################################

# Create User
# * Users can exist without being bound to a task or project
# * Cannot have duplicate user emails (allows duplicate names)
@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    try:
        return user.create_user(db, user)
    except DuplicateUserEmail as e:
        logging.warning(e.message)
        raise HTTPException(status_code=400, detail=e.message)

# Get User by ID
# * Handle not found error
@app.get("/users/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    try:
        return user.get_user(db, user_id)
    except UserNotFound as e:
        logging.warning(e.message)
        raise HTTPException(status_code=404, detail=e.message)

# Get All Users
@app.get("/users/", response_model=list[schemas.User])
def read_all_users(db: Session = Depends(get_db)):
    return user.get_all_users(db)

# Get All Users for Project
# * Handle not found error
@app.get("/projects/{project_id}/users", response_model=list[schemas.User])
def read_users_by_project(project_id: int, db: Session = Depends(get_db)):
    try:
        return user.get_users_by_project(db, project_id)
    except ProjectNotFound as e:
        logging.warning(e.message)
        raise HTTPException(status_code=404, detail=e.message)

# Update User - No need to update individual users

# Delete User
# * Handle not found error
@app.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    try:
        user = user.delete_user(db, user_id)
        return {"message": f"User {user_id} deleted"}
    except UserNotFound as e:
        logging.warning(e.message)
        raise HTTPException(status_code=404, detail=e.message)
