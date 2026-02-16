import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.database import engine, Base, SessionLocal
from app.routers import auth, matches, predictions, leaderboard
from app.services.seed_data import seed_all

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Trivia Mundial 2026",
    description="App de pronósticos para el Mundial de Fútbol 2026",
    version="1.0.0",
)

# CORS
cors_origins_env = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:3000")
cors_origins = ["*"] if cors_origins_env.strip() == "*" else cors_origins_env.split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=cors_origins != ["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth.router)
app.include_router(matches.router)
app.include_router(predictions.router)
app.include_router(leaderboard.router)


@app.on_event("startup")
def startup():
    db = SessionLocal()
    try:
        seed_all(db)
    finally:
        db.close()


@app.get("/api/health")
def health():
    return {"status": "ok", "app": "Trivia Mundial 2026"}
