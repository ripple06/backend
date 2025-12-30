# app/services/quiz_service.py
from supabase import Client
from app.schemas.schemas import *
from typing import Optional
import traceback
import random

def get_random_quiz_service(supabase: Client) -> Optional[dict]:
    try:
        resp = supabase.table('quizes').select('*').execute()
        if getattr(resp, "error", None):
            return None

        rows = resp.data if getattr(resp, "data", None) else []
        if not rows:
            return None

        quiz = random.choice(rows)
        return quiz
    except Exception:
        traceback.print_exc()
        return None