# app/schemas/review.py
from pydantic import BaseModel, ConfigDict
from typing import Optional
import uuid

class ReviewBase(BaseModel):
    rating: float
    comment: Optional[str] = None
    course_id: int

class ReviewCreate(ReviewBase):
    pass

class Review(ReviewBase):
    id: int # Auto-incrementing primary key
    owner_id: uuid.UUID
    model_config = ConfigDict(from_attributes=True)