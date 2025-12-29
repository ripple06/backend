# app/services/user_service.py
from supabase import Client
from app.schemas import schemas as user_schema

def create_user(supabase: Client, user: user_schema.UserCreate):
    """
    Supabase Auth를 사용하여 새로운 사용자를 생성합니다.
    MBTI 정보는 user_metadata에 저장합니다.
    """
    try:
        # Supabase 'sign_up'은 이메일을 필요로 하므로, username을 이메일 형식으로 가정합니다.
        # 또는 username과 email 필드를 분리해야 합니다. 여기서는 username이 이메일이라 가정합니다.
        res = supabase.auth.sign_up({
            "email": user.username,
            "password": user.password,
            "options": {
                "data": {
                    "mbti": user.mbti
                }
            }
        })
        # 성공 시, res.user 객체가 반환됩니다.
        return res.user
    except Exception as e:
        # Supabase API에서 반환하는 오류를 그대로 전달하거나 logging할 수 있습니다.
        # 예를 들어, 이미 존재하는 사용자인 경우 오류가 발생합니다.
        raise e
