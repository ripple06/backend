# app/main.py
from fastapi import FastAPI
from app.api import users, courses, locations, quiz

app = FastAPI(
    title="Ripple API",
    description="너의 진심이 물결(Ripple)처럼 번지는 곳, Reply(대답) + People(사람) + Ripple(파동)의 의미를 담은 서비스",
    version="0.1.0",
)

app.include_router(courses.router, prefix="/api", tags=["courses"])

@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "Welcome to Ripple API"}
