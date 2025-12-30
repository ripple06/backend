# app/services/course_service.py
import random
from supabase import Client
from app.schemas.schemas import *
from typing import Optional

def get_mbti(user_id: int, supabase: Client) -> Optional[str]:
    """
    사용자의 MBTI를 조회합니다.
    
    Args:
        user_id: 사용자 ID
        supabase: Supabase 클라이언트
        
    Returns:
        사용자의 MBTI 문자열, 존재하지 않으면 None
    """
    try:
        response = supabase.table('users').select('mbti').eq('id', user_id).execute()
        
        if response.data and len(response.data) > 0:
            return response.data[0]['mbti']
        return None
    except Exception as e:
        print(f"Error fetching MBTI for user {user_id}: {e}")
        return None

def recommend_course(mbti: str, sea_emotion: SeaEmotionRequest, supabase: Client):
    pass