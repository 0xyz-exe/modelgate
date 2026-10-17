"""FastAPI main application"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.db.session import engine, Base
from app.api.v1.chat import router as chat_router

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="ModelGate API",
    description="API Gateway & AI Usage Metering Platform",
    version="0.1.0",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(chat_router, prefix="/v1", tags=["chat"])


@app.get("/")
async def root():
    return {
        "name": "ModelGate",
        "version": "0.1.0",
        "status": "running",
        "demo_mode": settings.demo_mode,
    }


@app.get("/health")
async def health():
    return {"status": "healthy"}
