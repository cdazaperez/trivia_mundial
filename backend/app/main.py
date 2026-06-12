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

    user_cols = [col["name"] for col in inspect(engine).get_columns("users")]
    if "has_paid" not in user_cols:
        conn.execute(text("ALTER TABLE users ADD COLUMN has_paid BOOLEAN DEFAULT 0"))

    pred_cols = [col["name"] for col in inspect(engine).get_columns("match_predictions")]
    if "home_penalties" not in pred_cols:
        conn.execute(text("ALTER TABLE match_predictions ADD COLUMN home_penalties INTEGER"))
    if "away_penalties" not in pred_cols:
        conn.execute(text("ALTER TABLE match_predictions ADD COLUMN away_penalties INTEGER"))

    existing_tables = inspect(engine).get_table_names()
    if "prediction_audit_log" not in existing_tables:
        conn.execute(text("""
            CREATE TABLE prediction_audit_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL REFERENCES users(id),
                action VARCHAR(20) NOT NULL,
                prediction_type VARCHAR(20) NOT NULL,
                prediction_id INTEGER NOT NULL,
                old_values VARCHAR(500),
                new_values VARCHAR(500) NOT NULL,
                ip_address VARCHAR(45),
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """))

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
        _fix_match_dates(db)
    finally:
        db.close()


def _fix_match_dates(db):
    """One-time fix: correct match #20 date (was 24h early)."""
    from app.models.tournament import Match
    from datetime import datetime, timezone
    m20 = db.query(Match).filter(Match.match_number == 20).first()
    if m20:
        correct = datetime(2026, 6, 14, 4, 0, tzinfo=timezone.utc)
        wrong = datetime(2026, 6, 13, 4, 0, tzinfo=timezone.utc)
        current = m20.match_date.replace(tzinfo=timezone.utc) if m20.match_date.tzinfo is None else m20.match_date
        if current == wrong:
            m20.match_date = correct
            db.commit()


@app.get("/api/health")
def health():
    return {"status": "ok", "app": "Trivia Mundial 2026 - Amigos"}
