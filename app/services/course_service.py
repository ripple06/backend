# app/services/course_service.py
from supabase import Client
from app.schemas.location import SeaEmotion

def recommend_course(mbti: str, sea_emotion: SeaEmotion, supabase: Client):
    """
    사용자의 MBTI와 바다 분석 결과를 기반으로 코스를 추천하는 로직 (Supabase 버전).
    - 실제 구현 시, MBTI와 감정 상태에 따라 코스를 필터링하거나
      점수를 매겨 가장 적합한 코스를 찾는 복잡한 로직이 필요합니다.
    - 현재는 등록된 코스 중 첫 번째 코스를 반환하는 예시입니다.
    """
    try:
        # 예시: 단순히 첫 번째 코스를 추천
        response = supabase.table("courses").select("*").limit(1).single().execute()
        return response.data
    except Exception:
        # 코스가 하나도 없을 경우 single()에서 오류 발생 가능
        return None
