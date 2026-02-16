from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload

from app.core.database import get_db
from app.core.security import get_current_user, get_admin_user
from app.models.user import User
from app.models.tournament import Match, Phase, Team
from app.schemas.tournament import MatchResponse, MatchResultUpdate
from app.services.scoring import calculate_points_for_match

router = APIRouter(prefix="/api/matches", tags=["matches"])


@router.get("/", response_model=list[MatchResponse])
def get_matches(
    phase: str | None = None,
    group: str | None = None,
    matchday: int | None = None,
    db: Session = Depends(get_db),
    _current_user: User = Depends(get_current_user),
):
    query = db.query(Match).options(
        joinedload(Match.home_team), joinedload(Match.away_team)
    )
    if phase:
        query = query.filter(Match.phase == phase)
    if group:
        query = query.filter(Match.group_name == group)
    if matchday:
        query = query.filter(Match.matchday == matchday)
    return query.order_by(Match.match_date, Match.match_number).all()


@router.get("/{match_id}", response_model=MatchResponse)
def get_match(match_id: int, db: Session = Depends(get_db), _current_user: User = Depends(get_current_user)):
    match = db.query(Match).options(
        joinedload(Match.home_team), joinedload(Match.away_team)
    ).filter(Match.id == match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Partido no encontrado")
    return match


@router.put("/{match_id}/result", response_model=MatchResponse)
def update_match_result(
    match_id: int,
    result: MatchResultUpdate,
    db: Session = Depends(get_db),
    _admin: User = Depends(get_admin_user),
):
    match = db.query(Match).options(
        joinedload(Match.home_team), joinedload(Match.away_team)
    ).filter(Match.id == match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Partido no encontrado")

    match.home_score = result.home_score
    match.away_score = result.away_score
    match.is_finished = True
    db.commit()

    # Calculate points for all predictions on this match
    calculate_points_for_match(db, match)

    db.refresh(match)
    return match


@router.get("/phases/list", response_model=list[str])
def get_phases(_current_user: User = Depends(get_current_user)):
    return [p.value for p in Phase]


@router.get("/teams/all", response_model=list[dict])
def get_all_teams(db: Session = Depends(get_db), _current_user: User = Depends(get_current_user)):
    teams = db.query(Team).order_by(Team.group_name, Team.name).all()
    return [
        {"id": t.id, "name": t.name, "code": t.code, "group_name": t.group_name, "flag_emoji": t.flag_emoji}
        for t in teams
    ]
