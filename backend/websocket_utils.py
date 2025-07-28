################################################################################
# websocket_utils.py
# Purpose:  Provides a WebSocketManager class for emitting real-time Socket.IO
#           events related to project, task, and user updates in the
#           application. Includes utility functions for converting SQLAlchemy
#           objects to JSON-serializable dictionaries to ensure consistent
#           payload formatting.
################################################################################

# Libraries
import asyncio
import json
from typing import Any, Dict, Optional, Union
from enum import Enum

# Enum for WebSocket event types
class EventType(Enum):
    PROJECT_CREATED = "project_created"
    PROJECT_UPDATED = "project_updated"
    PROJECT_DELETED = "project_deleted"
    MEMBER_ADDED = "member_added"
    MEMBER_REMOVED = "member_removed"
    TASK_CREATED = "task_created"
    TASK_UPDATED = "task_updated"
    TASK_DELETED = "task_deleted"
    USER_CREATED = "user_created"
    USER_DELETED = "user_deleted"

class WebSocketManager:
    def __init__(self, sio):
        self.sio = sio
        self.debug = True  # Toggle for debug logging
    
    # Generic method to emit events with consistent structure
    async def _emit_event(self, event_type: Union[EventType, str],
                          data: Dict[str, Any]):
        event_name = event_type.value if isinstance(event_type, EventType)
                                      else event_type
        
        payload = {
            "type": event_name,
            "data": data
        }
        
        if self.debug and event_name in ["member_added", "member_removed"]:
            print(f"DEBUG {event_name}: {json.dumps(payload, indent=2)}")
        
        await self.sio.emit(event_name, payload)
    
    async def emit_project_created(self, project_data: Dict[str, Any]):
        await self._emit_event(EventType.PROJECT_CREATED, project_data)
    
    async def emit_project_updated(self, project_data: Dict[str, Any]):
        await self._emit_event(EventType.PROJECT_UPDATED, project_data)
    
    async def emit_project_deleted(self, project_id: int, project_name: str):
        await self._emit_event(EventType.PROJECT_DELETED, {
            "id": project_id, 
            "name": project_name
        })
    
    async def emit_member_added(self, project_id: int, user_data: Any):
        user_dict = self._prepare_data(user_data, "user_data")
        await self._emit_event(EventType.MEMBER_ADDED, {
            "project_id": project_id, 
            "user": user_dict
        })
    
    async def emit_member_removed(self, project_id: int, user_data: Any):
        user_dict = self._prepare_data(user_data, "user_data")
        await self._emit_event(EventType.MEMBER_REMOVED, {
            "project_id": project_id, 
            "user": user_dict
        })
    
    async def emit_task_created(self, task_data: Any):
        task_dict = self._prepare_data(task_data, "task_data")
        await self._emit_event(EventType.TASK_CREATED, task_dict)
    
    async def emit_task_updated(self, task_data: Any):
        task_dict = self._prepare_data(task_data, "task_data")
        await self._emit_event(EventType.TASK_UPDATED, task_dict)
    
    async def emit_task_deleted(self, task_id: int, task_title: str, \
                                project_id: Optional[int] = None):
        data = {"id": task_id, "title": task_title}
        if project_id is not None:
            data["project_id"] = project_id
        await self._emit_event(EventType.TASK_DELETED, data)
    
    async def emit_user_created(self, user_data: Any):
        user_dict = self._prepare_data(user_data, "user_data")
        await self._emit_event(EventType.USER_CREATED, user_dict)
    
    async def emit_user_deleted(self, user_id: int, user_name: str):
        await self._emit_event(EventType.USER_DELETED, {
            "id": user_id, 
            "name": user_name
        })
    
    # Prepare data for emission, converting SQLAlchemy objects if needed
    def _prepare_data(self, data: Any, data_name: str = "data") \
            -> Dict[str, Any]:
        if self.debug:
            print(f"DEBUG _prepare_data: {data_name} type={type(data)}")
        
        if hasattr(data, '__dict__') or hasattr(data, '__table__'):
            if self.debug:
                print(f"DEBUG: {data_name} needs conversion")
            result = convert_to_dict(data)
            if self.debug:
                print(f"DEBUG: After conversion: {result}")
            return result
        
        return data

# Convert SQLAlchemy object to dictionary for JSON serialization
def convert_to_dict(obj: Any) -> Any:
    if obj is None:
        return None
    
    # Handle SQLAlchemy objects with __table__ attribute
    if hasattr(obj, '__table__'):
        return _convert_sqlalchemy_object(obj)
    
    # Handle regular objects with __dict__
    if hasattr(obj, '__dict__'):
        return _convert_regular_object(obj)
    
    # Return as-is for primitive types
    return obj

# Convert SQLAlchemy model instance to dictionary
def _convert_sqlalchemy_object(obj: Any) -> Dict[str, Any]:
    result = {}
    
    for column in obj.__table__.columns:
        try:
            value = getattr(obj, column.name)
            result[column.name] = _convert_value(value)
        except Exception as e:
            print(f"Warning: Could not serialize {column.name}: {e}")
            continue
    
    return result

# Convert regular Python object to dictionary
def _convert_regular_object(obj: Any) -> Dict[str, Any]:
    result = {}
    
    for key, value in obj.__dict__.items():
        if not key.startswith('_'):
            result[key] = _convert_value(value)
    
    return result

# Convert a single value, handling nested objects and lists
def _convert_value(value: Any) -> Any:
    if value is None:
        return None
    
    # Handle nested SQLAlchemy objects
    if hasattr(value, '__table__'):
        return convert_to_dict(value)
    
    # Handle nested regular objects
    if hasattr(value, '__dict__'):
        return convert_to_dict(value)
    
    # Handle lists
    if isinstance(value, list):
        return [convert_to_dict(item) \
                if hasattr(item, ('__table__', '__dict__')) else item 
                for item in value]
    
    # Return primitive values as-is
    return value
