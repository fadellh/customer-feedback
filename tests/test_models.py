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
