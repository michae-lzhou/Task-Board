import os
import pytest

# Always use test.db in the project root for testing
DB_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                       "..", "test.db"))
os.environ["DATABASE_URL"] = f"sqlite:///{DB_FILE}"

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.main import app, get_db
from backend.database import Base

SQLALCHEMY_DATABASE_URL = os.environ["DATABASE_URL"]

engine = create_engine(SQLALCHEMY_DATABASE_URL,
                       connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False,
                                   bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture(scope="session", autouse=True)
def setup_and_teardown_db():
    Base.metadata.create_all(bind=engine)
    app.dependency_overrides[get_db] = override_get_db
    yield
    Base.metadata.drop_all(bind=engine)
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)

@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c
