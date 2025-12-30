# app/services/quiz_service.py
from supabase import Client
from app.schemas.schemas import *
from typing import Optional
import traceback
import random

def get_random_quiz_service(supabase: Client) -> Optional[dict]:
    try:
        # RPC 대신 테이블에서 직접 조회
        resp = supabase.table('quizes').select('*').execute()
        if getattr(resp, "error", None):
            print(f"[ERROR] quizes select error: {resp.error}")
            return None

        rows = resp.data if getattr(resp, "data", None) else []
        if not rows:
            return None

        # Python에서 랜덤 선택
        quiz = random.choice(rows)
        return quiz
    except Exception as e:
        print(f"[EXCEPTION] get_random_quiz_service failed: {e}")
        traceback.print_exc()
        return None