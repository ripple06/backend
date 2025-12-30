# app/routes/quiz.py
from fastapi import APIRouter, Query, Depends, HTTPException
from supabase import Client
from app.schemas.schemas import *
from app.core.supabase_client import get_supabase

router = APIRouter()

@router.get("/quizs", response_model=QuizResponse)
def get_quizs():
  # 퀴즈 불러오기 로직
  return {

  }