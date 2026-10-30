from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import CORS_ORIGINS, USE_CREDENTIALS, IS_DEV

# Import routers
from api.routers import auth_router, chat_router, ml_router

# Initialize FastAPI app
# Interactive API docs only in development
app = FastAPI(
    title="LyricMind NLP API",
    version="1.0.0",
    docs_url="/docs" if IS_DEV else None,
    redoc_url="/redoc" if IS_DEV else None,
    openapi_url="/openapi.json" if IS_DEV else None,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=USE_CREDENTIALS,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Include routers
app.include_router(auth_router.router)
app.include_router(chat_router.router)
app.include_router(ml_router.router)

# ─── Routes ────────────────────────────────────────────────────────────────────
@app.get("/")
def root():
    """Health check endpoint"""
    return {"message": "LyricMind API is running 🎵"}
