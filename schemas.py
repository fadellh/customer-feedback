from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel


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
