# Customer Feedback API — Design Document

**Date:** 2026-03-09
**Purpose:** Simple demo API for an English course presentation (backend role)

---

## Overview

A simple REST API built with FastAPI + PostgreSQL that accepts customer feedback form submissions, including optional file uploads. The project serves as a demo for an English course, showcasing a backend developer's role.

---

## Stack

| Component       | Choice           | Reason                                      |
|-----------------|------------------|---------------------------------------------|
| Framework       | FastAPI          | Modern, auto-generates Swagger UI for demos |
| Web Server      | Uvicorn          | Standard ASGI server for FastAPI            |
| ORM             | SQLAlchemy       | Mature Python ORM, works well with FastAPI  |
| DB Driver       | psycopg2         | PostgreSQL adapter for Python               |
| Database        | PostgreSQL       | Relational DB matching the provided ERD     |
| Validation      | Pydantic v2      | Built into FastAPI, handles request schemas |
| File Upload     | python-multipart | Multipart form data parsing                 |
| Config          | python-dotenv    | Load DB URL from .env file                  |

---

## Project Structure

```
customer-feedback/
├── main.py              # FastAPI app entry point, CORS config, startup event
├── database.py          # SQLAlchemy engine + SessionLocal + Base
├── models.py            # ORM models for all 3 tables
├── schemas.py           # Pydantic request/response schemas
├── routers/
│   └── feedback.py      # Route handlers
├── uploads/             # Saved uploaded files (gitignored)
├── requirements.txt     # Python dependencies
└── .env                 # DB_URL (not committed)
```

---

## Database Models (from ERD)

### `feedback_categories`
- `id` bigint PK
- `name` varchar(100) NOT NULL
- `created_at` datetime
- `updated_at` datetime

### `customer_feedback_forms`
- `id` bigint PK
- `name` varchar(100) NOT NULL
- `email` varchar(100) NOT NULL
- `phone_number` varchar(20)
- `feedback_category_id` bigint FK → feedback_categories.id
- `rating` integer NOT NULL
- `feedback` text
- `created_at` datetime
- `updated_at` datetime
- `deleted_at` datetime (soft delete)

### `file_uploads`
- `id` bigint PK
- `customer_feedback_id` bigint FK → customer_feedback_forms.id NOT NULL
- `name` varchar(255) NOT NULL
- `path` varchar(255) NOT NULL
- `created_at` datetime
- `updated_at` datetime

---

## Endpoints

### `POST /feedback`
Submit a customer feedback form with optional file uploads.

- **Content-Type:** `multipart/form-data`
- **Form fields:**

| Field                  | Type    | Required | Notes              |
|------------------------|---------|----------|--------------------|
| name                   | string  | Yes      | max 100 chars      |
| email                  | string  | Yes      | max 100 chars      |
| phone_number           | string  | No       | max 20 chars       |
| feedback_category_id   | integer | No       | FK to categories   |
| rating                 | integer | Yes      | value 1–5          |
| feedback               | string  | No       | free text          |
| files                  | file[]  | No       | optional uploads   |

- **Response `201`:** Created feedback record with file list
- **Response `422`:** Validation error (auto-handled by FastAPI)

### `GET /categories`
Returns all feedback categories for populating a dropdown on the frontend.

- **Response `200`:** List of `{ id, name }`

---

## Error Handling

- FastAPI's built-in validation handles missing/invalid fields (422)
- DB errors surface as 500 with a generic message
- No auth required (demo scope)

---

## Out of Scope

- Authentication / authorization
- Read, update, delete feedback endpoints
- Pagination
- Email notifications
