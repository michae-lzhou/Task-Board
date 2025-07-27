# Suite of custom exceptions for debugging and maintainability

class ProjectNotFound(Exception):
    def __init__(self, project_id: int):
        self.project_id = project_id
        self.message = f"Project {project_id} not found."
        super().__init__(self.message)

class DuplicateProjectName(Exception):
    def __init__(self, project_name: str):
        self.message = f"Duplicate project name [{project_name}]!"
        super().__init__(self.message)

class TaskNotFound(Exception):
    def __init__(self, task_id: int):
        self.task_id = task_id
        self.message = f"Task {task_id} not found."
        super().__init__(self.message)

class DuplicateTaskName(Exception):
    def __init__(self, task_name: str, project_name: str):
        self.task_name = task_name
        self.project_name = project_name
        self.message = f"Duplicate task name [{task_name}] in project " \
                       f"[{project_name}]!"
        super().__init__(self.message)

class MovingTaskToNewProject(Exception):
    def __init__(self, task_name: int):
        self.task_name = task_name
        self.message = f"Not allowed to move task [{task_name}] to a new "\
                        "project!"
        super().__init__(self.message)

class AssigneeNotMember(Exception):
    def __init__(self, assignee_name: str, project_name: int):
        self.assignee_name = assignee_name
        self.project_name = project_name
        self.message = f"User [{assignee_name}] is not a member of project " \
                       f"[{project_name}]!"

class UserNotFound(Exception):
    def __init__(self, user_id: int):
        self.user_id = user_id
        self.message = f"User {user_id} not found."
        super().__init__(self.message)

class DuplicateUserEmail(Exception):
    def __init__(self, email):
        self.email = email
        self.message = f"User with email {email} already exists."
        super().__init__(self.message)

class UserInProject(Exception):
    def __init__(self, user_name: str, project_name: str):
        self.user_name = user_name
        self.project_name = project_name
        self.message = f"User [{user_name}] is already a member of project " \
                       f"[{project_name}]."

class UserNotInProject(Exception):
    def __init__(self, user_name: str, project_name: str):
        self.user_name = user_name
        self.project_name = project_name
        self.message = f"User [{user_name}] is NOT a member of project " \
                       f"[{project_name}]."


__all__ = ["ProjectNotFound", "DuplicateProjectName", "TaskNotFound", \
           "MovingTaskToNewProject", "AssigneeNotMember", "DuplicateTaskName", \
           "UserNotFound", "DuplicateUserEmail", "UserInProject", \
           "UserNotInProject"]
