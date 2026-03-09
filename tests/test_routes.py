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
