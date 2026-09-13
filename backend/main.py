from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from api.chat_router import router as chat_router
from api.disease_router import router as disease_router
from api.weather_router import router as weather_router

limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="Crop Advisory Chatbot API",
    description="AI-powered crop advisory chatbot with RAG, disease diagnosis, and weather integration.",
    version="1.0.0",
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router, prefix="/api")
app.include_router(disease_router, prefix="/api")
app.include_router(weather_router, prefix="/api")


@app.get("/health")
def health_check():
    return {"status": "ok"}
