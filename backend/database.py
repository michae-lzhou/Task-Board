from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# This is the path to the SQLite file
SQLALCHEMY_DATABASE_URL = "sqlite:///./taskboard.db"

# SQLite needs a special argument for multi-threading support
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# SessionLocal gives us a database session to use in routes and logic
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class that all models will inherit from
Base = declarative_base()

