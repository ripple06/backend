# app/schemas/location.py
from pydantic import BaseModel, ConfigDict
from typing import Optional

# --- 바다 상태 분석 ---
class SeaEmotion(BaseModel):
    emotion_emoji: str
    emotion_name: str
    reason: str

# --- 지역 정보 ---
class LocationBase(BaseModel):
    name: str
    representative_creature: Optional[str] = None
    specialty: Optional[str] = None
    sea_state_summary: Optional[str] = None
    resort_info: Optional[str] = None

class LocationCreate(LocationBase):
    pass

class Location(LocationBase):
    id: int
    model_config = ConfigDict(from_attributes=True)
