# app/routes/courses.py
from fastapi import APIRouter, Query, Depends, HTTPException
from supabase import Client
from app.schemas.schemas import *
from app.services.course_service import get_mbti
from app.core.supabase_client import get_supabase

router = APIRouter()

@router.get("/courses", response_model=CourseListResponse)
def get_courses(
    user_id: int = Query(..., description="사용자 ID"),
    supabase: Client = Depends(get_supabase)
):
    """
    사용자의 MBTI를 기반으로 코스를 추천합니다.
    """
    # 사용자 MBTI 조회
    mbti = get_mbti(user_id, supabase)
    
    if not mbti:
        raise HTTPException(
            status_code=404, 
            detail="User not found or MBTI not set"
        )
    
    # TODO: mbti를 사용하여 코스 추천 로직 구현
    return CourseListResponse(courses=[])

@router.post("/courses/{course_id}/{user_id}", response_model=Message)
def complete_course(course_id: int, user_id: int):
    # 코스 완료 로직
    return {
        "message" : "코스 완료! 저장 되었습니다!"
    }


# review
@router.post("/reviews/{course_id}/{user_id}", response_model=Message)
def create_review(course_id: int, user_id: int, body: ReviewItem):
    # 리뷰 등록 로직
    return {
        "message" : "리뷰 등록 완료!"
    }

@router.put("/reviews/{course_id}/{user_id}", response_model=Message)
def update_review(course_id: int, user_id: int, body: ReviewItem):
    # 리뷰 수정 로직
    return {
        "message" : "리뷰 수정 완료!"
    }

@router.delete("/reviews/{course_id}/{user_id}", response_model=Message)
def delete_review(course_id: int, user_id: int):
    # 리뷰 삭제 로직
    return {
        "message" : "리뷰 삭제 완료!"
    }

@router.get("/reviews/{course_id}", response_model=ReviewListReponse)
def get_reviews(course_id: int):
    # 리뷰 조회 로직
    return {
        
    }