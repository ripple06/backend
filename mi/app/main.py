# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import course, mbti, question, quiz, seaecosystem, seaemotion, user

app = FastAPI(
    title="Ripple API",
    description="너의 진심이 물결(Ripple)처럼 번지는 곳, Reply(대답) + People(사람) + Ripple(파동)의 의미를 담은 서비스",
    version="0.1.0",
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(course.router, tags=["courses"])
app.include_router(mbti.router, tags=["mbti"])
app.include_router(question.router, tags=["question"])
app.include_router(quiz.router, tags=["quiz"])
app.include_router(seaecosystem.router, tags=["seaecosystem"])
app.include_router(seaemotion.router, tags=['seaemotion'])
app.include_router(user.router, tags=['user'])

@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "Welcome to Ripple API"}
