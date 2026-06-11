from pydantic import BaseModel, field_validator
from datetime import datetime, timezone


class TeamResponse(BaseModel):
    id: int
    name: str
    code: str
    group_name: str | None
    flag_emoji: str | None

    model_config = {"from_attributes": True}


class MatchResponse(BaseModel):
    id: int
    match_number: int
    phase: str
    group_name: str | None
    home_team: TeamResponse | None
    away_team: TeamResponse | None
    home_score: int | None
    away_score: int | None
    home_penalties: int | None = None
    away_penalties: int | None = None
    match_date: datetime
    venue: str | None
    is_finished: bool
    matchday: int | None

    @field_validator("match_date", mode="before")
    @classmethod
    def ensure_utc(cls, v: datetime) -> datetime:
        if isinstance(v, datetime) and v.tzinfo is None:
            return v.replace(tzinfo=timezone.utc)
        return v

    model_config = {"from_attributes": True}


class MatchResultUpdate(BaseModel):
    home_score: int
    away_score: int
    home_penalties: int | None = None
    away_penalties: int | None = None


class PredictionCreate(BaseModel):
    match_id: int
    home_score: int
    away_score: int
    home_penalties: int | None = None
    away_penalties: int | None = None


class PredictionResponse(BaseModel):
    id: int
    match_id: int
    home_score: int
    away_score: int
    home_penalties: int | None = None
    away_penalties: int | None = None
    points_earned: int
    match: MatchResponse | None = None

    model_config = {"from_attributes": True}


class GroupPredictionCreate(BaseModel):
    group_name: str
    first_place_team_id: int
    second_place_team_id: int


class GroupPredictionResponse(BaseModel):
    id: int
    group_name: str
    first_place_team: TeamResponse
    second_place_team: TeamResponse
    points_earned: int

    model_config = {"from_attributes": True}


class BonusPredictionCreate(BaseModel):
    prediction_type: str  # champion, runner_up, top_scorer, mvp
    team_id: int | None = None
    player_name: str | None = None


class BonusPredictionResponse(BaseModel):
    id: int
    prediction_type: str
    team: TeamResponse | None = None
    player_name: str | None = None
    points_earned: int

    model_config = {"from_attributes": True}


class BonusResultUpdate(BaseModel):
    prediction_type: str  # champion, runner_up, top_scorer, mvp
    team_id: int | None = None
    player_name: str | None = None


class LeaderboardEntry(BaseModel):
    user_id: int
    username: str
    full_name: str
    total_points: int
    exact_scores: int
    correct_results: int
    group_points: int
    bonus_points: int


class PhaseLeaderboard(BaseModel):
    phase: str
    entries: list[LeaderboardEntry]
