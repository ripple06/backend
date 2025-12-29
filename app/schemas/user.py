# app/schemas/user.py
from pydantic import BaseModel, ConfigDict, EmailStr
from typing import Optional
import uuid

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