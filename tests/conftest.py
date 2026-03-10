import os
import shutil
import tempfile
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base, get_db
from main import app
from models import FeedbackCategory

TEST_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db, tmp_upload_dir, monkeypatch):
    def override_get_db():
        try:
            yield db
        finally:
            pass

    # db fixture already creates tables via SQLite; skip the lifespan's create_all
    monkeypatch.setattr("database.Base.metadata.create_all", lambda bind: None)
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def tmp_upload_dir(monkeypatch):
    tmp_dir = tempfile.mkdtemp()
    monkeypatch.setattr("routers.feedback.UPLOAD_DIR", tmp_dir)
    yield tmp_dir
    shutil.rmtree(tmp_dir, ignore_errors=True)


@pytest.fixture
def category(db):
    cat = FeedbackCategory(name="Product")
    db.add(cat)
    db.commit()
    db.refresh(cat)
    return cat
