# 🗂️ Task Board App

A real-time collaborative task management web application built with **FastAPI** (backend) and **React** (frontend). Users can create projects, assign tasks, and manage team members — all with live updates powered by **WebSockets**.

---

## Features

- Create and manage projects
- Add, update, and delete tasks per project
- Invite and remove team members
- Real-time updates across all users using WebSockets
- Full API test coverage with `pytest`

---

## Tech Stack

| Layer     | Tech                     |
|-----------|--------------------------|
| Frontend  | React, Vite, JavaScript  |
| Backend   | FastAPI, SQLAlchemy      |
| Database  | SQLite (local)           |
| Real-Time | Socket.IO (via ASGI)     |
| Testing   | Pytest                   |

---

## Local Development Setup

> Run all commands **from the project root** (`Task-Board/`)

### Backend Setup (FastAPI)

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cd ..
python -m backend.server_startup
```


### Frontend (React)

```bash
cd frontend
npm install
npm run dev
```


### Unit Testing (pytest)
```bash
pytest
```
