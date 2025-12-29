# app/api/users.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from supabase import Client, APIResponse, User as SupabaseUser

from app.schemas import schemas as user_schema
from app.schemas import course as course_schema
from app.services import user_service
from app.core.supabase_client import get_supabase
from typing import List

router = APIRouter(
    prefix="/users",
    tags=["Users & Authentication"],
)

# 이 scheme은 토큰을 추출하는 데 사용되지만, 검증은 supabase.auth.get_user가 직접 수행합니다.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/token")

async def get_current_user(token: str = Depends(oauth2_scheme), supabase: Client = Depends(get_supabase)) -> SupabaseUser:
    """
    요청 헤더의 JWT를 사용하여 현재 로그인된 Supabase 사용자를 가져옵니다.
    """
    try:
        # 토큰을 사용하여 사용자 정보 가져오기
        user_response = supabase.auth.get_user(token)
        return user_response.user
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

@router.post("/register", response_model=user_schema.User)
def register_user(user: user_schema.UserCreate, supabase: Client = Depends(get_supabase)):
    """
    새로운 사용자를 등록합니다 (회원가입).
    사용자 이름으로 이메일을 사용합니다.
    """
    try:
        # User service를 통해 Supabase에 사용자 생성 요청
        new_user = user_service.create_user(supabase, user)
        # Supabase 응답에서 필요한 정보만 추출하여 반환
        return user_schema.User(
            id=new_user.id,
            email=new_user.email,
            mbti=new_user.user_metadata.get("mbti")
        )
    except Exception as e:
        # Supabase 클라이언트에서 발생하는 예외 처리
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/token", response_model=user_schema.Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), supabase: Client = Depends(get_supabase)):
    """
    사용자 로그인 후 액세스 토큰을 발급받습니다.
    """
    try:
        # Supabase에 이메일(username)과 비밀번호로 로그인 요청
        response: APIResponse = supabase.auth.sign_in_with_password({
            "email": form_data.username,
            "password": form_data.password
        })
        # 성공 시, response.session.access_token이 JWT입니다.
        return user_schema.Token(
            access_token=response.session.access_token,
            token_type="bearer"
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

@router.get("/me", response_model=user_schema.User)
async def read_users_me(current_user: SupabaseUser = Depends(get_current_user)):
    """
    현재 로그인된 사용자의 정보를 가져옵니다.
    """
    return user_schema.User(
        id=current_user.id,
        email=current_user.email,
        mbti=current_user.user_metadata.get("mbti")
    )

@router.get("/me/courses", response_model=List[course_schema.Course])
def read_my_courses(current_user: SupabaseUser = Depends(get_current_user), supabase: Client = Depends(get_supabase)):
    """
    내가 이때 동안 다닌 코스 기록을 확인합니다.
    (Supabase에 맞게 로직 재작성 필요)
    """
    # TODO: 'user_course_association'와 같은 연결 테이블과 'courses' 테이블에서
    # current_user.id를 기준으로 데이터를 조회하는 로직 구현
    
    # 예시: supabase.table("user_courses").select("*, courses(*)").eq("user_id", current_user.id).execute()
    
    # 현재는 빈 리스트를 반환합니다.
    return []