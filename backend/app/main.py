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
        _fix_knockout_schedule(db)
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


def _fix_knockout_schedule(db):
    """Update existing knockout matches with correct FIFA dates, venues, and bracket."""
    from app.models.tournament import Match, Phase, Team
    from app.services.knockout import MATCH_SCHEDULE, R16_MATCHES, _get_match_winner
    from app.services.knockout import R32_MATCHES, _get_team_by_position
    from app.services.standings import get_all_group_standings, get_best_third_place_teams
    from app.services.knockout import _assign_third_place_teams

    updated = False

    # Fix dates and venues for all existing knockout matches
    for match_num, (correct_date, correct_venue) in MATCH_SCHEDULE.items():
        match = db.query(Match).filter(Match.match_number == match_num).first()
        if not match:
            continue
        current_date = match.match_date
        if current_date and current_date.tzinfo is None:
            current_date = current_date.replace(tzinfo=correct_date.tzinfo)
        if current_date != correct_date or match.venue != correct_venue:
            match.match_date = correct_date
            match.venue = correct_venue
            updated = True

    # Fix R32 third-place team assignments using FIFA Annex C
    r32_exists = db.query(Match).filter(Match.phase == Phase.ROUND_OF_32).count()
    if r32_exists > 0:
        try:
            standings = get_all_group_standings(db)
            third_place_ranking = get_best_third_place_teams(db)
            qualifying_groups = sorted(
                [t["group"] for t in third_place_ranking if t["qualifies"]]
            )
            if len(qualifying_groups) == 8:
                assignment = _assign_third_place_teams(qualifying_groups)
                third_place_teams = {}
                for entry in third_place_ranking:
                    if entry["qualifies"]:
                        third_place_teams[entry["group"]] = entry["team_id"]

                for match_num, home_pos, away_pos in R32_MATCHES:
                    if away_pos is not None:
                        continue
                    match = db.query(Match).filter(
                        Match.match_number == match_num
                    ).first()
                    if not match or match.is_finished:
                        continue
                    assigned_group = assignment[match_num]
                    correct_away = third_place_teams[assigned_group]
                    correct_home = _get_team_by_position(standings, home_pos)
                    if match.away_team_id != correct_away or match.home_team_id != correct_home:
                        match.home_team_id = correct_home
                        match.away_team_id = correct_away
                        updated = True
        except (ValueError, KeyError):
            pass

    # Fix R16 bracket: matches 93 and 94 had swapped sources.
    r16_bracket_fix = {93: (83, 84), 94: (81, 82)}
    for match_num, (src_a, src_b) in r16_bracket_fix.items():
        r16_match = db.query(Match).filter(Match.match_number == match_num).first()
        if not r16_match or r16_match.is_finished:
            continue
        src_a_match = db.query(Match).filter(Match.match_number == src_a).first()
        src_b_match = db.query(Match).filter(Match.match_number == src_b).first()
        if not src_a_match or not src_b_match:
            continue
        if not src_a_match.is_finished or not src_b_match.is_finished:
            continue
        try:
            correct_home = _get_match_winner(db, src_a)
            correct_away = _get_match_winner(db, src_b)
            if r16_match.home_team_id != correct_home or r16_match.away_team_id != correct_away:
                r16_match.home_team_id = correct_home
                r16_match.away_team_id = correct_away
                updated = True
        except ValueError:
            pass

    if updated:
        db.commit()


@app.get("/api/health")
def health():
    return {"status": "ok", "app": "Trivia Mundial 2026 - Amigos"}
