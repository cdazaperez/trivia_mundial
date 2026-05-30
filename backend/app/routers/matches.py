from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload

from app.core.database import get_db
from app.core.security import get_current_user, get_admin_user
from app.models.user import User
from app.models.tournament import Match, MatchPrediction, GroupPrediction, BonusPrediction, Phase, Team
from app.schemas.tournament import MatchResponse, MatchResultUpdate, BonusResultUpdate
from app.services.scoring import calculate_points_for_match, calculate_group_prediction_points, calculate_bonus_prediction_points
from app.services.standings import (
    calculate_group_standings,
    get_all_group_standings,
    get_best_third_place_teams,
)
from app.services.knockout import (
    get_knockout_status,
    PHASE_GENERATORS,
)

router = APIRouter(prefix="/api/matches", tags=["matches"])


# --- Standings endpoints (BEFORE /{match_id} to avoid route conflict) ---

@router.get("/standings/")
def get_all_standings(
    db: Session = Depends(get_db),
    _current_user: User = Depends(get_current_user),
):
    """Get standings for all 12 groups."""
    all_standings = get_all_group_standings(db)
    return [
        {"group_name": group, "standings": standings}
        for group, standings in sorted(all_standings.items())
    ]


@router.get("/standings/{group_name}")
def get_group_standings_endpoint(
    group_name: str,
    db: Session = Depends(get_db),
    _current_user: User = Depends(get_current_user),
):
    """Get standings for a specific group."""
    group_name = group_name.upper()
    if group_name not in "ABCDEFGHIJKL":
        raise HTTPException(status_code=400, detail="Grupo inválido")
    standings = calculate_group_standings(db, group_name)
    total = db.query(Match).filter(
        Match.phase == Phase.GROUP, Match.group_name == group_name
    ).count()
    finished = db.query(Match).filter(
        Match.phase == Phase.GROUP, Match.group_name == group_name, Match.is_finished == True
    ).count()
    return {
        "group_name": group_name,
        "standings": standings,
        "all_matches_finished": total > 0 and total == finished,
    }


@router.get("/third-place-ranking")
def get_third_place_ranking_endpoint(
    db: Session = Depends(get_db),
    _current_user: User = Depends(get_current_user),
):
    """Get ranking of all third-place teams."""
    return get_best_third_place_teams(db)


@router.get("/knockout-status")
def get_knockout_status_endpoint(
    db: Session = Depends(get_db),
    _current_user: User = Depends(get_current_user),
):
    """Get the status of each knockout phase."""
    return get_knockout_status(db)


@router.post("/generate-knockout/{phase}")
def generate_knockout_round(
    phase: str,
    db: Session = Depends(get_db),
    _admin: User = Depends(get_admin_user),
):
    """Generate knockout round matches. Admin only."""
    generator = PHASE_GENERATORS.get(phase)
    if not generator:
        valid = ", ".join(PHASE_GENERATORS.keys())
        raise HTTPException(
            status_code=400,
            detail=f"Fase inválida. Opciones válidas: {valid}",
        )

    try:
        matches = generator(db)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {
        "phase": phase,
        "matches_created": len(matches),
        "message": f"Se generaron {len(matches)} partidos para {phase}",
    }


@router.post("/update-teams")
def update_teams_endpoint(
    db: Session = Depends(get_db),
    _admin: User = Depends(get_admin_user),
):
    """Update team names/codes/flags in-place. Preserves predictions."""
    from app.services.seed_data import force_update_teams
    updated = force_update_teams(db)
    return {"detail": f"Se actualizaron {updated} equipos correctamente"}


@router.post("/reseed")
def reseed_endpoint(
    db: Session = Depends(get_db),
    _admin: User = Depends(get_admin_user),
):
    """Re-seed teams and group matches from scratch. Only if no predictions exist."""
    from app.services.seed_data import reseed_all
    try:
        reseed_all(db)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"detail": "Equipos y partidos re-seedeados correctamente"}


# --- Standard match endpoints ---

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

    # If this is a group match, recalculate group prediction points
    if match.phase == Phase.GROUP and match.group_name:
        calculate_group_prediction_points(db, match.group_name)

    db.refresh(match)
    return match


@router.post("/bonus-result")
def set_bonus_result(
    data: BonusResultUpdate,
    db: Session = Depends(get_db),
    _admin: User = Depends(get_admin_user),
):
    """Set the actual bonus result and calculate points. Admin only."""
    valid_types = ["champion", "runner_up", "top_scorer", "mvp"]
    if data.prediction_type not in valid_types:
        raise HTTPException(status_code=400, detail=f"Tipo inválido. Opciones: {', '.join(valid_types)}")

    updated = calculate_bonus_prediction_points(
        db,
        data.prediction_type,
        team_id=data.team_id,
        player_name=data.player_name,
    )
    return {"detail": f"Bonus '{data.prediction_type}' calculado. {updated} acertaron."}


@router.post("/reset-all")
def reset_all_results(
    db: Session = Depends(get_db),
    _admin: User = Depends(get_admin_user),
):
    """Reset all match results and points (for testing purposes)."""
    # Delete predictions on knockout matches (they will be regenerated)
    knockout_match_ids = [
        m.id for m in db.query(Match).filter(Match.phase != Phase.GROUP).all()
    ]
    if knockout_match_ids:
        db.query(MatchPrediction).filter(
            MatchPrediction.match_id.in_(knockout_match_ids)
        ).delete(synchronize_session="fetch")

    # Delete knockout matches entirely
    db.query(Match).filter(Match.phase != Phase.GROUP).delete()

    # Reset group match results
    db.query(Match).filter(Match.phase == Phase.GROUP).update({
        Match.home_score: None,
        Match.away_score: None,
        Match.is_finished: False,
    })
    # Reset all remaining prediction points
    db.query(MatchPrediction).update({MatchPrediction.points_earned: 0})
    db.query(GroupPrediction).update({GroupPrediction.points_earned: 0})
    db.query(BonusPrediction).update({BonusPrediction.points_earned: 0})
    db.commit()
    return {"detail": "Todos los resultados y puntos han sido reiniciados"}
