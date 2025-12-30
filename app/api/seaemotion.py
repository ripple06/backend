from fastapi import APIRouter, HTTPException, Depends
from supabase import Client
from app.schemas.schemas import SeaEmotionResponse
from app.services.seamotion_service import *
from app.core.supabase_client import get_supabase

router = APIRouter()

@router.get("/seaemotion", response_model=SeaEmotionResponse)
async def get_sea_emotion(location: str, supabase: Client = Depends(get_supabase)):
    """
    바다 성격 불러오기 API
    - 지역을 입력받아 해양 데이터를 분석하고 바다의 성격 반환
    """
    try:
        # API Key (실제로는 환경변수 사용 권장)
        api_key = "ed3cbf2791458ab07d899ba85e16650e75c35184993c1f7a392d742dc4594c20"
        
        emotion_result = get_sea_emotion_service(location, api_key, supabase)
        
        # main 스키마에 맞게 변환 (emotion, name 필드만)
        return SeaEmotionResponse(
            emotion=emotion_result.get("emotion", "🌊"),
            name=emotion_result.get("name", "바다")
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"바다 성격 분석 실패: {str(e)}")