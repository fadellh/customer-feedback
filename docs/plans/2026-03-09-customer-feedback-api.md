# Customer Feedback API Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a simple FastAPI + PostgreSQL REST API that accepts customer feedback form submissions with optional file uploads.

**Architecture:** Minimal layered structure — `main.py` (app entry), `database.py` (DB connection), `models.py` (SQLAlchemy ORM), `schemas.py` (Pydantic), and `routers/feedback.py` (route handlers). Files are saved locally to an `uploads/` directory.

**Tech Stack:** FastAPI, Uvicorn, SQLAlchemy, psycopg2-binary, Pydantic v2, python-multipart, python-dotenv, pytest, httpx

---

## Pre-requisites

- Python 3.11+
- PostgreSQL running locally (or via Docker)
- A database named `customer_feedback` created:
  ```sql
  CREATE DATABASE customer_feedback;
  ```
- A `.env` file in project root:
  ```
  DATABASE_URL=postgresql://postgres:password@localhost:5432/customer_feedback
  ```

---

### Task 1: Project Bootstrap

**Files:**
- Create: `requirements.txt`
- Create: `.env` (not committed)
- Create: `.gitignore`

**Step 1: Create requirements.txt**

```
fastapi==0.115.0
uvicorn[standard]==0.30.6
sqlalchemy==2.0.35
psycopg2-binary==2.9.9
python-multipart==0.0.12
python-dotenv==1.0.1
pytest==8.3.3
httpx==0.27.2
```

**Step 2: Create .gitignore**

```
.env
__pycache__/
*.pyc
uploads/
.pytest_cache/
```

**Step 3: Install dependencies**

Run:
```bash
pip install -r requirements.txt
```
Expected: All packages install without errors.

**Step 4: Commit**

```bash
git init
git add requirements.txt .gitignore
git commit -m "chore: project bootstrap"
```

---

### Task 2: Database Connection

**Files:**
- Create: `database.py`
- Create: `tests/__init__.py`
- Create: `tests/conftest.py`

**Step 1: Write `database.py`**

```python
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

**Step 2: Write `tests/conftest.py`**

```python
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base, get_db
from main import app

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
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
```

**Step 3: Write `tests/__init__.py`** (empty file)

**Step 4: Commit**

```bash
git add database.py tests/
git commit -m "feat: add database connection and test fixtures"
```

---

### Task 3: SQLAlchemy Models

**Files:**
- Create: `models.py`

**Step 1: Write `models.py`**

```python
from datetime import datetime
from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from database import Base


class FeedbackCategory(Base):
    __tablename__ = "feedback_categories"

    id = Column(BigInteger, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    feedbacks = relationship("CustomerFeedbackForm", back_populates="category")


class CustomerFeedbackForm(Base):
    __tablename__ = "customer_feedback_forms"

    id = Column(BigInteger, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False)
    phone_number = Column(String(20), nullable=True)
    feedback_category_id = Column(BigInteger, ForeignKey("feedback_categories.id"), nullable=True)
    rating = Column(Integer, nullable=False)
    feedback = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = Column(DateTime, nullable=True)

    category = relationship("FeedbackCategory", back_populates="feedbacks")
    files = relationship("FileUpload", back_populates="feedback_form")


class FileUpload(Base):
    __tablename__ = "file_uploads"

    id = Column(BigInteger, primary_key=True, index=True)
    customer_feedback_id = Column(BigInteger, ForeignKey("customer_feedback_forms.id"), nullable=False)
    name = Column(String(255), nullable=False)
    path = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    feedback_form = relationship("CustomerFeedbackForm", back_populates="files")
```

**Step 2: Write the failing test**

File: `tests/test_models.py`

```python
from models import FeedbackCategory, CustomerFeedbackForm, FileUpload


def test_feedback_category_model(db):
    category = FeedbackCategory(name="Product")
    db.add(category)
    db.commit()
    db.refresh(category)
    assert category.id is not None
    assert category.name == "Product"


def test_customer_feedback_form_model(db):
    category = FeedbackCategory(name="Service")
    db.add(category)
    db.commit()

    form = CustomerFeedbackForm(
        name="Alice",
        email="alice@example.com",
        rating=5,
        feedback_category_id=category.id,
    )
    db.add(form)
    db.commit()
    db.refresh(form)
    assert form.id is not None
    assert form.name == "Alice"
    assert form.deleted_at is None


def test_file_upload_model(db):
    form = CustomerFeedbackForm(name="Bob", email="bob@example.com", rating=4)
    db.add(form)
    db.commit()

    upload = FileUpload(
        customer_feedback_id=form.id,
        name="receipt.pdf",
        path="uploads/receipt.pdf",
    )
    db.add(upload)
    db.commit()
    db.refresh(upload)
    assert upload.id is not None
    assert upload.name == "receipt.pdf"
```

**Step 3: Run test to verify it fails**

Run:
```bash
pytest tests/test_models.py -v
```
Expected: FAIL (no `main.py` yet, import error)

**Step 4: Create minimal `main.py` to unblock tests**

```python
from fastapi import FastAPI
from database import engine, Base

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Customer Feedback API")
```

**Step 5: Run test to verify it passes**

Run:
```bash
pytest tests/test_models.py -v
```
Expected: 3 tests PASS

**Step 6: Commit**

```bash
git add models.py tests/test_models.py main.py
git commit -m "feat: add SQLAlchemy models matching ERD"
```

---

### Task 4: Pydantic Schemas

**Files:**
- Create: `schemas.py`

**Step 1: Write `schemas.py`**

```python
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field


class FileUploadResponse(BaseModel):
    id: int
    name: str
    path: str
    created_at: datetime

    model_config = {"from_attributes": True}


class FeedbackCategoryResponse(BaseModel):
    id: int
    name: str

    model_config = {"from_attributes": True}


class FeedbackSubmitResponse(BaseModel):
    id: int
    name: str
    email: str
    phone_number: Optional[str]
    feedback_category_id: Optional[int]
    rating: int
    feedback: Optional[str]
    created_at: datetime
    files: List[FileUploadResponse] = []

    model_config = {"from_attributes": True}
```

**Step 2: Write the failing test**

File: `tests/test_schemas.py`

```python
from schemas import FeedbackSubmitResponse, FeedbackCategoryResponse


def test_feedback_category_response_schema():
    data = {"id": 1, "name": "Product"}
    schema = FeedbackCategoryResponse.model_validate(data)
    assert schema.id == 1
    assert schema.name == "Product"


def test_feedback_submit_response_schema():
    from datetime import datetime
    data = {
        "id": 1,
        "name": "Alice",
        "email": "alice@example.com",
        "phone_number": None,
        "feedback_category_id": None,
        "rating": 5,
        "feedback": "Great service!",
        "created_at": datetime.utcnow(),
        "files": [],
    }
    schema = FeedbackSubmitResponse.model_validate(data)
    assert schema.name == "Alice"
    assert schema.rating == 5
    assert schema.files == []
```

**Step 3: Run test to verify it fails**

Run:
```bash
pytest tests/test_schemas.py -v
```
Expected: FAIL — `schemas.py` not yet created

**Step 4: Run test to verify it passes**

Run:
```bash
pytest tests/test_schemas.py -v
```
Expected: 2 tests PASS

**Step 5: Commit**

```bash
git add schemas.py tests/test_schemas.py
git commit -m "feat: add Pydantic response schemas"
```

---

### Task 5: Feedback Router — GET /categories

**Files:**
- Create: `routers/__init__.py` (empty)
- Create: `routers/feedback.py`
- Create: `tests/test_routes.py`

**Step 1: Seed a category in conftest**

In `tests/conftest.py`, add a `category` fixture at the bottom:

```python
from models import FeedbackCategory

@pytest.fixture
def category(db):
    cat = FeedbackCategory(name="Product")
    db.add(cat)
    db.commit()
    db.refresh(cat)
    return cat
```

**Step 2: Write the failing test**

File: `tests/test_routes.py`

```python
def test_get_categories_empty(client):
    response = client.get("/categories")
    assert response.status_code == 200
    assert response.json() == []


def test_get_categories_returns_list(client, category):
    response = client.get("/categories")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Product"
```

**Step 3: Run test to verify it fails**

Run:
```bash
pytest tests/test_routes.py -v
```
Expected: FAIL — router not registered yet

**Step 4: Create `routers/feedback.py`**

```python
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import FeedbackCategory
from schemas import FeedbackCategoryResponse

router = APIRouter()


@router.get("/categories", response_model=List[FeedbackCategoryResponse])
def get_categories(db: Session = Depends(get_db)):
    return db.query(FeedbackCategory).all()
```

**Step 5: Register router in `main.py`**

Update `main.py`:

```python
from fastapi import FastAPI
from database import engine, Base
from routers import feedback

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Customer Feedback API")
app.include_router(feedback.router)
```

**Step 6: Run test to verify it passes**

Run:
```bash
pytest tests/test_routes.py::test_get_categories_empty tests/test_routes.py::test_get_categories_returns_list -v
```
Expected: 2 tests PASS

**Step 7: Commit**

```bash
git add routers/ tests/test_routes.py tests/conftest.py main.py
git commit -m "feat: add GET /categories endpoint"
```

---

### Task 6: Feedback Router — POST /feedback (no files)

**Files:**
- Modify: `routers/feedback.py`

**Step 1: Write the failing test**

Add to `tests/test_routes.py`:

```python
def test_submit_feedback_success(client, category):
    response = client.post("/feedback", data={
        "name": "Alice",
        "email": "alice@example.com",
        "rating": "5",
        "feedback_category_id": str(category.id),
        "feedback": "Excellent service!",
    })
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Alice"
    assert data["email"] == "alice@example.com"
    assert data["rating"] == 5
    assert data["files"] == []


def test_submit_feedback_missing_required_fields(client):
    response = client.post("/feedback", data={"name": "Bob"})
    assert response.status_code == 422


def test_submit_feedback_invalid_rating(client):
    response = client.post("/feedback", data={
        "name": "Charlie",
        "email": "charlie@example.com",
        "rating": "10",
    })
    assert response.status_code == 422
```

**Step 2: Run test to verify it fails**

Run:
```bash
pytest tests/test_routes.py::test_submit_feedback_success -v
```
Expected: FAIL — endpoint not defined

**Step 3: Add POST /feedback to `routers/feedback.py`**

```python
import os
import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session
from database import get_db
from models import CustomerFeedbackForm, FeedbackCategory, FileUpload
from schemas import FeedbackCategoryResponse, FeedbackSubmitResponse

router = APIRouter()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.get("/categories", response_model=List[FeedbackCategoryResponse])
def get_categories(db: Session = Depends(get_db)):
    return db.query(FeedbackCategory).all()


@router.post("/feedback", response_model=FeedbackSubmitResponse, status_code=status.HTTP_201_CREATED)
def submit_feedback(
    name: str = Form(...),
    email: str = Form(...),
    rating: int = Form(..., ge=1, le=5),
    phone_number: Optional[str] = Form(None),
    feedback_category_id: Optional[int] = Form(None),
    feedback: Optional[str] = Form(None),
    files: List[UploadFile] = File(default=[]),
    db: Session = Depends(get_db),
):
    if feedback_category_id is not None:
        category = db.query(FeedbackCategory).filter(FeedbackCategory.id == feedback_category_id).first()
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")

    form_entry = CustomerFeedbackForm(
        name=name,
        email=email,
        phone_number=phone_number,
        feedback_category_id=feedback_category_id,
        rating=rating,
        feedback=feedback,
    )
    db.add(form_entry)
    db.commit()
    db.refresh(form_entry)

    saved_files = []
    for file in files:
        ext = os.path.splitext(file.filename)[1]
        unique_name = f"{uuid.uuid4().hex}{ext}"
        file_path = os.path.join(UPLOAD_DIR, unique_name)
        with open(file_path, "wb") as f:
            f.write(file.file.read())

        upload = FileUpload(
            customer_feedback_id=form_entry.id,
            name=file.filename,
            path=file_path,
        )
        db.add(upload)
        saved_files.append(upload)

    if saved_files:
        db.commit()
        for upload in saved_files:
            db.refresh(upload)

    db.refresh(form_entry)
    return form_entry
```

**Step 4: Run all feedback tests**

Run:
```bash
pytest tests/test_routes.py -v
```
Expected: All tests PASS

**Step 5: Commit**

```bash
git add routers/feedback.py tests/test_routes.py
git commit -m "feat: add POST /feedback endpoint with optional file upload"
```

---

### Task 7: File Upload Test

**Files:**
- Modify: `tests/test_routes.py`

**Step 1: Write the failing test**

Add to `tests/test_routes.py`:

```python
import io

def test_submit_feedback_with_file(client):
    fake_file = io.BytesIO(b"fake file content")
    response = client.post(
        "/feedback",
        data={"name": "Dana", "email": "dana@example.com", "rating": "4"},
        files={"files": ("report.txt", fake_file, "text/plain")},
    )
    assert response.status_code == 201
    data = response.json()
    assert len(data["files"]) == 1
    assert data["files"][0]["name"] == "report.txt"
```

**Step 2: Run test to verify it passes** (implementation already complete from Task 6)

Run:
```bash
pytest tests/test_routes.py::test_submit_feedback_with_file -v
```
Expected: PASS

**Step 3: Run full test suite**

Run:
```bash
pytest -v
```
Expected: All tests PASS

**Step 4: Commit**

```bash
git add tests/test_routes.py
git commit -m "test: add file upload test for POST /feedback"
```

---

### Task 8: CORS + Final App Wiring

**Files:**
- Modify: `main.py`

**Step 1: Update `main.py` with CORS**

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
from routers import feedback

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Customer Feedback API",
    description="Demo API for handling customer feedback submissions",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(feedback.router)
```

**Step 2: Run full test suite to confirm nothing broke**

Run:
```bash
pytest -v
```
Expected: All tests PASS

**Step 3: Manual smoke test — start the server**

Run:
```bash
uvicorn main:app --reload
```
Open browser: `http://localhost:8000/docs`
Expected: Swagger UI shows `GET /categories` and `POST /feedback`

**Step 4: Commit**

```bash
git add main.py
git commit -m "feat: add CORS middleware and finalize app wiring"
```

---

## Summary

| Endpoint            | Method | Description                              |
|---------------------|--------|------------------------------------------|
| `/categories`       | GET    | List all feedback categories             |
| `/feedback`         | POST   | Submit feedback with optional file upload|
| `/docs`             | GET    | Auto-generated Swagger UI (FastAPI)      |

**Run all tests:**
```bash
pytest -v
```

**Start server:**
```bash
uvicorn main:app --reload
```
