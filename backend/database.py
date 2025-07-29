################################################################################
# database.py
# Purpose:  Sets up the locally hosted database via SQLite in taskboard.db
################################################################################

# Libraries
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

# Path to the SQLite file (now configurable via environment variable)
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./taskboard.db")

# SQLite needs a special argument for multi-threading support
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# SessionLocal gives us a database session to use in routes and logic
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class that all models will inherit from
Base = declarative_base()
