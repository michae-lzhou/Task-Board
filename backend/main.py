# main.py
# Libraries
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from database import Base, engine, SessionLocal
import logging
import socketio
# Local files
import models
from routers import projects, tasks, users

# Set up basic logging for errors
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s - %(levelname)s - %(message)s")

# Create Socket.IO server
sio = socketio.AsyncServer(
    async_mode='asgi',
    cors_allowed_origins="*",
    logger=True,
    engineio_logger=True
)

app = FastAPI()

# Allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create Socket.IO ASGI app
socket_app = socketio.ASGIApp(sio, app)

@app.get("/")
def read_root():
    return {"message": "Hello from backend"}

# Create database tables
models.Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# WebSocket event handlers
@sio.event
async def connect(sid, environ):
    print(f"Client connected: {sid}")
    await sio.emit("connection_established", {"message": "Connected to server"}, room=sid)

@sio.event
async def disconnect(sid):
    print(f"Client disconnected: {sid}")

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

# Make sio available to routers
app.state.sio = sio

# Include routers
app.include_router(projects.router, prefix="/projects", tags=["projects"])
app.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
app.include_router(users.router, prefix="/users", tags=["users"])
