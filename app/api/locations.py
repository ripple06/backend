# app/api/locations.py
from fastapi import APIRouter, Depends, HTTPException
from supabase import Client
from typing import List

from app.schemas import location as location_schema
from app.services import ocean_service
from app.core.supabase_client import get_supabase

router = APIRouter(
    prefix="/locations",
    tags=["Locations & Sea Analysis"],
)

@router.get("/", response_model=List[location_schema.Location])
def get_locations(skip: int = 0, limit: int = 10, supabase: Client = Depends(get_supabase)):
    """
    등록된 모든 지역 목록을 가져옵니다.
    """
    try:
        # Supabase에서 locations 테이블 데이터 가져오기
        response = supabase.table("locations").select("*").range(skip, skip + limit - 1).execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{location_id}", response_model=location_schema.Location)
def get_location_details(location_id: int, supabase: Client = Depends(get_supabase)):
    """
    특정 지역의 상세 정보(대표 생물, 특산물 등)를 가져옵니다.
    """
    try:
        response = supabase.table("locations").select("*").eq("id", location_id).single().execute()
        if not response.data:
            raise HTTPException(status_code=404, detail="Location not found")
        return response.data
    except Exception as e:
        # single()은 데이터가 없을 때 예외를 발생시킬 수 있습니다.
        if "PGRST116" in str(e): # PostgREST 에러 코드 (결과 0개)
             raise HTTPException(status_code=404, detail="Location not found")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{location_id}/analyze", response_model=location_schema.SeaEmotion)
def analyze_sea_state(location_id: int, supabase: Client = Depends(get_supabase)):
    """
    특정 지역의 바다 상태를 분석하여 감정 결과를 반환합니다.
    """
    # 1. 먼저 지역 정보 가져오기
    try:
        response = supabase.table("locations").select("name").eq("id", location_id).single().execute()
        if not response.data:
            raise HTTPException(status_code=404, detail="Location not found")
        
        location_name = response.data['name']
        
        # 2. Ocean Service를 호출하여 결과 받기
        sea_emotion = ocean_service.analyze_sea_conditions(location_name)
        return sea_emotion

    except Exception as e:
        if "PGRST116" in str(e):
             raise HTTPException(status_code=404, detail="Location not found")
        raise HTTPException(status_code=500, detail=str(e))