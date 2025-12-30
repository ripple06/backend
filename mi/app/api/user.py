# app/api/user.py
from fastapi import APIRouter, Depends, HTTPException
from supabase import Client
from app.schemas.schemas import *
from app.services.user_service import signup_service
from app.core.supabase_client import get_supabase

router = APIRouter()

@router.post("/signup", response_model=Message)
async def signup(
    request: SignupRequest,
    supabase: Client = Depends(get_supabase)
):
    """
    회원가입을 처리합니다.
    
    - **name**: 사용자 이름
    - **password**: 비밀번호
    """
    try:
        result = signup_service(request.name, request.password, supabase)
        return Message(message="회원가입 성공!")
    except ValueError as e:
        raise HTTPException(400, detail=str(e))
    except Exception as e:
        raise HTTPException(500, detail="회원가입 중 오류가 발생했습니다.")