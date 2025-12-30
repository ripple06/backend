# app/services/mbti_service.py
from supabase import Client
from typing import Optional
from datetime import datetime

def save_mbti_service(user_id: int, mbti: str, supabase: Client) -> dict:
    """
    사용자의 MBTI를 저장하거나 업데이트합니다.
    """
    try:
        # 사용자가 존재하는지 확인
        existing_user = supabase.table('users')\
            .select('id, mbti')\
            .eq('id', user_id)\
            .execute()
        
        if existing_user.data and len(existing_user.data) > 0:
            # 사용자가 존재하면 MBTI 업데이트
            response = supabase.table('users')\
                .update({'mbti': mbti})\
                .eq('id', user_id)\
                .execute()
            
            if response.data and len(response.data) > 0:
                return response.data[0]
            else:
                raise Exception("MBTI 업데이트에 실패했습니다.")
        else:
            # 사용자가 없으면 새로 생성
            user_insert = {
                'id': user_id,
                'mbti': mbti
            }
            
            response = supabase.table('users')\
                .insert(user_insert)\
                .execute()
            
            if response.data and len(response.data) > 0:
                return response.data[0]
            else:
                raise Exception("사용자 생성에 실패했습니다.")
            
    except Exception as e:
        print(f"MBTI 저장 실패: {e}")
        raise e

def get_mbti_service(user_id: int, supabase: Client) -> Optional[str]:
    """
    사용자의 MBTI를 조회합니다.
    """
    try:
        response = supabase.table('users')\
            .select('mbti')\
            .eq('id', user_id)\
            .execute()
        
        if response.data and len(response.data) > 0:
            return response.data[0]['mbti']
        return None
        
    except Exception as e:
        print(f"MBTI 조회 실패 > user_id {user_id}: {e}")
        return None