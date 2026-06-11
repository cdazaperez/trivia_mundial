import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "change-this-in-production-use-a-real-secret-key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./trivia_mundial.db")

# World Cup 2026 first match: June 11, 2026 at 19:00 UTC (2:00 PM Colombia)
WORLD_CUP_START_DATETIME = "2026-06-11T19:00:00"
# Predictions lock 10 minutes before the tournament starts
PREDICTION_LOCK_MINUTES_BEFORE = 10

# Scoring
POINTS_EXACT_SCORE = 3
POINTS_CORRECT_RESULT = 1  # Right winner/draw but wrong score
POINTS_PENALTY_WINNER = 1  # Correctly predicted penalty winner in knockout
POINTS_GROUP_QUALIFIER = 2  # Correctly predicted a team advances from group
POINTS_GROUP_FIRST = 3     # Correctly predicted 1st place in group
POINTS_CHAMPION = 10
POINTS_RUNNER_UP = 5
POINTS_TOP_SCORER = 5
POINTS_MVP = 5

# Entry fee and prize distribution
ENTRY_FEE = 50000  # pesos per participant
PRIZE_DISTRIBUTION = [0.60, 0.25, 0.10]  # 1st, 2nd, 3rd
ADMIN_FEE_PCT = 0.05  # 5% servicios de administración
