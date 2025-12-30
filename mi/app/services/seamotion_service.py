from supabase import Client
import requests
from datetime import datetime
from typing import Optional

def get_sea_data(location: str, api_key: str) -> dict:
    """
    외부 해양 데이터 API 호출
    (기상청 해양기상정보 API 등)
    """
    try:
        response = requests.get(
            "https://www.data.go.kr/data/15033708/openapi.do",
            params={"location": location, "api_key": api_key},
            timeout=3
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"해양 데이터 API 호출 실패: {e}")
        # API 호출 실패 시 임시 데이터 반환
        return {
            "wavesHeight": 1.2,
            "windSpeed": 8.5,
            "watertemperature": 18.74
        }

def analyze_sea_emotion(sea_data: dict) -> dict:
    """
    해양 데이터를 분석하여 바다의 성격 판단
    """
    waves = sea_data.get("wavesHeight", 1.0)
    wind = sea_data.get("windSpeed", 8.0)
    temperature = sea_data.get("watertemperature", 18.0)
    
    # 바다 상태에 따른 감정 분류
     # 1. 잠든 바다
    if waves < 0.3 and wind < 3:
        return {
            "emotion": "😴",
            "name": "잠든 바다",
            "message": "거울처럼 고요해요. 명상하기 완벽한 날이에요"
        }
    
    # 2. 천국 같은 바다
    if temperature > 25 and waves < 0.5 and wind < 5:
        return {
            "emotion": "🏖️",
            "name": "천국 같은 바다",
            "message": "물놀이 최적의 조건이에요! 수영 Go Go!"
        }
    
    # 3. 평온한 바다
    if waves < 0.5 and wind < 5 and temperature > 20:
        return {
            "emotion": "🫧",
            "name": "평온한 바다",
            "message": "산책하기 좋은 날이에요"
        }
    
    # 4. 상쾌한 바다
    if waves < 0.8 and wind < 7 and temperature > 18:
        return {
            "emotion": "☀️",
            "name": "상쾌한 바다",
            "message": "수영하기 딱 좋은 날씨예요"
        }
    
    # 5. 화창한 바다
    if waves < 1.0 and wind < 8 and temperature > 17:
        return {
            "emotion": "🔅",
            "name": "화창한 바다",
            "message": "해양 스포츠 즐기기 좋은 날이에요"
        }
    
    # 6. 서퍼의 바다
    if waves >= 1.2 and waves < 2.0 and wind < 10:
        return {
            "emotion": "🏄",
            "name": "서퍼의 바다",
            "message": "파도타기 최고의 컨디션이에요!"
        }
    
    # 7. 활기찬 바다
    if waves < 1.5 and wind < 10:
        return {
            "emotion": "🌊",
            "name": "활기찬 바다",
            "message": "파도가 살아있어요. 물놀이 조심하세요"
        }
    
    # 8. 바람부는 바다
    if wind >= 12 and wind < 15 and waves < 1.5:
        return {
            "emotion": "💨",
            "name": "바람부는 바다",
            "message": "연날리기 좋은 날이에요. 모자 단단히 잡으세요!"
        }
    
    # 9. 들뜬 바다
    if waves < 2.0 and wind < 12:
        return {
            "emotion": "🌀",
            "name": "들뜬 바다",
            "message": "바람이 제법 불어요. 주의하며 즐기세요"
        }
    
    # 10. 차가운 바다
    if temperature < 15 and waves < 1.5:
        return {
            "emotion": "❄️",
            "name": "차가운 바다",
            "message": "겨울 바다의 고요함. 따뜻하게 입고 산책하세요"
        }
    
    # 11. 흥분한 바다
    if waves < 2.5 and wind < 15:
        return {
            "emotion": "〰️",
            "name": "흥분한 바다",
            "message": "파도가 높아요. 해변가에서만 활동하세요"
        }
    
    # 12. 거친 바다
    if waves < 3.0 and wind < 18:
        return {
            "emotion": "💪",
            "name": "거친 바다",
            "message": "안전에 주의하세요. 입수는 위험해요"
        }
    
    # 13. 험한 바다
    if waves < 3.5 and wind < 20:
        return {
            "emotion": "⚠️",
            "name": "험한 바다",
            "message": "물놀이 금지! 해변 산책 정도만 권장해요"
        }
    
    # 14. 성난 바다
    if waves < 4.0 or wind < 25:
        return {
            "emotion": "⛈️",
            "name": "성난 바다",
            "message": "입수 금지! 해변에서도 안전거리를 유지하세요"
        }
    
    # 15. 광폭한 바다 (그 외 모든 경우)
    return {
        "emotion": "🌊⚡",
        "name": "광폭한 바다",
        "message": "매우 위험해요. 해안가 접근을 자제하세요"
    }


def get_cached_emotion(location: str, supabase: Client) -> Optional[dict]:
    """
    데이터베이스에서 캐시된 바다 성격 정보를 조회합니다.
    (10분 이내 캐시된 데이터 반환)
    """
    try:
        # 10분 전 시간 계산
        ten_minutes_ago = datetime.now().replace(second=0, microsecond=0)
        ten_minutes_ago = ten_minutes_ago.replace(minute=(ten_minutes_ago.minute // 10) * 10)
        
        response = supabase.table('sea_emotions')\
            .select('emotion, name, message')\
            .eq('location', location)\
            .gte('cached_at', ten_minutes_ago.isoformat())\
            .order('cached_at', desc=True)\
            .limit(1)\
            .execute()
        
        if response.data and len(response.data) > 0:
            return response.data[0]
        return None
            
    except Exception as e:
        print(f"캐시 조회 실패: {e}")
        return None

def save_emotion_cache(location: str, emotion_data: dict, sea_data: dict, supabase: Client) -> bool:
    """
    바다 성격 정보를 데이터베이스에 캐시합니다.
    """
    try:
        cache_insert = {
            'location': location,
            'emotion': emotion_data['emotion'],
            'name': emotion_data['name'],
            'message': emotion_data['message'],
            'sea_data': sea_data,
            'cached_at': datetime.now().isoformat()
        }
        
        response = supabase.table('sea_emotions')\
            .insert(cache_insert)\
            .execute()
        
        return response.data is not None and len(response.data) > 0
            
    except Exception as e:
        print(f"캐시 저장 실패: {e}")
        return False

def get_sea_emotion_service(location: str, api_key: str, supabase: Client) -> dict:
    """
    바다 성격 정보를 조회하거나 생성합니다.
    1. 캐시 확인 (10분 이내)
    2. 캐시 없으면 외부 API 호출 및 분석
    3. 결과 캐싱
    """
    try:
        # 1. 캐시 확인
        cached = get_cached_emotion(location, supabase)
        if cached:
            return cached
        
        # 2. 외부 API에서 해양 데이터 조회
        sea_data = get_sea_data(location, api_key)
        
        # 3. 해양 데이터 분석하여 바다 성격 판단
        emotion_result = analyze_sea_emotion(sea_data)
        
        # 4. 캐시 저장
        save_emotion_cache(location, emotion_result, sea_data, supabase)
        
        return emotion_result
            
    except Exception as e:
        print(f"바다 성격 조회 실패: {e}")
        raise e

def clean_old_cache(supabase: Client, days: int = 7) -> bool:
    """
    오래된 캐시 데이터를 삭제합니다. (선택사항)
    """
    try:
        cutoff_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        cutoff_date = cutoff_date.replace(day=cutoff_date.day - days)
        
        response = supabase.table('sea_emotions')\
            .delete()\
            .lt('cached_at', cutoff_date.isoformat())\
            .execute()
        
        return True
            
    except Exception as e:
        print(f"캐시 정리 실패: {e}")
        return False