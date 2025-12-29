# app/schemas/course.py
from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from app.schemas.review import Review # 절대 경로로 변경
import uuid

class PostCourseQuestionBase(BaseModel):
    question_text: str
    course_id: int

class PostCourseQuestionCreate(PostCourseQuestionBase):
    pass

class PostCourseQuestion(PostCourseQuestionBase):
    id: int # Auto-incrementing primary key
    owner_id: uuid.UUID
    model_config = ConfigDict(from_attributes=True)


class CourseBase(BaseModel):
    name: str
    description: Optional[str] = None
    location_id: int

class CourseCreate(CourseBase):
    pass

class Course(CourseBase):
    id: int
    # Supabase에서 join해서 가져올 때를 대비해 스키마 포함
    reviews: List[Review] = []
    questions: List[PostCourseQuestion] = []
    model_config = ConfigDict(from_attributes=True)