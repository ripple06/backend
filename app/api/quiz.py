# app/routes/quiz.py
from fastapi import APIRouter, Query, Depends, HTTPException
from supabase import Client
from app.schemas.schemas import *
from app.core.supabase_client import get_supabase

router = APIRouter()

@router.get("/quizes", response_model=QuizResponse)
def get_random_quizes(count: int = Query(1, ge=1, le=10), supabase: Client = Depends(get_supabase)):
  try:
    quizes = get_random_quizes(supabase, limit=count)

    if not quizes:
      raise HTTPException(404, detail="퀴즈를 찾을 수 없습니다.")
    
    if count == 1:
      quiz = quizes[0]
      return QuizResponse(id = quiz['id'], title = quiz['title'], content = quiz['content'], correct = quiz['correct'])
    
    return {"quizes": quizes}
  except Exception as e:
    raise HTTPException(500, detail="퀴즈 조회 중 오류가 발생했습니다.")