################################################################################
# routers/users.py
# Purpose:  Defines the API routes for user-related operations using FastAPI.
#           Supports creating, retrieving, and deleting users, with validations
#           for unique emails and user existence. Integrates with 
#           WebSocketManager to emit real-time events on user creation and
#           deletion. Users can exist independently of projects or tasks.
################################################################################

# Libraries
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
import logging

# Local files
from ..exceptions import *
from ..database import SessionLocal
from ..crud import users
from .. import schemas
from ..websocket_utils import WebSocketManager, convert_to_dict

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create User
# * Users can exist without being bound to a task or project
# * Cannot have duplicate user emails (allows duplicate names)
@router.post("/", response_model=schemas.User)
async def create_user(user: schemas.UserCreate,
                      request: Request, db: Session = Depends(get_db)):
    try:
        new_user = users.create_user(db, user)
        
        # Emit WebSocket event
        ws_manager = WebSocketManager(request.app.state.sio)
        await ws_manager.emit_user_created(convert_to_dict(new_user))
        
        return new_user
    except DuplicateUserEmail as e:
        logging.warning(e.message)
        raise HTTPException(status_code=400, detail=e.message)

# Get User by ID
# * Handle not found error
@router.get("/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    try:
        return users.get_user(db, user_id)
    except UserNotFound as e:
        logging.warning(e.message)
        raise HTTPException(status_code=404, detail=e.message)

# Get All Users
@router.get("/", response_model=list[schemas.User])
def read_all_users(db: Session = Depends(get_db)):
    return users.get_all_users(db)

# Delete User
# * Handle not found error
@router.delete("/{user_id}")
async def delete_user(user_id: int, request: Request,
                      db: Session = Depends(get_db)):
    try:
        user = users.delete_user(db, user_id)
        
        # Emit WebSocket event
        ws_manager = WebSocketManager(request.app.state.sio)
        await ws_manager.emit_user_deleted(user_id, user.name)
        
        return {"message": f"User [{user.name}] deleted"}
    except UserNotFound as e:
        logging.warning(e.message)
        raise HTTPException(status_code=404, detail=e.message)
