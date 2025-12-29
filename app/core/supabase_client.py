# app/core/supabase_client.py
from supabase import create_client, Client
from .config import settings

# 백엔드 전용 클라이언트는 service_role 키를 사용합니다.
# 이 키는 데이터베이스의 모든 테이블에 대한 전체 접근 권한을 가집니다.
supabase_admin: Client = create_client(
    settings.SUPABASE_URL, 
    settings.SUPABASE_SERVICE_KEY
)

def get_supabase() -> Client:
    """
    API 엔드포인트에서 사용할 Supabase 클라이언트 의존성.
    """
    return supabase_admin
