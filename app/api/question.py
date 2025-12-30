from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List

app = FastAPI()

# Request Model
class QuestionCreate(BaseModel):
    title: str
    content: str

# Response Models
class QuestionResponse(BaseModel):
    title: str
    content: str
    message: str

class QuestionListItem(BaseModel):
    title: str
    content: str
    message: str

class QuestionListResponse(BaseModel):
    questions: List[QuestionListItem]


# 1. 질문 생성 API
@app.post("/questions/{user_id}")
async def create_question(user_id: str, question: QuestionCreate):
    """
    코스 탐방 완료 후 다음 사람에게 질문 생성
    """
    # TODO: 데이터베이스에 질문 저장
    # - user_id로 사용자 확인
    # - question.title, question.content 저장
    
    return {
        "message": "당신의 질문이 생성되었습니다!"
    }


# 2. 질문 단일 보기 API
@app.get("/questions/{course_id}", response_model=QuestionResponse)
async def get_question(course_id: str):
    """
    특정 코스의 질문 조회
    """
    # TODO: 데이터베이스에서 course_id에 해당하는 질문 조회
    
    # 예시 응답
    return {
        "title": "제목",
        "content": "뻔딱뻔딱",
        "message": "조회 성공!"
    }


# 3. 질문 목록 보기 API
@app.get("/questions/{course_id}/list", response_model=QuestionListResponse)
async def get_question_list(course_id: str):
    """
    특정 코스의 모든 질문 목록 조회
    """
    # TODO: 데이터베이스에서 course_id에 해당하는 모든 질문 조회
    
    # 예시 응답
    return {
        "questions": [
            {
                "title": "제목",
                "content": "뻔딱뻔딱",
                "message": "조회 성공!"
            },
            {
                "title": "제목",
                "content": "뻔딱뻔딱",
                "message": "조회 성공!"
            }
        ]
    }