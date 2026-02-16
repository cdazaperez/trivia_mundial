from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.tournament import (
    MatchPrediction, GroupPrediction, BonusPrediction, Match, Phase,
)
from app.schemas.tournament import LeaderboardEntry

router = APIRouter(prefix="/api/leaderboard", tags=["leaderboard"])


@router.get("/", response_model=list[LeaderboardEntry])
def get_leaderboard(
    phase: str | None = None,
    db: Session = Depends(get_db),
    _current_user: User = Depends(get_current_user),
):
    users = db.query(User).filter(User.is_active == True, User.is_admin == False).all()
    entries = []

    for user in users:
        # Match prediction points
        match_query = db.query(MatchPrediction).join(Match).filter(
            MatchPrediction.user_id == user.id,
            Match.is_finished == True,
        )
        if phase:
            match_query = match_query.filter(Match.phase == phase)

        match_predictions = match_query.all()
        match_points = sum(p.points_earned for p in match_predictions)
        exact_scores = sum(1 for p in match_predictions if p.points_earned == 3)
        correct_results = sum(1 for p in match_predictions if p.points_earned == 1)

        # Group prediction points
        group_points = 0
        if not phase or phase == Phase.GROUP.value:
            group_preds = db.query(GroupPrediction).filter(
                GroupPrediction.user_id == user.id
            ).all()
            group_points = sum(p.points_earned for p in group_preds)

        # Bonus prediction points
        bonus_points = 0
        if not phase:
            bonus_preds = db.query(BonusPrediction).filter(
                BonusPrediction.user_id == user.id
            ).all()
            bonus_points = sum(p.points_earned for p in bonus_preds)

        total = match_points + group_points + bonus_points

        entries.append(LeaderboardEntry(
            user_id=user.id,
            username=user.username,
            full_name=user.full_name,
            total_points=total,
            exact_scores=exact_scores,
            correct_results=correct_results,
            group_points=group_points,
            bonus_points=bonus_points,
        ))

    entries.sort(key=lambda e: e.total_points, reverse=True)
    return entries


@router.get("/phase-winners", response_model=dict)
def get_phase_winners(
    db: Session = Depends(get_db),
    _current_user: User = Depends(get_current_user),
):
    """Get top 2 winners for each completed phase."""
    results = {}
    for phase in Phase:
        phase_matches = db.query(Match).filter(
            Match.phase == phase.value,
            Match.is_finished == True,
        ).count()

        total_matches = db.query(Match).filter(Match.phase == phase.value).count()

        if total_matches == 0:
            continue

        # Get leaderboard for this phase
        users = db.query(User).filter(User.is_active == True, User.is_admin == False).all()
        phase_entries = []

        for user in users:
            preds = db.query(MatchPrediction).join(Match).filter(
                MatchPrediction.user_id == user.id,
                Match.phase == phase.value,
                Match.is_finished == True,
            ).all()
            points = sum(p.points_earned for p in preds)
            phase_entries.append({
                "username": user.username,
                "full_name": user.full_name,
                "points": points,
            })

        phase_entries.sort(key=lambda e: e["points"], reverse=True)

        results[phase.value] = {
            "completed_matches": phase_matches,
            "total_matches": total_matches,
            "all_completed": phase_matches == total_matches,
            "top_2": phase_entries[:2] if phase_entries else [],
        }

    return results
