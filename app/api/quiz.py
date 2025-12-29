# app/api/quiz.py
from fastapi import APIRouter, Depends, HTTPException
from supabase import Client
from app.core.supabase_client import get_supabase

router = APIRouter(
    prefix="/quiz",
    tags=["Quiz"],
)

@router.get("/random")
def get_random_quiz(supabase: Client = Depends(get_supabase)):
    """
    해양 관련 퀴즈를 랜덤으로 하나 가져옵니다.
    """
    try:
        # TODO: 성능 최적화를 위해 DB에 함수를 만들고 RPC로 호출하는 것이 가장 좋습니다.
        # 예시: response = supabase.rpc('get_random_quiz').execute()
        #
        # 현재는 가장 간단한 방법으로 첫 번째 질문을 가져옵니다.
        response = supabase.table("quiz_questions").select("*").limit(1).single().execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="No quiz questions found")
            
        # 정답 필드는 클라이언트에게 보내지 않는 것이 좋습니다.
        response.data.pop('correct_answer', None)

        return response.data
        
    except Exception as e:
        if "PGRST116" in str(e): # 결과가 없을 때
            raise HTTPException(status_code=404, detail="No quiz questions found")
        raise HTTPException(status_code=500, detail=str(e))