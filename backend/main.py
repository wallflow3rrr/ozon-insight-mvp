from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api import router
from database import engine
from models_db import Base

app = FastAPI(title="OzonInsight API (PostgreSQL)", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

# Примечание: Поскольку мы используем Alembic, вызывать Base.metadata.create_all() 
# в main.py больше НЕ нужно. Таблицы управляются миграциями.
# Данные мы заполним отдельной командой.

@app.get("/")
def root():
    return {"status": "OzonInsight API is running on PostgreSQL!"}