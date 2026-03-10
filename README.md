# Customer Feedback API

A REST API to receive customer feedback from a web form. Built with FastAPI and PostgreSQL.

---

## System Overview

This API handles customer feedback submissions. The frontend sends a form with the customer's name, email, rating, and optional message. The backend stores the data in a PostgreSQL database.

**Architecture:**

```
Frontend Form  →  POST /feedback  →  FastAPI  →  PostgreSQL
                  GET /categories →  FastAPI  →  PostgreSQL
```

**Tech stack:**

| Component  | Technology        |
|------------|-------------------|
| Framework  | FastAPI (Python)  |
| Database   | PostgreSQL        |
| ORM        | SQLAlchemy        |
| Server     | Uvicorn           |

**Database tables:**

- `feedback_categories` — stores feedback category options (e.g. Product, Service)
- `customer_feedback_forms` — stores each feedback submission
- `file_uploads` — stores files attached to a submission

---

## Requirements

- Python 3.11+
- Docker (for PostgreSQL)

---

## Setup Instructions

**1. Clone the repository**

```bash
git clone <repository-url>
cd customer-feedback
```

**2. Install dependencies**

```bash
pip install -r requirements.txt
```

**3. Create the environment file**

Create a `.env` file in the project root:

```
DATABASE_URL=postgresql://postgres:password@localhost:5432/customer_feedback
```

**4. Start the database**

```bash
docker compose up -d
```

**5. Start the API server**

```bash
uvicorn main:app --reload
```

The server runs at `http://localhost:8000`.
The tables are created automatically on startup.

---

## API Endpoints

### GET /categories

Returns a list of feedback categories.

**Request:**

```
GET http://localhost:8000/categories
```

**Response (200 OK):**

```json
[
  { "id": 1, "name": "Product" },
  { "id": 2, "name": "Service" }
]
```

---

### POST /feedback

Submits a customer feedback form. Accepts optional file attachments.

**Request:**

```
POST http://localhost:8000/feedback
Content-Type: multipart/form-data
```

| Field                | Type    | Required | Description                     |
|----------------------|---------|----------|---------------------------------|
| name                 | string  | Yes      | Customer full name              |
| email                | string  | Yes      | Customer email address          |
| rating               | integer | Yes      | Score from 1 (low) to 5 (high)  |
| phone_number         | string  | No       | Customer phone number           |
| feedback_category_id | integer | No       | ID from GET /categories         |
| feedback             | string  | No       | Written feedback message        |
| files                | file    | No       | One or more file attachments    |

**Example curl:**

```bash
curl -X POST http://localhost:8000/feedback \
  -F "name=John Doe" \
  -F "email=john@example.com" \
  -F "rating=5" \
  -F "feedback=The service was excellent!"
```

**Response (201 Created):**

```json
{
  "id": 1,
  "name": "John Doe",
  "email": "john@example.com",
  "phone_number": null,
  "feedback_category_id": null,
  "rating": 5,
  "feedback": "The service was excellent!",
  "created_at": "2026-03-10T08:00:00",
  "files": []
}
```

**Error responses:**

| Status | Reason                              |
|--------|-------------------------------------|
| 422    | Missing required field or invalid rating |
| 404    | `feedback_category_id` does not exist   |

---

## Interactive API Docs

FastAPI generates a Swagger UI automatically.

Open: `http://localhost:8000/docs`

Use it to test all endpoints directly in the browser without Postman or curl.

---

## Run Tests

```bash
pytest -v
```

Tests use an in-memory SQLite database. No PostgreSQL connection is needed to run tests.
