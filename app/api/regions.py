# app/api/regions.py
from fastapi import APIRouter, HTTPException
from app.schemas.schemas import Region, RegionListResponse, RegionEcosystemResponse, MarineEcosystem, SeaEmotionResponse
from app.services.ocean_service import analyze_sea_conditions
from app.services.marine_data_service import marine_data_service
import random
import threading

router = APIRouter()

# 테스트용 지역 데이터
REGIONS_DATA = {
    "saha": {
        "id": "saha",
        "name": "사하구",
        "code": "saha",
        "latitude": 35.1047,
        "longitude": 129.0263,
        "description": "부산광역시 사하구",
        "ecosystem": {
            "representative_species": ["멸치", "고등어", "전복", "해조류"],
            "specialties": ["멸치젓", "전복", "해조류"],
            "sea_condition": "잔잔한 파도, 얕은 바다",
            "representative_resorts": ["을숙도", "낙동강 하구"],
            "ecosystem_description": "낙동강 하구와 접한 사하구는 다양한 해양 생물이 서식하는 생태계가 발달했습니다."
        }
    },
    "gijang": {
        "id": "gijang",
        "name": "기장군",
        "code": "gijang",
        "latitude": 35.2444,
        "longitude": 129.2139,
        "description": "부산광역시 기장군",
        "ecosystem": {
            "representative_species": ["멍게", "해삼", "전복", "다랑어"],
            "specialties": ["멍게", "해삼", "전복"],
            "sea_condition": "깊은 바다, 강한 파도",
            "representative_resorts": ["해운대", "송정해수욕장", "일광해수욕장"],
            "ecosystem_description": "동해와 접한 기장군은 깊은 바다와 다양한 해양 생물이 서식하는 지역입니다."
        }
    },
    "yeongdo": {
        "id": "yeongdo",
        "name": "영도구",
        "code": "yeongdo",
        "latitude": 35.0914,
        "longitude": 129.0678,
        "description": "부산광역시 영도구",
        "ecosystem": {
            "representative_species": ["고등어", "꽁치", "멸치", "해조류"],
            "specialties": ["고등어", "멸치젓"],
            "sea_condition": "중간 깊이, 적당한 파도",
            "representative_resorts": ["태종대", "영도대교"],
            "ecosystem_description": "부산항과 접한 영도구는 다양한 어류가 서식하는 해양 생태계를 가지고 있습니다."
        }
    },
    "nam": {
        "id": "nam",
        "name": "남구",
        "code": "nam",
        "latitude": 35.1367,
        "longitude": 129.0844,
        "description": "부산광역시 남구",
        "ecosystem": {
            "representative_species": ["전복", "해조류", "멸치"],
            "specialties": ["전복", "해조류"],
            "sea_condition": "잔잔한 파도",
            "representative_resorts": ["이기대", "용호동"],
            "ecosystem_description": "남구는 해조류가 풍부하고 전복 양식이 발달한 지역입니다."
        }
    },
    "seo": {
        "id": "seo",
        "name": "서구",
        "code": "seo",
        "latitude": 35.0979,
        "longitude": 129.0244,
        "description": "부산광역시 서구",
        "ecosystem": {
            "representative_species": ["멸치", "고등어", "해조류"],
            "specialties": ["멸치젓"],
            "sea_condition": "얕은 바다, 잔잔한 파도",
            "representative_resorts": ["송도해수욕장"],
            "ecosystem_description": "서구는 얕은 바다와 해조류가 풍부한 해양 생태계를 가지고 있습니다."
        }
    }
}

@router.get("", response_model=RegionListResponse)
async def get_regions():
    """지역 목록 조회"""
    regions = [
        Region(**{k: v for k, v in data.items() if k != "ecosystem"})
        for data in REGIONS_DATA.values()
    ]
    return RegionListResponse(regions=regions)

@router.get("/{region_id}", response_model=Region)
async def get_region(region_id: str):
    """지역 상세 정보"""
    if region_id not in REGIONS_DATA:
        raise HTTPException(status_code=404, detail="Region not found")
    
    data = REGIONS_DATA[region_id]
    return Region(**{k: v for k, v in data.items() if k != "ecosystem"})

@router.get("/{region_id}/ecosystem", response_model=RegionEcosystemResponse)
async def get_region_ecosystem(region_id: str):
    """지역의 해양 생태계 정보 및 바다의 성격 분석"""
    import time
    request_start_time = time.time()
    
    print(f"🚀 [백엔드] 요청 시작: region_id={region_id}, 시간={time.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}")
    
    if region_id not in REGIONS_DATA:
        raise HTTPException(status_code=404, detail="Region not found")
    
    data = REGIONS_DATA[region_id]
    region = Region(**{k: v for k, v in data.items() if k != "ecosystem"})
    ecosystem_data = data["ecosystem"].copy()
    
    ecosystem_start = time.time()
    # 해양 생태계 정보 즉시 생성
    ecosystem = MarineEcosystem(**ecosystem_data)
    ecosystem_duration = (time.time() - ecosystem_start) * 1000
    print(f"📊 [백엔드] 해양 생태계 생성 완료: {ecosystem_duration:.3f}ms")
    
    # 바다의 성격 분석 (점수 기반 계산, AI 사용 안 함, 즉시 응답)
    # 최적화: 지역명을 직접 사용하여 딕셔너리 조회 최소화
    region_name = region.name
    
    sea_emotion_start = time.time()
    # 바다 기분 분석 즉시 실행 (API 호출 없음, 0.1ms 이내 완료)
    sea_emotion_data = analyze_sea_conditions(
        region_name, 
        region_code="101", 
        skip_api=True,
        ecosystem_data=ecosystem_data
    )
    sea_emotion_duration = (time.time() - sea_emotion_start) * 1000
    print(f"🌊 [백엔드] 바다 기분 분석 완료: {sea_emotion_duration:.3f}ms, 결과={sea_emotion_data.emoji} {sea_emotion_data.name}")
    
    response_start = time.time()
    # 즉시 응답 반환 (해양 생태계 + 바다 기분 모두 포함)
    response = RegionEcosystemResponse(
        region=region,
        ecosystem=ecosystem,
        sea_emotion=sea_emotion_data
    )
    response_duration = (time.time() - response_start) * 1000
    total_duration = (time.time() - request_start_time) * 1000
    
    print(f"✅ [백엔드] 응답 생성 완료: {response_duration:.3f}ms")
    print(f"⏱️  [백엔드] 전체 처리 시간: {total_duration:.3f}ms (생태계: {ecosystem_duration:.3f}ms, 바다기분: {sea_emotion_duration:.3f}ms, 응답: {response_duration:.3f}ms)")
    
    return response
