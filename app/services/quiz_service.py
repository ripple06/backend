# app/services/quiz_service.py
import random
from supabase import Client
from app.schemas.schemas import *
from typing import Optional, List
from datetime import datetime

def get_random_quiz(supabase: Client, limit:int = 1) -> List[dict]:
  try:
    response = supabase.rpc('get_random_quizzes', {'quiz_limit': limit}).execute()

    if not response.data:
      all_quizes = supabase.table('quizes').select('*').execute()
      if all_quizes.data:
        return random.sample(all_quizes.data, min(limit, len(all_quizes.data)))
      return []
    
    return response.data
  except Exception as e:
    print(f"랜덤 퀴즈에서 오류: {e}")
    try:
      all_quizzes = supabase.table('quizzes').select('*').execute()
      if all_quizzes.data and len(all_quizzes.data) > 0:
        return random.sample(all_quizzes.data, min(limit, len(all_quizzes.data)))
      return []
    except Exception as fallback_error:
      print(f"또 실패: {fallback_error}")
      return []