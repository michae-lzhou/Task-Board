'''
NOTE: everything here is actually what happens in the database, main.py is more
logic and API endpoint flow + error handling

NOTE: all instances are accessed via their unique id here to avoid problems deep
into the code, other function figure out what the id is supposed to be from the
individual fields
'''
# Libraries
from sqlalchemy.orm import Session, selectinload
from pydantic import EmailStr

# Local files
from models import Project, Task, User
from schemas import ProjectCreate, TaskCreate, UserCreate
from exceptions import *

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

    db_project = Project(**project.dict())
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

''' TODO: maybe send a message saying there are no projects?? '''
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
    else:
        raise UserInProject(user.name, project.name)

    return project

# Delete
def delete_project(db: Session, project_id: int):
    db_project = get_project(db, project_id)
    if not db_project:
        raise ProjectNotFound(project_id)
    db.delete(db_project)
    db.commit()
    return db_project

################################################################################
###                                  Task                                    ###
################################################################################

# Create
def create_task(db: Session, task: TaskCreate):
    # Double checks that the project to be attached to exists
    project = db.query(Project).filter(
                    Project.id == task.project_id
              ).first()
    if not project:
        raise ProjectNotFound(task.project_id)

    # Handling duplicate names in the same project
    dupe = db.query(Task).filter(
                Task.project_id == task.project_id,
                Task.title == task.title
           ).first()
    if dupe:
        raise DuplicateTaskName(task.title, project.name)

    db_task = Task(**task.dict())
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

# Read
def get_task(db: Session, task_id: int):
    task = db.query(Task) \
           .options(
               selectinload(Task.project),
               selectinload(Task.assigned_user)
           ) \
           .filter(
               Task.id == task_id
           ).first()
    if not task:
        raise TaskNotFound(task_id)
    return task

def get_tasks_by_project(db: Session, project_id: int):
    project = db.query(Project).filter(
                    Project.id == project_id
              ).first()
    if not project:
        raise ProjectNotFound(project_id)
    return db.query(Task) \
            .options(
                selectinload(Task.project),
                selectinload(Task.assigned_user)
            ) \
            .filter(
                Task.project_id == project_id
            ).all()

# Update
def update_task(db: Session, task_id: int, updated: TaskCreate):
    db_task = get_task(db, task_id)
    if not db_task:
        raise TaskNotFound(task_id)

    # Prevent project reassignment
    if updated.project_id != db_task.project_id:
        raise MovingTaskToNewProject(db_task.title)

    # Check if the assigned user is a member of the project
    if updated.assigned_to is not None:
        assignee = db.query(User).filter(
                        User.id == updated.assigned_to
                   ).first()
        if not assignee:
            raise UserNotFound(updated.assigned_to)

        project = db.query(Project).filter(
                        Project.id == db_task.project_id
                  ).first()
        if not project:
            raise ProjectNotFound(db_task.project_id)
        user_ids = [user.id for user in project.members]
        # Since members of a project HAS to be valid users, no need to double
        # check here
        if assignee.id not in user_ids:
            raise AssigneeNotMember(assignee.name, project.name)

    # Check if the new name is a duplicate within the project
    dupe = db.query(Task).filter(
                Task.project_id == db_task.project_id,
                Task.title == updated.title,
                # Allow edits without changing task title
                Task.title != db_task.title
           ).first()
    if dupe:
        raise DuplicateTaskName(updated.title, project.name)

    for key, value in updated.dict().items():
        setattr(db_task, key, value)
    db.commit()
    db.refresh(db_task)
    return db_task

# Delete
def delete_task(db: Session, task_id: int):
    db_task = get_task(db, task_id)
    if not db_task:
        raise TaskNotFound(task_id)
    db.delete(db_task)
    db.commit()
    return db_task


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
    db.delete(db_user)
    db.commit()
    return db_user
