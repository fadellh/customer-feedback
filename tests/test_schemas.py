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
