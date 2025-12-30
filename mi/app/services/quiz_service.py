# app/services/quiz_service.py
from supabase import Client
from app.schemas.schemas import *
from typing import Optional

def get_random_quiz_service(supabase: Client) -> Optional[dict]:
    response = supabase.rpc("get_random_quiz").execute()

    if response.data and len(response.data) > 0:
        return response.data[0]

    return None