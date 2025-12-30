# app/services/ai_service.py
"""
AI 서비스 - OpenAI, Anthropic, Gemini를 사용한 AI 기능
"""
import os
import json
from typing import Dict, List, Optional
from app.core.config import settings

class AIService:
    """AI 서비스 클래스"""
    
    def __init__(self):
        self.openai_key = settings.OPENAI_API_KEY
        self.anthropic_key = settings.ANTHROPIC_API_KEY
        self.gemini_key = settings.GEMINI_API_KEY
    
    def _call_openai(self, prompt: str, model: str = "gpt-4o-mini", temperature: float = 0.7) -> Optional[str]:
        """OpenAI API 호출"""
        if not self.openai_key:
            return None
        
        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.openai_key)
            
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that provides JSON responses."},
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature,
                response_format={"type": "json_object"}
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"OpenAI API 호출 실패: {e}")
            return None
    
    def _call_anthropic(self, prompt: str, model: str = "claude-3-5-sonnet-20241022", temperature: float = 0.7) -> Optional[str]:
        """Anthropic Claude API 호출"""
        if not self.anthropic_key:
            return None
        
        try:
            from anthropic import Anthropic
            client = Anthropic(api_key=self.anthropic_key)
            
            response = client.messages.create(
                model=model,
                max_tokens=2000,
                temperature=temperature,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            return response.content[0].text
        except Exception as e:
            print(f"Anthropic API 호출 실패: {e}")
            return None
    
    def _call_gemini(self, prompt: str, model: str = "gemini-1.5-flash-latest", temperature: float = 0.7) -> Optional[str]:
        """Google Gemini API 호출"""
        if not self.gemini_key:
            print("  ❌ Gemini API Key가 없습니다.")
            return None
        
        try:
            import google.generativeai as genai
            import time
            genai.configure(api_key=self.gemini_key)
            
            # 사용 가능한 모델 목록 확인
            try:
                models = genai.list_models()
                available_models = [m.name for m in models if 'generateContent' in m.supported_generation_methods]
                print(f"  📋 사용 가능한 Gemini 모델: {available_models[:3]}")
                
                # 사용 가능한 모델 중 하나 선택
                if available_models:
                    model = available_models[0].split('/')[-1]  # models/gemini-1.5-flash -> gemini-1.5-flash
                    print(f"  🎯 선택된 모델: {model}")
                else:
                    model = "gemini-1.5-flash"
                    print(f"  ⚠️  기본 모델 사용: {model}")
            except Exception as e:
                # 모델 목록 조회 실패 시 기본값 사용
                model = "gemini-1.5-flash"
                print(f"  ⚠️  모델 목록 조회 실패, 기본 모델 사용: {model}, 에러: {e}")
            
            print(f"  🚀 Gemini API 호출 시작...")
            api_start_time = time.time()
            
            model_instance = genai.GenerativeModel(model)
            
            # 웹 검색을 위한 tools 설정 (Gemini 2.0/2.5 Flash는 자동으로 웹 검색 활용 가능)
            # 프롬프트에 웹 검색을 명시적으로 요청하면 모델이 자동으로 검색 수행
            print(f"  🔍 웹 검색을 통한 최신 정보 수집 요청")
            
            response = model_instance.generate_content(
                prompt,
                generation_config={
                    "temperature": temperature,
                    "response_mime_type": "application/json"
                }
            )
            api_duration = (time.time() - api_start_time) * 1000
            print(f"  ✅ Gemini API 응답 수신: {api_duration:.3f}ms")
            return response.text
        except Exception as e:
            print(f"  ❌ Gemini API 호출 실패: {e}")
            import traceback
            print(traceback.format_exc())
            return None
    
    def analyze_sea_emotion(self, location_name: str, weather_data: Optional[Dict] = None, ecosystem_data: Optional[Dict] = None) -> Dict:
        """
        AI를 사용하여 바다의 감정을 분석
        
        Args:
            location_name: 지역명
            weather_data: 해양기상 데이터 (파고, 풍속, 수온 등)
            ecosystem_data: 해양 생태계 데이터 (대표 생물, 특산물 등)
        
        Returns:
            {"emoji": str, "name": str, "reason": str}
        """
        # 프롬프트 구성
        weather_info = ""
        if weather_data:
            wave_height = weather_data.get("wave_height", 0)
            wind_speed = weather_data.get("wind_speed", 0)
            water_temp = weather_data.get("water_temperature", 0)
            weather_info = f"""
해양기상 정보:
- 파고: {wave_height}m
- 풍속: {wind_speed}m/s
- 수온: {water_temp}°C
"""
        
        ecosystem_info = ""
        if ecosystem_data:
            species = ecosystem_data.get("representative_species", [])
            specialties = ecosystem_data.get("specialties", [])
            condition = ecosystem_data.get("sea_condition", "")
            ecosystem_info = f"""
해양 생태계 정보:
- 대표 생물: {', '.join(species) if species else '정보 없음'}
- 특산물: {', '.join(specialties) if specialties else '정보 없음'}
- 바다 상태: {condition}
"""
        
        prompt = f"""당신은 해양 전문가이자 시인입니다. {location_name}의 바다를 분석하여 바다의 오늘 기분을 감정적으로 표현해주세요.

{weather_info}
{ecosystem_info}

다음 JSON 형식으로 응답해주세요:
{{
    "emoji": "이모티콘 하나 (예: 😊, 🌊, 🤩, 😢, 🤔, 🌅)",
    "name": "감정 이름 (예: 평온한 미소, 역동적인 파도, 활기찬 물결)",
    "reason": "한 줄 이유 설명 (50자 이내, 시적이고 감성적으로)"
}}

바다의 현재 상태, 날씨, 생태계를 종합적으로 고려하여 창의적이고 감성적인 감정을 표현해주세요."""
        
        # API 우선순위: OpenAI > Anthropic > Gemini
        response_text = None
        if self.openai_key:
            response_text = self._call_openai(prompt, model="gpt-4o-mini", temperature=0.8)
        elif self.anthropic_key:
            response_text = self._call_anthropic(prompt, model="claude-3-5-sonnet-20241022", temperature=0.8)
        elif self.gemini_key:
            response_text = self._call_gemini(prompt, model="gemini-1.5-flash", temperature=0.8)
        
        if response_text:
            try:
                result = json.loads(response_text)
                if "emoji" in result and "name" in result and "reason" in result:
                    return result
            except json.JSONDecodeError:
                print(f"AI 응답 JSON 파싱 실패: {response_text}")
        
        # AI 호출 실패 시 기본값 반환
        return {
            "emoji": "😊",
            "name": "평온한 미소",
            "reason": f"{location_name}의 바다가 당신을 기다리고 있어요."
        }
    
    def generate_course_recommendations(
        self,
        location_name: str,
        mbti: str,
        sea_emotion: Dict,
        ecosystem_data: Optional[Dict] = None,
        user_preferences: Optional[Dict] = None,
        limit: int = 5
    ) -> List[Dict]:
        """
        AI를 사용하여 여행 코스를 추천
        
        Args:
            location_name: 지역명
            mbti: 사용자 MBTI
            sea_emotion: 바다 감정 분석 결과
            ecosystem_data: 해양 생태계 데이터
            user_preferences: 사용자 선호도
            limit: 추천 코스 개수
        
        Returns:
            List[Dict] - 코스 리스트
        """
        # MBTI 특성 설명
        mbti_traits = {
            "ISTP": "실용적이고 모험을 좋아하며, 혼자서 탐험하는 것을 선호합니다.",
            "ISFP": "예술적이고 감성적이며, 자연을 사랑하고 조용한 곳을 선호합니다.",
            "ESTP": "활동적이고 즉흥적이며, 스릴과 모험을 추구합니다.",
            "ESFP": "사교적이고 활발하며, 즐거운 경험을 중시합니다.",
            "ISTJ": "체계적이고 신중하며, 계획된 여행을 선호합니다.",
            "ISFJ": "배려심이 많고 전통을 중시하며, 편안한 환경을 선호합니다.",
            "ESTJ": "리더십이 있고 조직적이며, 효율적인 여행을 선호합니다.",
            "ESFJ": "사교적이고 배려심이 많으며, 함께하는 여행을 선호합니다.",
            "INFJ": "직관적이고 이상주의적이며, 의미 있는 경험을 추구합니다.",
            "INFP": "창의적이고 이상주의적이며, 개인적인 가치를 중시합니다.",
            "ENFJ": "카리스마 있고 배려심이 많으며, 사람들과의 교류를 중시합니다.",
            "ENFP": "열정적이고 창의적이며, 새로운 경험을 추구합니다.",
            "INTJ": "전략적이고 독립적이며, 깊이 있는 탐험을 선호합니다.",
            "INTP": "분석적이고 호기심이 많으며, 지적 탐구를 선호합니다.",
            "ENTJ": "리더십이 있고 목표 지향적이며, 효율적인 탐험을 선호합니다.",
            "ENTP": "창의적이고 논쟁을 좋아하며, 다양한 경험을 추구합니다.",
        }
        
        mbti_description = mbti_traits.get(mbti, "개인적인 선호도를 가진")
        
        ecosystem_info = ""
        if ecosystem_data:
            species = ecosystem_data.get("representative_species", [])
            specialties = ecosystem_data.get("specialties", [])
            resorts = ecosystem_data.get("representative_resorts", [])
            ecosystem_info = f"""
**해양 생태계 정보 (이 정보를 반드시 활용하여 해양 관광 코스를 추천하세요):**
- 대표 생물: {', '.join(species) if species else '정보 없음'}
  → 이 생물들을 관찰하거나 체험할 수 있는 해양 관광지(해양 생태 체험장, 해양 박물관, 해안 탐조대 등)를 코스에 포함하세요.
- 특산물: {', '.join(specialties) if specialties else '정보 없음'}
  → 이 특산물을 맛볼 수 있는 해양 식당, 해안 시장, 해산물 식당을 코스에 포함하세요.
- 대표 휴양지: {', '.join(resorts) if resorts else '정보 없음'}
  → 이 휴양지들을 코스의 경유지로 포함하거나 참고하세요.

**중요:** 위 해양 생태계 정보를 반드시 활용하여 해당 생물, 특산물, 휴양지를 체험할 수 있는 해양 관광 코스를 추천하세요.
"""
        else:
            ecosystem_info = f"""
**해양 생태계 정보: 정보 없음**
→ 웹 검색을 통해 {location_name} 지역의 해양 생태계 정보를 조사하고, 해양 생물 관찰이나 해양 체험이 가능한 해양 관광지를 추천하세요.
"""
        
        preferences_info = ""
        if user_preferences:
            # MBTI는 이미 별도로 표시되므로 제외
            filtered_prefs = {k: v for k, v in user_preferences.items() if k != "mbti" and k != "sea_emotion"}
            if filtered_prefs:
                preferences_info = f"""
**추가 사용자 선호도:**
{json.dumps(filtered_prefs, ensure_ascii=False, indent=2)}
"""
        
        prompt = f"""당신은 {location_name} 지역의 전문 해양 여행 가이드입니다. **반드시 웹 검색을 활용하여** 최신 정보를 바탕으로 사용자의 MBTI 성향, 해양 생태계 정보, 바다의 기분을 종합적으로 고려하여 맞춤형 해양 여행 코스를 추천해주세요.

**⚠️ 필수 요구사항:**
1. **웹 검색을 먼저 수행하여 {location_name} 지역의 해양 관광지, 해안 명소, 해양 체험 시설 정보를 조사하세요.**
   - ⚠️ 중요: 일반 관광지가 아닌 **해양/해안 관련 관광지만** 추천하세요.
   - 해수욕장, 해안 산책로, 해양 생태 체험장, 해양 박물관, 해안 카페, 해양 스포츠 시설 등
2. 웹 검색 결과를 바탕으로 실제 존재하는 해양 관광지만 추천하세요.
3. 각 해양 관광지의 실제 위도/경도 좌표를 웹 검색을 통해 확인하세요.
4. 추천 이유(reason)에는 웹 검색 결과, MBTI 특성, 해양 생태계 정보, 바다 기분을 종합하여 구체적으로 설명하세요.

**사용자 정보 (이 정보들을 종합하여 해양 관광 코스를 추천하세요):**
- **MBTI: {mbti}** ({mbti_description})
  → 이 MBTI 특성에 맞는 해양 관광 코스를 추천하세요.
  → 예: ISTP는 혼자 탐험하기 좋은 해양 생태 관찰 코스, ESFP는 사교적인 해양 체험 코스
- **바다의 오늘 기분:** {sea_emotion.get('name', '')} {sea_emotion.get('emoji', '')}
- **바다 기분 이유:** {sea_emotion.get('reason', '')}
  → 이 바다 기분과 조화로운 해양 관광 코스를 추천하세요.

{ecosystem_info}

{preferences_info}

**🔍 웹 검색을 통해 다음 해양 관광지 정보를 반드시 조사하세요:**
1. "{location_name} 해양 관광지" 또는 "{location_name} 해안 명소" 검색
2. "{location_name} 해양 생태 체험" 또는 "{location_name} 해양 생물 관찰" 검색
3. "{location_name} 해안 산책로" 또는 "{location_name} 해안 코스" 검색  
4. "{location_name} 해수욕장" 또는 "{location_name} 해양 스포츠" 검색
5. 각 해양 관광지의 실제 위치(위도/경도) 정보 검색
6. 최신 리뷰 및 인기도 정보 확인

다음 JSON 형식으로 {limit}개의 해양 관광 코스를 추천해주세요:
{{
    "courses": [
        {{
            "name": "해양 관광 코스 이름 (예: 사하구 해안 생태 탐방 코스, 기장 해조류 체험 코스)",
            "description": "코스 설명 (50자 이내) - 해양 생태계 체험 중심으로",
            "reason": "이 코스를 추천하는 이유를 구체적으로 설명하세요:\n- MBTI({mbti}) 특성과의 연관성\n- 해양 생태계 정보 활용 방법\n- 바다 기분({sea_emotion.get('name', '')})과의 조화\n- 웹 검색 결과를 바탕으로 한 최신 정보",
            "distance": 숫자 (km, 2.0~10.0 사이),
            "duration": "예상 소요 시간 (예: 1시간 30분)",
            "highlights": ["해양 생태계 체험 하이라이트 1", "해양 관광 하이라이트 2", "MBTI 맞춤 하이라이트 3"],
            "path": [
                {{"lat": 위도, "lng": 경도, "name": "해양 관광지 이름 (예: 해운대 해수욕장, 해양 생태 체험장)", "description": "이 해양 관광지에서 체험할 수 있는 해양 생태계 관련 내용"}},
                {{"lat": 위도, "lng": 경도, "name": "해양 관광지 이름", "description": "해양 생태계 관련 내용"}},
                {{"lat": 위도, "lng": 경도, "name": "해양 관광지 이름", "description": "해양 생태계 관련 내용"}}
            ]
        }}
    ]
}}

**최종 체크리스트 (모두 확인하세요):**
1. ✅ **웹 검색을 먼저 수행하여 해양 관광지 정보를 조사했는가?** (필수)
2. ✅ **일반 관광지가 아닌 해양/해안 관련 관광지만 추천했는가?** (필수)
   - 해수욕장, 해안 산책로, 해양 생태 체험장, 해양 박물관, 해안 카페, 해양 스포츠 시설 등만 포함
   - 일반 박물관, 쇼핑몰, 도심 관광지는 제외
3. ✅ 웹 검색 결과를 바탕으로 실제 존재하는 해양 관광지만 추천했는가?
4. ✅ 각 해양 관광지의 실제 위도/경도를 웹 검색을 통해 확인했는가?
5. ✅ **MBTI({mbti}) 특성에 맞는 해양 관광 코스인가?** 
   - 예: ISTP는 혼자 탐험하기 좋은 해양 생태 관찰 코스
   - 예: ESFP는 사교적인 해양 체험 코스
   - 예: INFJ는 의미 있는 해양 생태 보호 체험 코스
6. ✅ **해양 생태계 정보를 활용한 코스인가?** 
   - 대표 생물을 관찰할 수 있는 해양 관광지 포함
   - 특산물을 맛볼 수 있는 해양 식당/시장 포함
   - 대표 휴양지를 경유지로 포함
7. ✅ 바다의 기분({sea_emotion.get('name', '')})과 조화로운 해양 관광 코스인가?
   - 평온한 미소 → 해안 산책, 해양 생태 관찰
   - 역동적인 파도 → 해양 스포츠, 해양 체험
8. ✅ reason 필드에 다음을 모두 포함하여 구체적으로 작성했는가?
   - 웹 검색 결과를 바탕으로 한 최신 정보
   - MBTI({mbti}) 특성과의 연관성
   - 해양 생태계 정보 활용 방법
   - 바다 기분({sea_emotion.get('name', '')})과의 조화

**좌표 범위:** {location_name} 지역 내의 실제 위도/경도 (부산 기준: 위도 35.0~35.3, 경도 129.0~129.3)

**⚠️ 중요: 일반 관광지가 아닌 해양 관광지만 추천하세요! 해수욕장, 해안 산책로, 해양 생태 체험장, 해양 박물관 등 해양/해안 관련 시설만 포함하세요.**

**시작하기 전에 반드시 웹 검색을 수행하여 해양 관광지 정보를 조사하세요!**"""
        
        # API 우선순위: OpenAI > Anthropic > Gemini
        response_text = None
        api_used = None
        if self.openai_key:
            print("  🔵 OpenAI API 사용")
            response_text = self._call_openai(prompt, model="gpt-4o-mini", temperature=0.7)
            api_used = "OpenAI"
        elif self.anthropic_key:
            print("  🟣 Anthropic API 사용")
            response_text = self._call_anthropic(prompt, model="claude-3-5-sonnet-20241022", temperature=0.7)
            api_used = "Anthropic"
        elif self.gemini_key:
            print("  🟢 Gemini API 사용")
            response_text = self._call_gemini(prompt, temperature=0.7)  # 모델은 함수 내에서 자동 선택
            api_used = "Gemini"
        else:
            print("  ⚠️  사용 가능한 AI API가 없습니다.")
        
        if response_text:
            try:
                print(f"  📝 {api_used} 응답 파싱 시작...")
                result = json.loads(response_text)
                if "courses" in result and isinstance(result["courses"], list):
                    print(f"  ✅ {len(result['courses'])}개 코스 추출 성공")
                    courses = []
                    for i, course in enumerate(result["courses"][:limit]):
                        # PathPoint 생성
                        path = course.get("path", [])
                        if not path:
                            # 기본 경로 생성
                            path = [
                                {"lat": 35.1796, "lng": 129.0756},
                                {"lat": 35.1800, "lng": 129.0760},
                                {"lat": 35.1804, "lng": 129.0764}
                            ]
                        
                        courses.append({
                            "courseId": i + 1,
                            "name": course.get("name", f"{location_name} 코스 {i+1}"),
                            "totalDistance": float(course.get("distance", 5.0)),
                            "color": "#7364fe",
                            "path": path,
                            "description": course.get("description", ""),
                            "reason": course.get("reason", ""),  # 추천 이유 추가
                            "duration": course.get("duration", ""),
                            "highlights": course.get("highlights", [])
                        })
                    return courses
            except (json.JSONDecodeError, KeyError, ValueError) as e:
                print(f"AI 코스 추천 응답 파싱 실패: {e}, 응답: {response_text}")
        
        # AI 호출 실패 시 기본 코스 반환
        return [{
            "courseId": 1,
            "name": f"{location_name} 해안 탐방 코스",
            "totalDistance": 5.0,
            "color": "#7364fe",
            "path": [
                {"lat": 35.1796, "lng": 129.0756},
                {"lat": 35.1800, "lng": 129.0760},
                {"lat": 35.1804, "lng": 129.0764}
            ]
        }]

# 싱글톤 인스턴스
ai_service = AIService()
