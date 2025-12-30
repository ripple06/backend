# app/services/marine_data_service.py
"""
해양 데이터 수집 서비스
가이드 문서를 참고하여 실제 API를 호출하는 서비스
"""
import os
import requests
from typing import Optional, Dict, List
from app.core.config import settings
from datetime import datetime

class MarineDataService:
    """해양 데이터 수집 서비스"""
    
    def __init__(self):
        self.marine_weather_api_key = settings.MARINE_WEATHER_NMPNT_API_KEY
        self.marine_statistics_api_key = settings.MARINE_STATISTICS_API_KEY
        self.marine_api_key = settings.MARINE_API_KEY
    
    def get_marine_weather(self, region_code: str = "101", station_code: str = "994401584") -> Optional[Dict]:
        """
        해양기상 정보 조회 (국립해양측위정보원)
        region_code: 기관코드 (101=부산청, 102=인천청, 103=여수청 등)
        station_code: 지점코드
        """
        if not self.marine_weather_api_key:
            return None
        
        url = "http://marineweather.nmpnt.go.kr:8001/openWeatherNow.do"
        params = {
            "serviceKey": self.marine_weather_api_key,
            "resultType": "json",
            "mmaf": region_code,
            "mmsi": station_code,
            "dataType": "1"
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)  # 타임아웃 10초로 증가
            response.encoding = "UTF-8"
            
            if response.status_code == 200:
                data = response.json()
                if data.get("result", {}).get("status") == "OK":
                    return data
            return None
        except requests.Timeout:
            print(f"해양기상 API 타임아웃 (10초 초과)")
            return None
        except requests.exceptions.ConnectionError as e:
            print(f"해양기상 API 연결 실패: {e}")
            return None
        except Exception as e:
            print(f"해양기상 API 호출 실패: {e}")
            return None
    
    def get_marine_statistics(self, page: int = 1, per_page: int = 100) -> Optional[Dict]:
        """
        해양수산부 통계시스템공통 API 조회 (ODCloud)
        """
        if not self.marine_statistics_api_key:
            return None
        
        url = "https://api.odcloud.kr/api/15070375/v1/uddi:7cdf774a-ccbb-4c72-8923-dfb1f70ab70c"
        params = {
            "serviceKey": self.marine_statistics_api_key,
            "page": page,
            "perPage": per_page
        }
        
        try:
            response = requests.get(url, params=params, timeout=3)  # 타임아웃 3초로 단축
            if response.status_code == 200:
                return response.json()
            return None
        except requests.Timeout:
            print(f"해양통계 API 타임아웃 (3초 초과)")
            return None
        except Exception as e:
            print(f"해양통계 API 호출 실패: {e}")
            return None
    
    def analyze_sea_condition_from_weather(self, weather_data: Dict) -> Dict:
        """
        해양기상 데이터를 기반으로 바다 상태 분석
        """
        if not weather_data or "result" not in weather_data:
            return {
                "condition": "데이터 없음",
                "description": "해양기상 데이터를 가져올 수 없습니다."
            }
        
        recordset = weather_data.get("result", {}).get("recordset", [])
        if not recordset:
            return {
                "condition": "데이터 없음",
                "description": "관측 데이터가 없습니다."
            }
        
        record = recordset[0]  # 첫 번째 관측지점 데이터 사용
        
        # 파고 분석
        wave_height = float(record.get("WAVE_HEIGTH", 0) or 0)
        wind_speed = float(record.get("WIND_SPEED", 0) or 0)
        water_temp = float(record.get("WATER_TEMPER", 0) or 0)
        
        # 바다 상태 판단
        if wave_height < 0.5:
            condition = "잔잔한 파도"
        elif wave_height < 1.5:
            condition = "적당한 파도"
        elif wave_height < 2.5:
            condition = "강한 파도"
        else:
            condition = "매우 강한 파도"
        
        description = f"파고: {wave_height}m, 풍속: {wind_speed}m/s, 수온: {water_temp}°C"
        
        return {
            "condition": condition,
            "description": description,
            "wave_height": wave_height,
            "wind_speed": wind_speed,
            "water_temperature": water_temp
        }

# 싱글톤 인스턴스
marine_data_service = MarineDataService()
