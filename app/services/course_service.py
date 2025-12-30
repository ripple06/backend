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

def _try_select_variants(table_name: str, supabase: Client, variants: list, filters: dict = None):
    """
    select 문자열 표기(큰따옴표 포함/미포함 등)를 여러가지로 시도해서 데이터가 반환되는 첫 결과를 리턴합니다.
    filters: {'field': value, ...} 형태로 eq 필터들을 전달 가능 (선택).
    """
    for sel in variants:
        try:
            q = supabase.table(table_name).select(sel)
            if filters:
                for k, v in filters.items():
                    q = q.eq(k, v)
            resp = q.execute()
            if getattr(resp, "data", None):
                return resp
        except Exception:
            # 시도 중 에러나 실패는 무시하고 다음 표기법 시도
            continue
    return None

def _try_order_variants(table, select_str, supabase: Client, course_id):
    """
    order 필드 표기도 여러가지로 시도해서 경로 데이터를 반환합니다.
    """
    order_variants = ['"order"', 'order']
    for ord_field in order_variants:
        try:
            resp = supabase.table(table)\
                .select(select_str)\
                .eq('courseId', course_id)\
                .order(ord_field, asc=True)\
                .execute()
            if getattr(resp, "data", None):
                return resp
        except Exception:
            continue
    # 마지막으로 order 없이 그냥 select 만 시도
    try:
        resp = supabase.table(table).select(select_str).eq('courseId', course_id).execute()
        if getattr(resp, "data", None):
            return resp
    except Exception:
        pass
    return None

def get_all_courses_service(supabase: Client) -> List[dict]:
    """
    모든 코스를 조회합니다. 코스 전체 경로(path)를 포함합니다.
    여러 select 표기법을 시도하여 데이터가 정상적으로 반환되도록 합니다.
    """
    try:
        select_variants = ['id, name, "totalDistance"', 'id, name, totalDistance', '*']
        resp = _try_select_variants('courses', supabase, select_variants)
        if not resp or not getattr(resp, "data", None):
            # 데이터가 없으면 빈 리스트 반환
            return []

        courses = []
        for course in resp.data:
            # 경로 조회: order 표기법을 여러가지로 시도
            paths_resp = _try_order_variants('course_paths', 'latitude, longitude', supabase, course.get('id'))
            paths = [
                {"lat": float(p['latitude']), "lng": float(p['longitude'])}
                for p in (paths_resp.data if paths_resp and getattr(paths_resp, "data", None) else [])
            ]

            courses.append({
                'courseId': course.get('id'),
                'name': course.get('name'),
                'totalDistance': course.get('totalDistance'),
                'color': COMMON_COURSE_COLOR,
                'paths': paths
            })

        return courses
    except Exception as e:
        print(f"코스 목록 조회 실패: {e}")
        return []

def get_course_by_id_service(course_id: int, supabase: Client) -> Optional[dict]:
    """
    특정 코스의 상세 정보를 조회합니다. 여러 select 표기법과 order 표기를 시도합니다.
    """
    try:
        select_variants = ['id, name, "totalDistance"', 'id, name, totalDistance', '*']
        resp = _try_select_variants('courses', supabase, select_variants, filters={'id': course_id})
        if not resp or not getattr(resp, "data", None) or len(resp.data) == 0:
            return None

        course = resp.data[0]

        paths_resp = _try_order_variants('course_paths', 'latitude, longitude', supabase, course_id)
        paths = [
            {"lat": float(p['latitude']), "lng": float(p['longitude'])}
            for p in (paths_resp.data if paths_resp and getattr(paths_resp, "data", None) else [])
        ]

        return {
            'courseId': course.get('id'),
            'name': course.get('name'),
            'totalDistance': course.get('totalDistance'),
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
        
        # rating을 DB 정수 타입에 맞게 변환 (반올림)
        try:
            rating_int = int(round(float(review_data.rating)))
        except Exception:
            rating_int = int(review_data.rating)  # fallback
        
        # 리뷰 데이터 준비
        review_insert = {
            'userId': user_id,
            'courseId': course_id,
            'title': review_data.title,
            'keyword': review_data.keyword,
            'rating': rating_int,
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
        
        # rating을 DB 정수 타입에 맞게 변환 (반올림)
        try:
            rating_int = int(round(float(review_data.rating)))
        except Exception:
            rating_int = int(review_data.rating)  # fallback
        
        # 리뷰 업데이트 데이터 준비
        review_update = {
            'title': review_data.title,
            'keyword': review_data.keyword,
            'rating': rating_int,
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

def get_completed_courses_service(user_id: int, supabase: Client) -> List[dict]:
    """
    특정 사용자가 완료한 코스 목록을 반환합니다.
    completed_courses 테이블을 조회하여 course_id 목록을 얻은 뒤,
    각 코스의 상세(get_course_by_id_service)을 호출합니다.
    (디버그 로그 및 다양한 키/타입 처리 추가)
    """
    try:
        resp = supabase.table('completed_courses')\
            .select('courseId')\
            .eq('userId', user_id)\
            .execute()
        
        if not resp.data:
            return []
        
        course_ids = []
        for row in resp.data:
            if isinstance(row, dict):
                for key in ('courseId', 'courseid', 'course_id'):
                    if key in row and row[key] is not None:
                        val = row[key]
                        try:
                            course_ids.append(int(val))
                        except Exception:
                            try:
                                course_ids.append(int(str(val).strip()))
                            except Exception:
                                pass
                        break
                else:
                    for v in row.values():
                        if isinstance(v, int):
                            course_ids.append(v)
                            break
                        if isinstance(v, str) and v.strip().isdigit():
                            course_ids.append(int(v.strip()))
                            break
            else:
                try:
                    course_ids.append(int(row))
                except Exception:
                    pass

        course_ids = sorted(set(course_ids))
        if not course_ids:
            return []

        courses = []
        for cid in course_ids:
            course = get_course_by_id_service(cid, supabase)
            if course:
                courses.append(course)

        return courses
    except Exception as e:
        print(f"완료된 코스 조회 실패 (user_id={user_id}): {e}")
        return []

def start_course_service(user_id: int, course_id: int, supabase: Client) -> None:
    """
    코스 시작
    - completed_courses에 기존 기록이 있으면 삭제
    """
    try:
        # 유효성 체크
        course = supabase.table('courses').select('id').eq('id', course_id).execute()
        if not course.data:
            raise ValueError("존재하지 않는 코스입니다.")

        user = supabase.table('users').select('id').eq('id', user_id).execute()
        if not user.data:
            raise ValueError("존재하지 않는 사용자입니다.")

        # 기존 완료 기록 삭제 (있어도 되고 없어도 됨)
        supabase.table('completed_courses')\
            .delete()\
            .eq('userId', user_id)\
            .eq('courseId', course_id)\
            .execute()

    except Exception as e:
        print(f"코스 시작 실패 (user_id={user_id}, course_id={course_id}): {e}")
        raise e

def finish_course_service(user_id: int, course_id: int, supabase: Client) -> dict:
    """
    코스 종료
    - completed_courses에 INSERT
    """
    try:
        # 유효성 체크
        course = supabase.table('courses').select('id').eq('id', course_id).execute()
        if not course.data:
            raise ValueError("존재하지 않는 코스입니다.")

        user = supabase.table('users').select('id').eq('id', user_id).execute()
        if not user.data:
            raise ValueError("존재하지 않는 사용자입니다.")

        insert_data = {
            "userId": user_id,
            "courseId": course_id,
            "completed_at": datetime.now().isoformat()
        }

        # UNIQUE 제약 때문에 중복 시 에러 → start에서 이미 정리됨
        resp = supabase.table('completed_courses').insert(insert_data).execute()

        if not resp.data:
            raise Exception("코스 완료 저장 실패")

        return resp.data[0]

    except Exception as e:
        print(f"코스 종료 실패 (user_id={user_id}, course_id={course_id}): {e}")
        raise e
