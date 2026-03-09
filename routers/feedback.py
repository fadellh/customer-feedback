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
