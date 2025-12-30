from supabase import Client
from typing import Optional

def get_ecosystem_service(location: str, supabase: Client) -> Optional[dict]:
    """
    데이터베이스에서 해양 생태계 정보를 조회합니다.
    """
    try:
        # region_info 테이블에서 지역명으로 조회
        response = supabase.table("region_info")\
            .select("creature, specialties")\
            .eq("region_name", location)\
            .maybe_single()\
            .execute()
        
        if response.data:
            return response.data
        return None
            
    except Exception as e:
        print(f"해양 생태계 조회 실패 > location {location}: {e}")
        return None

def get_all_regions_service(supabase: Client) -> list:
    """
    모든 지역 정보를 조회합니다. (선택사항)
    """
    try:
        response = supabase.table("region_info")\
            .select("*")\
            .execute()
        
        return response.data if response.data else []
            
    except Exception as e:
        print(f"전체 지역 조회 실패: {e}")
        return []