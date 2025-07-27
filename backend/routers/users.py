# routers/users.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
import logging
# Local files
from exceptions import *
from crud import users
import schemas

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
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    try:
        return users.create_user(db, user)
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
def delete_user(user_id: int, db: Session = Depends(get_db)):
    try:
        user = users.delete_user(db, user_id)
        return {"message": f"User [{user.name}] deleted"}
    except UserNotFound as e:
        logging.warning(e.message)
        raise HTTPException(status_code=404, detail=e.message)
