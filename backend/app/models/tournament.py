from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Enum as SAEnum
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import enum

from app.core.database import Base


class Phase(str, enum.Enum):
    GROUP = "group"
    ROUND_OF_32 = "round_of_32"
    ROUND_OF_16 = "round_of_16"
    QUARTER_FINAL = "quarter_final"
    SEMI_FINAL = "semi_final"
    THIRD_PLACE = "third_place"
    FINAL = "final"


class Team(Base):
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    code = Column(String(3), unique=True, nullable=False)  # FIFA code
    group_name = Column(String(1), nullable=True)  # A-L
    flag_emoji = Column(String(10), nullable=True)


class Match(Base):
    __tablename__ = "matches"

    id = Column(Integer, primary_key=True, index=True)
    match_number = Column(Integer, unique=True, nullable=False)
    phase = Column(SAEnum(Phase), nullable=False)
    group_name = Column(String(1), nullable=True)
    home_team_id = Column(Integer, ForeignKey("teams.id"), nullable=True)
    away_team_id = Column(Integer, ForeignKey("teams.id"), nullable=True)
    home_score = Column(Integer, nullable=True)  # Actual result
    away_score = Column(Integer, nullable=True)
    home_penalties = Column(Integer, nullable=True)
    away_penalties = Column(Integer, nullable=True)
    match_date = Column(DateTime, nullable=False)
    venue = Column(String(200), nullable=True)
    is_finished = Column(Boolean, default=False)
    matchday = Column(Integer, nullable=True)  # Jornada

    home_team = relationship("Team", foreign_keys=[home_team_id])
    away_team = relationship("Team", foreign_keys=[away_team_id])
    predictions = relationship("MatchPrediction", back_populates="match")


class MatchPrediction(Base):
    __tablename__ = "match_predictions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    match_id = Column(Integer, ForeignKey("matches.id"), nullable=False)
    home_score = Column(Integer, nullable=False)
    away_score = Column(Integer, nullable=False)
    points_earned = Column(Integer, default=0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="predictions")
    match = relationship("Match", back_populates="predictions")

    class Meta:
        unique_together = ("user_id", "match_id")


class GroupPrediction(Base):
    __tablename__ = "group_predictions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    group_name = Column(String(1), nullable=False)
    first_place_team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    second_place_team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    points_earned = Column(Integer, default=0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="group_predictions")
    first_place_team = relationship("Team", foreign_keys=[first_place_team_id])
    second_place_team = relationship("Team", foreign_keys=[second_place_team_id])


class BonusPrediction(Base):
    __tablename__ = "bonus_predictions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    prediction_type = Column(String(50), nullable=False)  # champion, runner_up, top_scorer, mvp
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=True)
    player_name = Column(String(100), nullable=True)
    points_earned = Column(Integer, default=0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="bonus_predictions")
    team = relationship("Team")
