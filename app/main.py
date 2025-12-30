# app/main.py
from fastapi import FastAPI
from app.api import course, mbti, question, quiz, seaecosystem, seaemotion

app = FastAPI(
    title="Ripple API",
    description="너의 진심이 물결(Ripple)처럼 번지는 곳, Reply(대답) + People(사람) + Ripple(파동)의 의미를 담은 서비스",
    version="0.1.0",
)

app.include_router(course.router, prefix="/api", tags=["courses"])
app.include_router(mbti.router, prefix="/api", tags=["mbti"])
app.include_router(question.router, prefix="/api", tag=["question"])
app.include_router(quiz.router, prefix="/api", tag=["quiz"])
app.include_router(seaecosystem.router, prefix="/api", tag=["seaecosystem"])
app.include_router(seaemotion.router, prefix="/api", tag=['seaemotion'])

@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "Welcome to Ripple API"}
