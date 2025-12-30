# app/routes/course.py
from fastapi import APIRouter, Query, Depends, HTTPException
from supabase import Client
from app.schemas.schemas import *
from app.services.course_service import *
from app.core.supabase_client import get_supabase

router = APIRouter()

def _parse_int_from_path(name: str, value: str) -> int:
    """
    최소 변경: 경로 파라미터를 안전하게 int로 변환.
    실패하면 HTTPException(400) 발생.
    """
    try:
        return int(value)
    except Exception:
        raise HTTPException(status_code=400, detail=f"Path parameter '{name}' must be an integer. Received: {value}")

@router.get("/courses", response_model=CourseListResponse)
def get_courses(user_id: int = Query(...), supabase: Client = Depends(get_supabase)):
  """
  사용자의 MBTI + 바다 분석 결과를 기반으로 코스를 추천합니다.
  """
  try:
    # 사용자 MBTI 조회
    mbti = get_mbti(user_id, supabase)
    
    if not mbti:
      raise HTTPException(
        status_code=404, 
        detail="유저가 없거나 mbti가 설정 안됨"
      )
    
    # 코스 추천 로직 구현
    courses = get_all_courses_service(supabase)
    
    return CourseListResponse(courses=courses)
  except HTTPException:
    raise
  except Exception as e:
    raise HTTPException(500, detail="코스 조회 중 오류가 발생했습니다.")

@router.get("/courses/{course_id}", response_model=Course)
def get_course_detail(course_id: str, supabase: Client = Depends(get_supabase)):
  """
  특정 코스의 상세 정보를 조회합니다.
  """
  try:
    cid = _parse_int_from_path('course_id', course_id)
    course = get_course_by_id_service(cid, supabase)
    
    if not course:
      raise HTTPException(404, detail="코스를 찾을 수 없습니다.")
    
    return course
  except HTTPException:
    raise
  except Exception as e:
    raise HTTPException(500, detail="코스 상세 조회 중 오류가 발생했습니다.")

@router.post("/courses/{course_id}/{user_id}", response_model=Message)
def complete_course(course_id: str, user_id: str, supabase: Client = Depends(get_supabase)):
  """
  변경: course_id, user_id를 str로 받고 내부에서 int로 변환
  """
  try:
    cid = _parse_int_from_path('course_id', course_id)
    uid = _parse_int_from_path('user_id', user_id)
    result = complete_course_service(uid, cid, supabase)
    return Message(message="코스 완료! 저장 되었습니다!")
  except ValueError as e:
    raise HTTPException(404, detail=str(e))
  except HTTPException:
    raise
  except Exception as e:
    raise HTTPException(500, detail="코스 완료 처리 중 오류가 발생했습니다.")


# review
@router.post("/reviews/{course_id}/{user_id}", response_model=Message)
def create_review(course_id: str, user_id: str, body: ReviewItem, supabase: Client = Depends(get_supabase)):
  try:
    cid = _parse_int_from_path('course_id', course_id)
    uid = _parse_int_from_path('user_id', user_id)
    create_review_service(uid, cid, body, supabase)
    return Message(message="리뷰 등록 완료!")
  except ValueError as e:
    raise HTTPException(400, detail=str(e))
  except HTTPException:
    raise
  except Exception as e:
    raise HTTPException(500, detail="리뷰 등록 중 오류가 발생했습니다.")

@router.put("/reviews/{course_id}/{user_id}", response_model=Message)
def update_review(course_id: str, user_id: str, body: ReviewItem, supabase: Client = Depends(get_supabase)):
  try:
    cid = _parse_int_from_path('course_id', course_id)
    uid = _parse_int_from_path('user_id', user_id)
    update_review_service(uid, cid, body, supabase)
    return Message(message="리뷰 수정 완료!")
  except ValueError as e:
    raise HTTPException(404, detail=str(e))
  except HTTPException:
    raise
  except Exception as e:
    raise HTTPException(500, detail="리뷰 수정 중 오류가 발생했습니다.")

@router.delete("/reviews/{course_id}/{user_id}", response_model=Message)
def delete_review(course_id: str, user_id: str, supabase: Client = Depends(get_supabase)):
    try:
      cid = _parse_int_from_path('course_id', course_id)
      uid = _parse_int_from_path('user_id', user_id)
      delete_review_service(uid, cid, supabase)
      return Message(message="리뷰 삭제 완료!")
    except ValueError as e:
      raise HTTPException(404, detail=str(e))
    except HTTPException:
      raise
    except Exception as e:
      raise HTTPException(500, detail="리뷰 삭제 중 오류가 발생했습니다.")

@router.get("/reviews/{course_id}", response_model=ReviewListReponse)
def get_reviews(course_id: str, supabase: Client = Depends(get_supabase)):
    try:
      cid = _parse_int_from_path('course_id', course_id)
      reviews = get_reviews_by_course(cid, supabase)
      review_items = [
        ReviewItem(
          title=review["title"],
          keyword=review["keyword"],
          rating=review["rating"],
          content=review["content"]
        )
        for review in reviews
      ]
      return ReviewListReponse(reviews=review_items)
    except HTTPException:
      raise
    except Exception as e:
      raise HTTPException(500, detail="리뷰 조회 중 오류가 발생했습니다.")