'''
NOTE: everything here is actually what happens in the database, main.py is more
logic and API endpoint flow + error handling

NOTE: all instances are accessed via their unique id here to avoid problems deep
into the code, other function figure out what the id is supposed to be from the
individual fields
'''
# Libraries
from sqlalchemy.orm import Session
from pydantic import EmailStr

# Local files
from models import Project, User, Task
from schemas import UserCreate
from exceptions import *

################################################################################
###                                  User                                    ###
################################################################################

# Create
def create_user(db: Session, user: UserCreate):
    # Handling duplicate names
    dupe = db.query(User).filter(
                User.email == user.email
           ).first()
    if dupe:
        raise DuplicateUserEmail(user.email)

    db_user = User(**user.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# Read
def get_user(db: Session, user_id: int):
    user = db.query(User).filter(
                User.id == user_id
           ).first()
    if not user:
        raise UserNotFound(user_id)
    return user

def get_all_users(db: Session):
    users = db.query(User).all()
    return users

def get_users_by_project(db: Session, project_id: int):
    project = db.query(Project).filter(
                    Project.id == project_id
              ).first()
    if not project:
        raise ProjectNotFound(project_id)
    return project.members

# Update - No need to update user information

# Search
def find_user_by_email(db: Session, name: str, email: EmailStr):
    user = db.query(User).filter(
                User.email == email.lower(),
                User.name == name
           ).first()
    # Force create a new user here
    if not user:
        new_user_data = UserCreate(name=name, email=email)
        user = create_user(db, new_user_data)

    return user

# Delete
def delete_user(db: Session, user_id: int):
    db_user = get_user(db, user_id)
    if not db_user:
        raise UserNotFound(user_id)

    # Update all tasks assigned to this user to have assigned_to = None
    db.query(Task).filter(Task.assigned_to == user_id).update({"assigned_to": None})

    db.delete(db_user)
    db.commit()
    return db_user

