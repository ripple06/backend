# app/services/ocean_service.py
import random
from app.schemas.location import SeaEmotion

def analyze_sea_conditions(location_name: str) -> SeaEmotion:
    """
    선택된 지역의 해양 데이터를 기반으로 바다의 성격을 분석하는 함수 (시뮬레이션).
    실제 구현 시에는 이 함수에서 외부 해양 데이터 API를 호출하거나,
    가지고 있는 데이터를 분석하는 로직이 들어갑니다.
    """
    emotions = [
        {"emoji": "😊", "name": "평온한 미소", "reason": f"{location_name}의 잔잔한 파도가 마음을 편안하게 합니다."},
        {"emoji": "😢", "name": "쓸쓸한 파도", "reason": f"조용한 {location_name}의 바다, 오늘은 조금 외로워 보여요."},
        {"emoji": "🤩", "name": "활기찬 물결", "reason": f"{location_name}의 역동적인 파도가 새로운 영감을 줍니다!"},
        {"emoji": "🤔", "name": "생각에 잠긴 심해", "reason": f"깊이를 알 수 없는 {location_name}의 바다가 명상을 유도합니다."},
    ]
    
    selected = random.choice(emotions)

    return SeaEmotion(
        emotion_emoji=selected["emoji"],
        emotion_name=selected["name"],
        reason=selected["reason"]
    )
