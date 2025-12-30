# app/api/question.py
from fastapi import APIRouter, HTTPException, Depends, Query
from supabase import Client
from app.schemas.schemas import *
from app.services.question_service import (
    create_question_service,
    get_question_service,
    get_question_list_service,
    answer_question_service
)
from app.core.supabase_client import get_supabase
from typing import Optional

router = APIRouter()

def _safe_int(val):
    """
    val을 안전하게 int로 변환. 변환 실패하면 None 반환.
    """
    if val is None:
        return None
    try:
        return int(val)
    except Exception:
        try:
            s = str(val).strip()
            return int(s) if s.isdigit() else None
        except Exception:
            return None

# 4. 질문 대답하기 API
@router.post("/questions/{question_id}/answer/{user_id}", response_model=Message)
async def answer_question(
    question_id: int,
    answer: QuestionAnswer,
    user_id: int,
    supabase: Client = Depends(get_supabase)
):
    """
    특정 질문에 대한 답변을 저장합니다.
    user_id를 주면 answerId로 저장됩니다.
    """
    try:
        # 실제 서비스 호출 (answerer id 전달)
        result = answer_question_service(question_id, answer.answer, supabase, answerer_id=user_id)
        return Message(message="질문 답변 성공!")
    except ValueError as e:
        raise HTTPException(404, detail=str(e))
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(500, detail="질문 답변 중 오류가 발생했습니다.")


# 1. 질문 생성 API
@router.post("/questions/{course_id}/{user_id}", response_model=Message)
async def create_question(
    course_id: int, 
    user_id: int, 
    question: QuestionItem,
    supabase: Client = Depends(get_supabase)
):
    """
    코스 탐방 완료 후 다음 사람에게 질문 생성
    """
    try:
        result = create_question_service(user_id, course_id, question, supabase)
        return Message(message="당신의 질문이 생성되었습니다!")
    except ValueError as e:
        raise HTTPException(404, detail=str(e))
    except Exception:
        raise HTTPException(500, detail="질문 생성 중 오류가 발생했습니다.")


# 2. 질문 단일 보기 API
@router.get("/questions/{course_id}", response_model=QuestionItem)
async def get_question(
    course_id: int,
    supabase: Client = Depends(get_supabase)
):
    """
    특정 코스의 가장 최근 질문 조회
    """
    try:
        question = get_question_service(course_id, supabase)
        
        if not question:
            raise HTTPException(404, detail="질문을 찾을 수 없습니다.")
        
        return QuestionItem(
            id=_safe_int(question.get('id')),
            title=question.get('title'),
            content=question.get('content'),
            answer=question.get('answer') if question.get('answer') is not None else None,
            answerId=_safe_int(question.get('answerId'))
        )
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(500, detail="질문 조회 중 오류가 발생했습니다.")


# 3. 질문 목록 보기 API
@router.get("/questions/{course_id}/list", response_model=QuestionListResponse)
async def get_question_list(
    course_id: int,
    supabase: Client = Depends(get_supabase)
):
    """
    특정 코스의 모든 질문 목록 조회
    """
    try:
        questions = get_question_list_service(course_id, supabase)
        
        question_items = [
            QuestionItem(
                id=_safe_int(q.get('id')),
                title=q.get('title'),
                content=q.get('content'),
                answer=q.get('answer') if q.get('answer') is not None else None,
                answerId=_safe_int(q.get('answerId'))
            )
            for q in questions
        ]
        
        return QuestionListResponse(questions=question_items)
    except Exception:
        raise HTTPException(500, detail="질문 목록 조회 중 오류가 발생했습니다.")
