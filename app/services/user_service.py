# app/services/user_service.py
from supabase import Client
from typing import Optional
import hashlib

def hash_password(password: str) -> str:
    """
    비밀번호를 해시화합니다.
    """
    return hashlib.sha256(password.encode()).hexdigest()

def signup_service(name: str, password: str, supabase: Client) -> dict:
    """
    회원가입을 처리합니다.
    """
    try:
        # 이름 중복 확인 (선택사항)
        existing_user = supabase.table('users')\
            .select('id')\
            .eq('name', name)\
            .execute()
        
        if existing_user.data and len(existing_user.data) > 0:
            raise ValueError("이미 존재하는 이름입니다.")
        
        # 비밀번호 해시화
        hashed_password = hash_password(password)
        
        # 사용자 생성
        user_insert = {
            'name': name,
            'password': hashed_password
        }
        
        response = supabase.table('users').insert(user_insert).execute()
        
        if response.data and len(response.data) > 0:
            return response.data[0]
        else:
            raise Exception("회원가입에 실패했습니다.")
            
    except ValueError:
        raise
    except Exception as e:
        print(f"회원가입 실패: {e}")
        raise e

def verify_user(name: str, password: str, supabase: Client) -> Optional[dict]:
    """
    로그인 시 사용자 인증을 처리합니다.
    """
    try:
        hashed_password = hash_password(password)
        
        response = supabase.table('users')\
            .select('id, name, mbti')\
            .eq('name', name)\
            .eq('password', hashed_password)\
            .execute()
        
        if response.data and len(response.data) > 0:
            return response.data[0]
        return None
        
    except Exception as e:
        print(f"사용자 인증 실패: {e}")
        return None