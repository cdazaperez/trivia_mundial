import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from sqlalchemy import inspect, text

from app.core.database import engine, Base, SessionLocal
from app.routers import auth, matches, predictions, leaderboard
from app.services.seed_data import seed_all

# Create tables
Base.metadata.create_all(bind=engine)

# Add new columns if missing (lightweight migration for SQLite)
with engine.connect() as conn:
    match_cols = [col["name"] for col in inspect(engine).get_columns("matches")]
    if "home_penalties" not in match_cols:
        conn.execute(text("ALTER TABLE matches ADD COLUMN home_penalties INTEGER"))
    if "away_penalties" not in match_cols:
        conn.execute(text("ALTER TABLE matches ADD COLUMN away_penalties INTEGER"))

    pred_cols = [col["name"] for col in inspect(engine).get_columns("match_predictions")]
    if "home_penalties" not in pred_cols:
        conn.execute(text("ALTER TABLE match_predictions ADD COLUMN home_penalties INTEGER"))
    if "away_penalties" not in pred_cols:
        conn.execute(text("ALTER TABLE match_predictions ADD COLUMN away_penalties INTEGER"))
    conn.commit()

app = FastAPI(
    title="Trivia Mundial 2026 - Amigos",
    description="Plataforma de entretenimiento entre amigos - Pronósticos del Mundial FIFA 2026",
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
    return {"status": "ok", "app": "Trivia Mundial 2026 - Amigos"}
