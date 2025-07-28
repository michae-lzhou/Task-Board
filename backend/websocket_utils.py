# websocket_utils.py
import asyncio
import json
from typing import Any, Dict

class WebSocketManager:
    def __init__(self, sio):
        self.sio = sio
    
    async def emit_project_created(self, project_data: Dict[str, Any]):
        """Emit when a new project is created"""
        await self.sio.emit("project_created", {
            "type": "project_created",
            "data": project_data
        })
    
    async def emit_project_updated(self, project_data: Dict[str, Any]):
        """Emit when a project is updated"""
        await self.sio.emit("project_updated", {
            "type": "project_updated", 
            "data": project_data
        })
    
    async def emit_project_deleted(self, project_id: int, project_name: str):
        """Emit when a project is deleted"""
        await self.sio.emit("project_deleted", {
            "type": "project_deleted",
            "data": {"id": project_id, "name": project_name}
        })
    
    async def emit_member_added(self, project_id: int, user_data: Dict[str, Any]):
        """Emit when a member is added to a project"""
        print(f"DEBUG emit_member_added: project_id={project_id}")
        print(f"DEBUG emit_member_added: user_data type={type(user_data)}")
        print(f"DEBUG emit_member_added: user_data={user_data}")
        
        # Convert if needed
        if hasattr(user_data, '__dict__'):
            print(f"DEBUG: user_data has __dict__, converting...")
            user_data = convert_to_dict(user_data)
            print(f"DEBUG: After conversion: {user_data}")
        
        payload = {
            "type": "member_added",
            "data": {"project_id": project_id, "user": user_data}
        }
        print(f"DEBUG: Final payload: {json.dumps(payload, indent=2)}")
        
        await self.sio.emit("member_added", payload)
    
    async def emit_member_removed(self, project_id: int, user_data: Dict[str, Any]):
        """Emit when a member is removed from a project"""
        await self.sio.emit("member_removed", {
            "type": "member_removed",
            "data": {"project_id": project_id, "user": user_data}
        })
    
    async def emit_task_created(self, task_data: Dict[str, Any]):
        """Emit when a new task is created"""
        await self.sio.emit("task_created", {
            "type": "task_created",
            "data": task_data
        })
    
    async def emit_task_updated(self, task_data: Dict[str, Any]):
        """Emit when a task is updated"""
        await self.sio.emit("task_updated", {
            "type": "task_updated",
            "data": task_data
        })
    
    async def emit_task_deleted(self, task_id: int, task_title: str):
        """Emit when a task is deleted"""
        await self.sio.emit("task_deleted", {
            "type": "task_deleted", 
            "data": {"id": task_id, "title": task_title}
        })
    
    async def emit_user_created(self, user_data: Dict[str, Any]):
        """Emit when a new user is created"""
        await self.sio.emit("user_created", {
            "type": "user_created",
            "data": user_data
        })
    
    async def emit_user_deleted(self, user_id: int, user_name: str):
        """Emit when a user is deleted"""
        await self.sio.emit("user_deleted", {
            "type": "user_deleted",
            "data": {"id": user_id, "name": user_name}
        })

def convert_to_dict(obj):
    """Convert SQLAlchemy object to dictionary for JSON serialization"""
    if obj is None:
        return None
    
    # For SQLAlchemy objects, try to use the __table__ columns
    if hasattr(obj, '__table__'):
        result = {}
        for column in obj.__table__.columns:
            try:
                value = getattr(obj, column.name)
                if value is not None and hasattr(value, '__table__'):
                    # Recursively convert nested SQLAlchemy objects
                    result[column.name] = convert_to_dict(value)
                elif isinstance(value, list):
                    # Handle lists (like relationships)
                    result[column.name] = [convert_to_dict(item) if hasattr(item, '__table__') else item for item in value]
                else:
                    # Handle regular values
                    result[column.name] = value
            except Exception as e:
                # Skip any attributes that cause issues
                print(f"Warning: Could not serialize {column.name}: {e}")
                continue
        return result
    
    # Fallback for non-SQLAlchemy objects
    if hasattr(obj, '__dict__'):
        result = {}
        for key, value in obj.__dict__.items():
            if not key.startswith('_'):
                if hasattr(value, '__dict__'):
                    result[key] = convert_to_dict(value)
                elif isinstance(value, list):
                    result[key] = [convert_to_dict(item) if hasattr(item, '__dict__') else item for item in value]
                else:
                    result[key] = value
        return result
    
    return obj
