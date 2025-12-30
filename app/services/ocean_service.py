# app/services/ocean_service.py
from typing import Dict, Optional
from app.schemas.schemas import SeaEmotionResponse

def calculate_sea_mood_score(wave_height: float, wind_speed: float, water_temp: Optional[float] = None) -> Dict:
    """
    해양 데이터를 기반으로 바다의 기분 점수를 계산합니다.
    
    점수 구성:
    - 안전 점수 (0-100): 파고와 풍속 기반, 낮을수록 안전
    - 활동 점수 (0-100): 다양한 활동 가능성
    - 평온 점수 (0-100): 평화로움 정도
    
    Returns:
        {
            "safety_score": int,  # 안전 점수 (높을수록 안전)
            "activity_score": int,  # 활동 점수 (높을수록 활동적)
            "calm_score": int,  # 평온 점수 (높을수록 평온)
            "total_score": int,  # 종합 점수 (0-100)
            "wave_height": float,
            "wind_speed": float
        }
    """
    # 안전 점수 계산 (파고와 풍속이 낮을수록 높은 점수)
    # 파고 0.5m 이하: 100점, 1.0m: 80점, 2.0m: 50점, 3.0m 이상: 20점
    if wave_height <= 0.5:
        wave_safety = 100
    elif wave_height <= 1.0:
        wave_safety = 100 - (wave_height - 0.5) * 40  # 80점
    elif wave_height <= 2.0:
        wave_safety = 80 - (wave_height - 1.0) * 30  # 50점
    else:
        wave_safety = max(20, 50 - (wave_height - 2.0) * 15)
    
    # 풍속 5m/s 이하: 100점, 10m/s: 80점, 15m/s: 50점, 20m/s 이상: 20점
    if wind_speed <= 5:
        wind_safety = 100
    elif wind_speed <= 10:
        wind_safety = 100 - (wind_speed - 5) * 4  # 80점
    elif wind_speed <= 15:
        wind_safety = 80 - (wind_speed - 10) * 6  # 50점
    else:
        wind_safety = max(20, 50 - (wind_speed - 15) * 6)
    
    safety_score = int((wave_safety + wind_safety) / 2)
    
    # 활동 점수 계산 (적당한 파도와 풍속이 있을 때 높은 점수)
    # 파고 0.5-1.5m, 풍속 5-12m/s가 이상적
    if 0.5 <= wave_height <= 1.5 and 5 <= wind_speed <= 12:
        activity_score = 100
    elif wave_height < 0.5 or wind_speed < 5:
        activity_score = 60  # 너무 잔잔함
    elif wave_height > 2.5 or wind_speed > 18:
        activity_score = 30  # 너무 거침
    else:
        activity_score = 70
    
    # 평온 점수 계산 (파고와 풍속이 낮을수록 높은 점수)
    calm_score = safety_score  # 안전 점수와 동일하게 계산
    
    # 종합 점수 (가중 평균)
    total_score = int(safety_score * 0.4 + activity_score * 0.3 + calm_score * 0.3)
    
    return {
        "safety_score": safety_score,
        "activity_score": activity_score,
        "calm_score": calm_score,
        "total_score": total_score,
        "wave_height": wave_height,
        "wind_speed": wind_speed
    }

def get_emotion_from_score(score_data: Dict, location_name: str) -> Dict:
    """
    점수 데이터를 기반으로 바다의 감정을 결정합니다.
    """
    total_score = score_data["total_score"]
    wave_height = score_data["wave_height"]
    wind_speed = score_data["wind_speed"]
    safety_score = score_data["safety_score"]
    
    # 점수 구간별 감정 결정
    if total_score >= 85:
        if wave_height < 0.5:
            return {
                "emoji": "😊",
                "name": "평온한 미소",
                "reason": f"{location_name}의 잔잔한 파도({wave_height:.1f}m)가 마음을 편안하게 합니다. 산책하기 완벽한 날이에요!",
                "score": total_score
            }
        else:
            return {
                "emoji": "🌅",
                "name": "평화로운 새벽",
                "reason": f"{location_name}의 고요한 바다(파고 {wave_height:.1f}m)가 평화를 줍니다.",
                "score": total_score
            }
    elif total_score >= 70:
        return {
            "emoji": "😊",
            "name": "편안한 물결",
            "reason": f"{location_name}의 적당한 파도({wave_height:.1f}m)가 산책하기 좋습니다.",
            "score": total_score
        }
    elif total_score >= 55:
        if safety_score >= 60:
            return {
                "emoji": "🌊",
                "name": "역동적인 파도",
                "reason": f"{location_name}의 강한 파도({wave_height:.1f}m)가 에너지를 줍니다. 해양 스포츠를 즐기기 좋은 날이에요!",
                "score": total_score
            }
        else:
            return {
                "emoji": "🤩",
                "name": "활기찬 물결",
                "reason": f"{location_name}의 역동적인 파도({wave_height:.1f}m)가 새로운 영감을 줍니다!",
                "score": total_score
            }
    elif total_score >= 40:
        return {
            "emoji": "🌊",
            "name": "거친 파도",
            "reason": f"{location_name}의 거친 파도({wave_height:.1f}m, 풍속 {wind_speed:.1f}m/s)가 힘을 줍니다. 안전에 주의하세요.",
            "score": total_score
        }
    else:
        return {
            "emoji": "⚠️",
            "name": "위험한 파도",
            "reason": f"{location_name}의 매우 거친 파도({wave_height:.1f}m, 풍속 {wind_speed:.1f}m/s)입니다. 해안 접근을 피하세요.",
            "score": total_score
        }

# 지역별 기본 해양 데이터 (전역 상수로 최적화)
_DEFAULT_WEATHER_DATA = {
    "사하구": {"wave_height": 0.8, "wind_speed": 6.5},
    "기장군": {"wave_height": 1.2, "wind_speed": 8.0},
    "영도구": {"wave_height": 1.0, "wind_speed": 7.0},
    "남구": {"wave_height": 0.9, "wind_speed": 6.0},
    "서구": {"wave_height": 0.7, "wind_speed": 5.5},
    "saha": {"wave_height": 0.8, "wind_speed": 6.5},
    "gijang": {"wave_height": 1.2, "wind_speed": 8.0},
    "yeongdo": {"wave_height": 1.0, "wind_speed": 7.0},
    "nam": {"wave_height": 0.9, "wind_speed": 6.0},
    "seo": {"wave_height": 0.7, "wind_speed": 5.5},
}

_NAME_TO_ID = {
    "사하구": "saha",
    "기장군": "gijang",
    "영도구": "yeongdo",
    "남구": "nam",
    "서구": "seo",
}

def analyze_sea_conditions(location_name: str, region_code: str = "101", skip_api: bool = True, ecosystem_data: Optional[Dict] = None) -> SeaEmotionResponse:
    """
    선택된 지역의 해양 데이터를 기반으로 바다의 성격을 분석하는 함수.
    즉시 응답을 위해 시뮬레이션 데이터만 사용합니다 (API 호출 없음).
    """
    import time
    analysis_start = time.time()
    
    # 지역별 기본 해양 데이터 조회 (최적화: 전역 상수 사용)
    weather = _DEFAULT_WEATHER_DATA.get(location_name)
    if not weather:
        # 지역명으로 매핑 시도
        region_id = _NAME_TO_ID.get(location_name, "saha")
        weather = _DEFAULT_WEATHER_DATA.get(region_id, {"wave_height": 0.8, "wind_speed": 6.5})
    
    score_start = time.time()
    # 점수 계산 (즉시 처리, 1ms 이내)
    score_data = calculate_sea_mood_score(
        wave_height=weather["wave_height"],
        wind_speed=weather["wind_speed"]
    )
    score_duration = (time.time() - score_start) * 1000
    
    emotion_start = time.time()
    # 점수 기반 감정 결정 (즉시 처리)
    emotion = get_emotion_from_score(score_data, location_name)
    emotion_duration = (time.time() - emotion_start) * 1000
    
    total_duration = (time.time() - analysis_start) * 1000
    
    print(f"  📈 [ocean_service] 점수 계산: {score_duration:.3f}ms, 감정 결정: {emotion_duration:.3f}ms, 총: {total_duration:.3f}ms")
    
    return SeaEmotionResponse(
        emotion=emotion["emoji"],  # main 스키마에 맞게 emoji -> emotion으로 변환
        name=emotion["name"]
    )
