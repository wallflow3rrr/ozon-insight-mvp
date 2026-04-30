from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api import router
from database import engine
from models_db import Base
from seed import run_full_seed

app = FastAPI(title="OzonInsight API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)
    run_full_seed()

@app.get("/")
def root():
    return {"status": "OzonInsight API is running"}