# app/routes/courses.py
from fastapi import APIRouter, Query, Depends, HTTPException
from supabase import Client
from app.schemas.schemas import *
from app.services.course_service import *
from app.core.supabase_client import get_supabase

router = APIRouter()

@router.get("/courses", response_model=CourseListResponse)
def get_courses(user_id: int = Query(...), supabase: Client = Depends(get_supabase)):
  """
  사용자의 MBTI + 바다 분석 결과를 기반으로 코스를 추천합니다.
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
def complete_course(course_id: int, user_id: int, supabase: Client = Depends(get_supabase)):
  try:
    result = complete_course_service(course_id, user_id, supabase)
    return Message(message="코스 완료! 저장 되었습니다!")
  except ValueError as e:
    raise HTTPException(404, detail=str(e))
  except Exception as e:
    raise HTTPException(500, detail="코스 완료 처리 중 오류가 발생했습니다.")


# review
@router.post("/reviews/{course_id}/{user_id}", response_model=Message)
def create_review(course_id: int, user_id: int, body: ReviewItem, supabase: Client = Depends(get_supabase)):
  try:
    create_review_service(user_id, course_id, body, supabase)
    return Message(message="리뷰 등록 완료!")
  except ValueError as e:
    raise HTTPException(404, detail=str(e))
  except Exception as e:
    raise HTTPException(500, detail="리뷰 등록 중 오류가 발생했습니다.")

@router.put("/reviews/{course_id}/{user_id}", response_model=Message)
def update_review(course_id: int, user_id: int, body: ReviewItem, supabase: Client = Depends(get_supabase)):
  try:
    update_review_service(user_id, course_id, body, supabase)
    return Message(message="리뷰 수정 완료!")
  except ValueError as e:
    raise HTTPException(404, detail=str(e))
  except Exception as e:
    raise HTTPException(500, detail="리뷰 수정 중 오류가 발생했습니다.")

@router.delete("/reviews/{course_id}/{user_id}", response_model=Message)
def delete_review(course_id: int, user_id: int, supabase: Client = Depends(get_supabase)):
    try:
      delete_review_service(user_id, course_id, supabase)
      return Message(message="리뷰 삭제 완료!")
    except ValueError as e:
      raise HTTPException(404, detail=str(e))
    except Exception as e:
      raise HTTPException(500, detail="리뷰 삭제 중 오류가 발생했습니다.")

@router.get("/reviews/{course_id}", response_model=ReviewListReponse)
def get_reviews(course_id: int, supabase: Client = Depends(get_supabase)):
    try:
      reviews = get_reviews_by_course(course_id, supabase)
      review_items = [
        ReviewItem(
          title=review["title"],
          keyword=review["keyword"],
          rating=review["rating"],
          content=review["content"]
        )
        for review in reviews
      ]
      return ReviewListReponse(reviews = review_items)
    except Exception as e:
      raise HTTPException(500, detail="리뷰 조회 중 오류가 발생했습니다.")