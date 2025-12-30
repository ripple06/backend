# app/routes/course.py
from fastapi import APIRouter, Query, Depends, HTTPException, Body
from supabase import Client
from app.schemas.schemas import *
from app.services.course_service import *
from app.services.ai_service import ai_service
from app.core.supabase_client import get_supabase
from typing import Optional, Dict, Any

router = APIRouter()

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

@router.post("/courses/ai-recommend", response_model=CourseListResponse)
async def get_ai_course_recommendations(
    location: str = Body(...),
    sea_emotion: Dict[str, str] = Body(...),
    mbti: Optional[str] = Body(None),
    ecosystem_data: Optional[Dict[str, Any]] = Body(None),
    user_preferences: Optional[Dict[str, Any]] = Body(None),
    limit: int = Body(5)
):
  """
  AI를 사용하여 코스를 추천합니다.
  - location: 지역명 (예: "사하구", "기장군")
  - sea_emotion: 바다 기분 분석 결과 {"emotion": "🌊", "name": "평온한 미소"}
  - mbti: 사용자 MBTI (선택)
  - ecosystem_data: 해양 생태계 데이터 (선택)
  - user_preferences: 사용자 선호도 (선택)
  - limit: 추천 코스 개수 (기본값: 5)
  """
  try:
    # AI 서비스를 사용하여 코스 추천
    ai_courses = ai_service.generate_course_recommendations(
        location_name=location,
        mbti=mbti or "ISFP",  # 기본값
        sea_emotion=sea_emotion,
        ecosystem_data=ecosystem_data,
        user_preferences=user_preferences,
        limit=limit
    )
    
    # AI 응답 형식을 Course 스키마에 맞게 변환
    courses = []
    for ai_course in ai_courses:
        # path에서 startPoint와 endPoint 추출
        path = ai_course.get("path", [])
        if len(path) >= 2:
            start_point = StartPoint(lat=path[0]["lat"], lng=path[0]["lng"])
            end_point = EndPoint(lat=path[-1]["lat"], lng=path[-1]["lng"])
        else:
            # 기본값
            start_point = StartPoint(lat=35.1796, lng=129.0756)
            end_point = EndPoint(lat=35.1800, lng=129.0760)
        
        course = Course(
            courseId=ai_course.get("courseId", 0),
            name=ai_course.get("name", ""),
            totalDistance=ai_course.get("totalDistance", 5.0),
            color=ai_course.get("color", "#7364fe"),
            startPoint=start_point,
            endPoint=end_point
        )
        courses.append(course)
    
    return CourseListResponse(courses=courses)
  except Exception as e:
    raise HTTPException(500, detail=f"AI 코스 추천 중 오류가 발생했습니다: {str(e)}")

@router.get("/courses/{course_id}", response_model=Course)
def get_course_detail(course_id: int, supabase: Client = Depends(get_supabase)):
  """
  특정 코스의 상세 정보를 조회합니다.
  """
  try:
    course = get_course_by_id_service(course_id, supabase)
    
    if not course:
      raise HTTPException(404, detail="코스를 찾을 수 없습니다.")
    
    return course
  except HTTPException:
    raise
  except Exception as e:
    raise HTTPException(500, detail="코스 상세 조회 중 오류가 발생했습니다.")

@router.post("/courses/{course_id}/{user_id}", response_model=Message)
def complete_course(course_id: int, user_id: int, supabase: Client = Depends(get_supabase)):
  try:
    result = complete_course_service(user_id, course_id, supabase)
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
    raise HTTPException(400, detail=str(e))
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
      return ReviewListReponse(reviews=review_items)
    except Exception as e:
      raise HTTPException(500, detail="리뷰 조회 중 오류가 발생했습니다.")