from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

# Request Model
class MBTIRequest(BaseModel):
    mbti: str

# Response Model
class MBTIResponse(BaseModel):
    message: str

@app.post("/mbti/{user_id}", response_model=MBTIResponse)
async def save_mbti(user_id: str, request: MBTIRequest):
    """
    사용자의 MBTI를 저장합니다.
    
    - **user_id**: 사용자 ID
    - **mbti**: MBTI 유형 (예: AAAA, INFP 등)
    """
    # TODO: 실제로는 데이터베이스에 저장하는 로직이 필요합니다
    # 예: await db.save_mbti(user_id, request.mbti)
    
    return MBTIResponse(
        message=f"이얏 당신의 MBTI는 {request.mbti}이군요!"
    )

# 서버 실행 방법:
# uvicorn main:app --reload
# 문서 확인: http://127.0.0.1:8000/docs