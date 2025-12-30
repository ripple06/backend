from fastapi import APIRouter, HTTPException
import requests
from datetime import datetime
from app.schemas.schemas import *

router = APIRouter()

# 캐시 저장소 (실제로는 Redis나 DB 사용 권장)
emotion_cache = {}

def get_sea_data(location: str):
    """
    외부 해양 데이터 API 호출
    (기상청 해양기상정보 API 등)
    """

    try:
        response = requests.get(
            "https://www.data.go.kr/data/15033708/openapi.do",
            params={"location": location, "api_key": "ed3cbf2791458ab07d899ba85e16650e75c35184993c1f7a392d742dc4594c20"},
            timeout=3
        )
        response.raise_for_status()
        return response.json()
    except Exception:
        # API 호출 실패 시 (또는 테스트용) 임시 데이터 반환
        return {
            "wavesHeight": 1.2,
            "windSpeed": 8.5
        }
    

def analyze_sea_emotion(sea_data: dict) -> dict:
    """
    해양 데이터를 분석하여 바다의 성격 판단
    """
    waves = sea_data["wavesHeight"]
    wind = sea_data["windSpeed"]
    
    # 바다 상태에 따른 감정 분류
    if waves < 0.5 and wind < 5:
        return {
            "emotion": "🫧",
            "name": "평온한 바다",
            "message": "산책하기 좋은 날이에요"
        }
    elif waves < 1.0 and wind < 8:
        return {
            "emotion": "🔅",
            "name": "화창한 바다",
            "message": "해양 스포츠 즐기기 좋은 날이에요"
        }
    elif waves < 2.0 and wind < 12:
        return {
            "emotion": "🌊",
            "name": "활기찬 바다",
            "message": "쉬어가도록 해요"
        }
    else:
        return {
            "emotion": "💪",
            "name": "거친 바다",
            "message": "안전에 주의하세요"
        }

@router.get("/seaemotion", response_model=SeaEmotionResponse)
async def get_sea_emotion(location: str):
    """
    바다 성격 불러오기 API
    - 지역을 입력받아 해양 데이터를 분석하고 바다의 성격 반환
    """
    try:
        # 캐시 확인 (10분 이내 데이터가 있으면 재사용)
        cache_key = f"{location}_{datetime.now().strftime('%Y%m%d%H%M')[:11]}"  # 10분 단위
        
        if cache_key in emotion_cache:
            return emotion_cache[cache_key]
        
        # 1. 외부 API에서 해양 데이터 조회
        sea_data = get_sea_data(location)
        
        # 2. 해양 데이터 분석하여 바다 성격 판단
        emotion_result = analyze_sea_emotion(sea_data)
        
        # 3. 응답 생성
        response = {
            "emotion": emotion_result["emotion"],
            "name": emotion_result["name"],
            "message": emotion_result["message"]
        }
        
        # 캐시 저장
        emotion_cache[cache_key] = response
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"바다 성격 분석 실패: {str(e)}")