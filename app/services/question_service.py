from supabase import Client
from app.schemas.schemas import QuestionItem
from typing import Optional, List
from datetime import datetime

def create_question_service(user_id: int, course_id: int, question_data: QuestionItem, supabase: Client) -> dict:
    """
    새로운 질문을 생성합니다.
    """
    try:
        # 사용자가 존재하는지 확인
        user = supabase.table('users')\
            .select('id')\
            .eq('id', user_id)\
            .execute()
        
        if not user.data or len(user.data) == 0:
            raise ValueError("존재하지 않는 사용자입니다.")
        
        # 코스가 존재하는지 확인
        course = supabase.table('courses')\
            .select('id')\
            .eq('id', course_id)\
            .execute()
        
        if not course.data or len(course.data) == 0:
            raise ValueError("존재하지 않는 코스입니다.")
        
        # 질문 데이터 준비
        question_insert = {
            'userId': user_id,
            'courseId': course_id,
            'title': question_data.title,
            'content': question_data.content,
            'created_at': datetime.now().isoformat()
        }
        
        # 질문 삽입
        response = supabase.table('questions')\
            .insert(question_insert)\
            .execute()
        
        if response.data and len(response.data) > 0:
            return response.data[0]
        else:
            raise Exception("질문 생성에 실패했습니다.")
            
    except Exception as e:
        print(f"질문 생성 실패: {e}")
        raise e

def get_question_service(course_id: int, supabase: Client) -> Optional[dict]:
    """
    특정 코스의 가장 최근 질문을 조회합니다.
    """
    try:
        response = supabase.table('questions')\
            .select('*, users(id, name)')\
            .eq('courseId', course_id)\
            .order('created_at', desc=True)\
            .limit(1)\
            .execute()
        
        if response.data and len(response.data) > 0:
            return response.data[0]
        return None
            
    except Exception as e:
        print(f"질문 조회 실패: {e}")
        return None

def get_question_list_service(course_id: int, supabase: Client) -> List[dict]:
    """
    특정 코스의 모든 질문 목록을 조회합니다.
    """
    try:
        response = supabase.table('questions')\
            .select('*, users(id, name)')\
            .eq('courseId', course_id)\
            .order('created_at', desc=True)\
            .execute()
        
        return response.data if response.data else []
            
    except Exception as e:
        print(f"질문 목록 조회 실패: {e}")
        return []
    
def answer_question_service(question_id: int, answer: str, supabase: Client) -> dict:
    """
    질문에 답변을 저장합니다.
    """
    try:
        question = supabase.table('questions').select('*').eq('id', question_id).execute()
        if not question.data or len(question.data) == 0:
            raise ValueError("질문을 찾을 수 없습니다.")

        response = supabase.table('questions')\
            .update({'answer': answer, 'answered_at': datetime.now().isoformat()})\
            .eq('id', question_id)\
            .execute()
        
        return response.data[0] if response.data else {}
    except Exception as e:
        print(f"질문 답변 실패: {e}")
        raise e