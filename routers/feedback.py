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
