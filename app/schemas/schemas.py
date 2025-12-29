# app/schemas/user.py
from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List
import uuid

# mbti
class MbtiRequest(BaseModel):
    mbti: str = Field(...)


# question
class QuestionItem(BaseModel):
  title: str
  content: Optional[str] = None

class QuestionListResponse(BaseModel):
    questions: List[QuestionItem]


# seaEmotion
class SeaEmotionRequest(BaseModel):
    location: str

class SeaEmotionResponse(BaseModel):
    emotion: str
    name: str


# course
class PathPoint(BaseModel):
    lat: float
    lng: float

class Course(BaseModel):
    courseId: int
    name: str
    totalDistance: float
    color: str
    path: List[PathPoint]

class CourseListResponse(BaseModel):
    courses: List[Course]


# review
class ReviewItem(BaseModel):
    title: str
    keyword: str
    rating: float
    content: str

class ReviewListReponse(BaseModel):
    reviews: List[ReviewItem]

class UserBase(BaseModel):
    mbti: Optional[str] = None

# Supabase 유저 응답을 위한 스키마
class User(UserBase):
    id: uuid.UUID
    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    # Supabase JWT에는 'sub' 클레임에 user_id가 들어갑니다.
    user_id: Optional[str] = None