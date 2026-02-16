import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "change-this-in-production-use-a-real-secret-key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./trivia_mundial.db")

# World Cup 2026 starts June 11, 2026
WORLD_CUP_START_DATE = "2026-06-11"
# Predictions lock 24 hours before the tournament starts
PREDICTION_LOCK_HOURS_BEFORE = 24

# Scoring
POINTS_EXACT_SCORE = 3
POINTS_CORRECT_RESULT = 1  # Right winner/draw but wrong score
POINTS_GROUP_QUALIFIER = 2  # Correctly predicted a team advances from group
POINTS_GROUP_FIRST = 3     # Correctly predicted 1st place in group
POINTS_CHAMPION = 10
POINTS_RUNNER_UP = 5
POINTS_TOP_SCORER = 5
POINTS_MVP = 5
