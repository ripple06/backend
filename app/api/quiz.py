# app/routes/quiz.py
from fastapi import APIRouter, Depends, HTTPException
from supabase import Client
from app.schemas.schemas import *
from app.core.supabase_client import get_supabase
from app.services.quiz_service import *
import traceback

router = APIRouter()

@router.get("/quizes", response_model=QuizResponse)
def get_random_quizes(supabase: Client = Depends(get_supabase)):
  try:
    quiz = get_random_quiz_service(supabase)

    if not quiz:
      raise HTTPException(404, detail="퀴즈를 찾을 수 없습니다.")
    
    return QuizResponse(id = quiz['id'], title = quiz['title'], content = quiz['content'], correct = quiz['correct'])
  except HTTPException:
    raise
  except Exception as e:
    traceback.print_exc()
    raise HTTPException(500, detail=f"퀴즈 조회 중 오류가 발생했습니다: {str(e)}")