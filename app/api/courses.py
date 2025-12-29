# app/api/courses.py
from fastapi import APIRouter, Depends, HTTPException, Body
from supabase import Client
from typing import List, Optional

from app.schemas import course as course_schema
from app.schemas import review as review_schema
from app.services import course_service, ocean_service
from app.core.supabase_client import get_supabase
from app.api.users import get_current_user
from supabase import User as SupabaseUser

router = APIRouter(
    prefix="/courses",
    tags=["Courses & Reviews"],
)

@router.post("/recommend", response_model=Optional[course_schema.Course])
def get_course_recommendation(
    location_id: int, 
    mbti: str = Body(..., embed=True),
    supabase: Client = Depends(get_supabase),
):
    """
    선택한 지역과 MBTI를 기반으로 코스를 추천받습니다.
    """
    # 1. 지역 정보 확인
    location_response = supabase.table("locations").select("name").eq("id", location_id).single().execute()
    if not location_response.data:
        raise HTTPException(status_code=404, detail="Location not found")

    # 2. 바다 상태 분석
    sea_emotion = ocean_service.analyze_sea_conditions(location_response.data['name'])

    # 3. 코스 추천 서비스 호출
    recommended_course = course_service.recommend_course(mbti, sea_emotion, supabase)
    
    if not recommended_course:
        raise HTTPException(status_code=404, detail="No suitable course found")
        
    return recommended_course

@router.get("/{course_id}", response_model=course_schema.Course)
def get_course_details(course_id: int, supabase: Client = Depends(get_supabase)):
    """
    특정 코스의 상세 정보를 리뷰, 질문과 함께 가져옵니다.
    """
    response = supabase.table("courses").select("*, reviews(*), post_course_questions(*)").eq("id", course_id).single().execute()
    if not response.data:
        raise HTTPException(status_code=404, detail="Course not found")
    
    # Supabase는 questions 테이블을 'post_course_questions'로 자동 참조합니다. 스키마 필드명과 맞춰줍니다.
    response.data['questions'] = response.data.pop('post_course_questions', [])

    return response.data

@router.post("/reviews", response_model=review_schema.Review)
def create_course_review(
    review: review_schema.ReviewCreate,
    supabase: Client = Depends(get_supabase),
    current_user: SupabaseUser = Depends(get_current_user),
):
    """
    특정 코스에 대한 리뷰를 작성합니다.
    """
    # 리뷰 데이터에 현재 사용자 ID 추가
    review_data = review.model_dump()
    review_data['owner_id'] = str(current_user.id) # UUID를 문자열로 변환

    response = supabase.table("reviews").insert(review_data).execute()
    
    if not response.data:
        raise HTTPException(status_code=500, detail="Failed to create review")

    return response.data[0]

@router.post("/questions", response_model=course_schema.PostCourseQuestion)
def create_post_course_question(
    question: course_schema.PostCourseQuestionCreate,
    supabase: Client = Depends(get_supabase),
    current_user: SupabaseUser = Depends(get_current_user)
):
    """
    코스 완료 후, 다음 사람을 위한 질문을 남깁니다.
    """
    question_data = question.model_dump()
    question_data['owner_id'] = str(current_user.id)

    response = supabase.table("post_course_questions").insert(question_data).execute()

    if not response.data:
        raise HTTPException(status_code=500, detail="Failed to create question")
        
    return response.data[0]