# app/routes/mbti.py
from fastapi import APIRouter, Depends, HTTPException
from supabase import Client
from app.schemas.schemas import *
from app.services.mbti_service import save_mbti_service, get_mbti_service
from app.core.supabase_client import get_supabase

router = APIRouter()

@router.post("/mbti/{user_id}", response_model=Message)
async def save_mbti(
    user_id: int, 
    request: Mbti,
    supabase: Client = Depends(get_supabase)
):
    """
    사용자의 MBTI를 저장합니다.
     
    - **user_id**: 사용자 ID
    - **mbti**: MBTI 유형 (예: INFP, ENFJ 등)
    """
    try:
        result = save_mbti_service(user_id, request.mbti, supabase)
        return Message(
            message=f"이얏 당신의 MBTI는 {request.mbti}이군요!"
        )
    except Exception as e:
        raise HTTPException(500, detail="MBTI 저장 중 오류가 발생했습니다.")

@router.get("/mbti/{user_id}", response_model=Mbti)
async def get_mbti(
    user_id: int,
    supabase: Client = Depends(get_supabase)
):
    """
    사용자의 MBTI를 조회합니다.
    
    - **user_id**: 사용자 ID
    """
    try:
        mbti = get_mbti_service(user_id, supabase)
        
        if not mbti:
            raise HTTPException(404, detail="사용자를 찾을 수 없거나 MBTI가 설정되지 않았습니다.")
        
        return Mbti(mbti=mbti)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, detail="MBTI 조회 중 오류가 발생했습니다.")