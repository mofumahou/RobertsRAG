from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import health, chat

app = FastAPI(title="RobertsRAG Chat", version="0.0.1")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Subject to change in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)