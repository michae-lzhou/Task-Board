################################################################################
# crud/tasks.py
# Purpose:  Implements CRUD operations for the Task model using SQLAlchemy.
#           Includes functionality for task creation, retrieval (by ID and by
#           project), updating (with validation for reassignment and
#           duplicates), and deletion. Ensures business rules like project
#           membership and task uniqueness are enforced at the database
#           interaction layer. Again, ID's are used to ensure consistency in the
#           event of data corruption.
################################################################################

# Libraries
from sqlalchemy.orm import Session, selectinload

# Local files
from ..models import Project, Task, User
from ..schemas import TaskCreate
from ..exceptions import *

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

    # Check if the assigned user is a member of the project
    if task.assigned_to is not None:
        assignee = db.query(User).filter(
                        User.id == task.assigned_to
                   ).first()
        if not assignee:
            raise UserNotFound(task.assigned_to)

        project = db.query(Project).filter(
                        Project.id == task.project_id
                  ).first()
        if not project:
            raise ProjectNotFound(task.project_id)
        user_ids = [user.id for user in project.members]
        # Since members of a project HAS to be valid users, no need to double
        # check here
        if assignee.id not in user_ids:
            raise AssigneeNotMember(assignee.name, project.name)

    db_task = Task(**task.model_dump())
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

    for key, value in updated.model_dump().items():
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

