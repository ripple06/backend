from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import Optional
import os
from supabase import create_client, Client

app = FastAPI()

# Supabase 클라이언트 설정 (환경변수 확인 필요)
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_URL and SUPABASE_KEY else None

# Response Model
class SeaEcosystemResponse(BaseModel):
    creature: str
    specialties: str

@app.get("/seaecosystem", response_model=SeaEcosystemResponse)
async def get_sea_ecosystem(location: Optional[str] = Query(None, description="지역명")):
    """
    해양 생태계 불러오기 API
    - 특정 지역의 대표 생물, 특산물 정보 반환
    """
    try:
        if not location:
            raise HTTPException(status_code=400, detail="지역명을 입력해주세요")
        
        # 임시 데이터 (실제로는 DB에서 조회)
        ecosystem_data = get_ecosystem_from_db(location)
        
        if not ecosystem_data:
            raise HTTPException(status_code=404, detail="해당 지역 정보를 찾을 수 없습니다")
        
        return {
            "creature": ecosystem_data["creature"],
            "specialties": ecosystem_data["specialties"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"생태계 정보 조회 실패: {str(e)}")


def get_ecosystem_from_db(location: str) -> Optional[dict]:
    """
    데이터베이스에서 해양 생태계 정보 조회
    """
    if not supabase:
        return None

    try:
        # 'region_info' 테이블에서 지역명(region_name)으로 조회
        # 테이블 이름과 컬럼명은 실제 DB에 맞게 수정이 필요할 수 있습니다.
        response = supabase.table("region_info").select("creature, specialties").eq("region_name", location).maybe_single().execute()
        return response.data
    except Exception as e:
        print(f"Supabase 조회 오류: {e}")
        return None