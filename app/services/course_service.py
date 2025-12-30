# app/services/course_service.py
from supabase import Client
from app.schemas.schemas import *
from typing import Optional, List
from datetime import datetime

def get_mbti(user_id: int, supabase: Client) -> Optional[str]:
    """
    사용자의 MBTI를 조회합니다.
    """
    try:
        response = supabase.table('users').select('mbti').eq('id', user_id).execute()
        
        if response.data and len(response.data) > 0:
            return response.data[0]['mbti']
        return None
    except Exception as e:
        print(f"MBTI 찾기 실패 > {user_id}: {e}")
        return None

def recommend_course(mbti: str, sea_emotion: SeaEmotionRequest, supabase: Client):
    """
    MBTI와 바다 감정을 기반으로 코스를 추천합니다.
    """
    # TODO: 실제 추천 로직 구현
    pass

def create_review_service(user_id: int, course_id: int, review_data: ReviewItem, supabase: Client) -> dict:
    """
    새로운 리뷰를 생성합니다.
    """
    try:
        # 이미 리뷰가 있는지 확인
        existing = supabase.table('reviews')\
            .select('id')\
            .eq('userId', user_id)\
            .eq('courseId', course_id)\
            .execute()
        
        if existing.data and len(existing.data) > 0:
            raise ValueError("이미 이 코스에 대한 리뷰를 작성하셨습니다.")
        
        # 리뷰 데이터 준비
        review_insert = {
            'userId': user_id,
            'courseId': course_id,
            'title': review_data.title,
            'keyword': review_data.keyword,
            'rating': review_data.rating,
            'content': review_data.content,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        # 리뷰 삽입
        response = supabase.table('reviews').insert(review_insert).execute()
        
        if response.data and len(response.data) > 0:
            return response.data[0]
        else:
            raise Exception("리뷰 생성에 실패했습니다.")
            
    except Exception as e:
        print(f"후기 생성 실패: {e}")
        raise e

def update_review_service(user_id: int, course_id: int, review_data: ReviewItem, supabase: Client) -> dict:
    """
    기존 리뷰를 수정합니다.
    """
    try:
        # 리뷰 존재 여부 확인
        existing = supabase.table('reviews')\
            .select('id')\
            .eq('userId', user_id)\
            .eq('courseId', course_id)\
            .execute()
        
        if not existing.data or len(existing.data) == 0:
            raise ValueError("수정할 리뷰가 존재하지 않습니다.")
        
        # 리뷰 업데이트 데이터 준비
        review_update = {
            'title': review_data.title,
            'keyword': review_data.keyword,
            'rating': review_data.rating,
            'content': review_data.content,
            'updated_at': datetime.now().isoformat()
        }
        
        # 리뷰 업데이트
        response = supabase.table('reviews')\
            .update(review_update)\
            .eq('userId', user_id)\
            .eq('courseId', course_id)\
            .execute()
        
        if response.data and len(response.data) > 0:
            return response.data[0]
        else:
            raise Exception("리뷰 수정에 실패했습니다.")
            
    except Exception as e:
        print(f"후기 수정 실패: {e}")
        raise e

def delete_review_service(user_id: int, course_id: int, supabase: Client) -> bool:
    """
    리뷰를 삭제합니다.
    """
    try:
        # 리뷰 존재 여부 확인
        existing = supabase.table('reviews')\
            .select('id')\
            .eq('userId', user_id)\
            .eq('courseId', course_id)\
            .execute()
        
        if not existing.data or len(existing.data) == 0:
            raise ValueError("삭제할 리뷰가 존재하지 않습니다.")
        
        # 리뷰 삭제
        response = supabase.table('reviews')\
            .delete()\
            .eq('userId', user_id)\
            .eq('courseId', course_id)\
            .execute()
        
        return True
            
    except Exception as e:
        print(f"후기 삭제 실패: {e}")
        raise e

def get_reviews_by_course(course_id: int, supabase: Client) -> List[dict]:
    """
    특정 코스의 모든 리뷰를 조회합니다.
    """
    try:
        response = supabase.table('reviews')\
            .select('*, users(id, name)')\
            .eq('courseId', course_id)\
            .order('created_at', desc=True)\
            .execute()
        
        return response.data if response.data else []
            
    except Exception as e:
        print(f"후기 조회 실패: {e}")
        return []

def complete_course_service(user_id: int, course_id: int, supabase: Client) -> dict:
    """
    코스 완료를 기록합니다.
    (완료 기록을 위한 별도 테이블이 필요할 수 있습니다)
    """
    try:
        # 실제로는 course_completions 같은 테이블이 필요합니다
        # 여기서는 임시로 questions 테이블에 완료 질문을 생성하는 것으로 가정
        
        # 코스가 존재하는지 확인
        course = supabase.table('courses')\
            .select('id, name')\
            .eq('id', course_id)\
            .execute()
        
        if not course.data or len(course.data) == 0:
            raise ValueError("존재하지 않는 코스입니다.")
        
        # 사용자가 존재하는지 확인
        user = supabase.table('users')\
            .select('id, name')\
            .eq('id', user_id)\
            .execute()
        
        if not user.data or len(user.data) == 0:
            raise ValueError("존재하지 않는 사용자입니다.")
        
        return {
            "user_id": user_id,
            "course_id": course_id,
            "completed_at": datetime.now().isoformat()
        }
            
    except Exception as e:
        print(f"코스 기록 실패: {e}")
        raise e