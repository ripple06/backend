# app/services/course_service.py (기존 코드에 추가)
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

COMMON_COURSE_COLOR = "#8FA1FF"

def get_all_courses_service(supabase: Client) -> List[dict]:
    """
    모든 코스를 조회합니다. 코스 전체 경로(path)를 포함합니다.
    """
    try:
        response = supabase.table('courses')\
            .select('id, name, "totalDistance"')\
            .execute()
        
        if not response.data:
            return []

        courses = []
        for course in response.data:
            # 경로 조회
            paths_response = supabase.table('course_paths')\
                .select('latitude, longitude')\
                .eq('courseId', course['id'])\
                .order('"order"', asc=True)\
                .execute()

            paths = [
                {"lat": float(p['latitude']), "lng": float(p['longitude'])}
                for p in paths_response.data
            ] if paths_response.data else []

            courses.append({
                'courseId': course['id'],
                'name': course['name'],
                'totalDistance': course['totalDistance'],
                'color': COMMON_COURSE_COLOR,
                'paths': paths
            })

        return courses
    except Exception as e:
        print(f"코스 목록 조회 실패: {e}")
        return []

def get_course_by_id_service(course_id: int, supabase: Client) -> Optional[dict]:
    """
    특정 코스의 상세 정보를 조회합니다. 코스 전체 경로(path)를 포함합니다.
    """
    try:
        course_response = supabase.table('courses')\
            .select('id, name, "totalDistance"')\
            .eq('id', course_id)\
            .execute()
        
        if not course_response.data or len(course_response.data) == 0:
            return None
        
        course = course_response.data[0]

        paths_response = supabase.table('course_paths')\
            .select('latitude, longitude')\
            .eq('courseId', course_id)\
            .order('"order"', asc=True)\
            .execute()

        paths = [
            {"lat": float(p['latitude']), "lng": float(p['longitude'])}
            for p in paths_response.data
        ] if paths_response.data else []

        return {
            'courseId': course['id'],
            'name': course['name'],
            'totalDistance': course['totalDistance'],
            'color': COMMON_COURSE_COLOR,
            'paths': paths
        }

    except Exception as e:
        print(f"코스 상세 조회 실패: {e}")
        return None


def recommend_course(mbti: str, sea_emotion: SeaEmotionRequest, supabase: Client) -> List[dict]:
    """
    MBTI와 바다 감정을 기반으로 코스를 추천합니다.
    """
    try:
        # TODO: MBTI와 바다 감정에 따른 추천 로직 구현
        # 현재는 모든 코스를 반환
        courses = get_all_courses_service(supabase)
        return courses
    except Exception as e:
        print(f"코스 추천 실패: {e}")
        return []

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
    """
    try:
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
        
        # TODO: 실제로는 course_completions 테이블에 저장하는 로직 추가
        # completion_data = {
        #     'userId': user_id,
        #     'courseId': course_id,
        #     'completed_at': datetime.now().isoformat()
        # }
        # supabase.table('course_completions').insert(completion_data).execute()
        
        return {
            "user_id": user_id,
            "course_id": course_id,
            "completed_at": datetime.now().isoformat()
        }
            
    except Exception as e:
        print(f"코스 기록 실패: {e}")
        raise e