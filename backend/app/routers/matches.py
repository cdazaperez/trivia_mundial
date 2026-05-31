from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload

from app.core.database import get_db
from app.core.security import get_current_user, get_admin_user
from app.models.user import User
from app.models.tournament import Match, MatchPrediction, GroupPrediction, BonusPrediction, Phase, Team
from app.schemas.tournament import MatchResponse, MatchResultUpdate, BonusResultUpdate
from app.services.scoring import calculate_points_for_match, calculate_group_prediction_points, calculate_bonus_prediction_points
from app.services.seed_data import force_update_teams, force_update_matches
from app.services.standings import (
    calculate_group_standings,
    get_all_group_standings,
    get_best_third_place_teams,
)
from app.services.knockout import (
    get_knockout_status,
    PHASE_GENERATORS,
    generate_round_of_32,
    generate_round_of_16,
    generate_quarter_finals,
    generate_semi_finals,
    generate_finals,
)
from app.services.standings import are_all_group_matches_finished

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


@router.post("/auto-generate-next")
def auto_generate_next_phase(
    db: Session = Depends(get_db),
    _admin: User = Depends(get_admin_user),
):
    """Auto-generate the next knockout phase if previous phase is complete. Admin only."""
    phase_chain = [
        (Phase.GROUP, "round_of_32", generate_round_of_32),
        (Phase.ROUND_OF_32, "round_of_16", generate_round_of_16),
        (Phase.ROUND_OF_16, "quarter_final", generate_quarter_finals),
        (Phase.QUARTER_FINAL, "semi_final", generate_semi_finals),
        (Phase.SEMI_FINAL, "finals", generate_finals),
    ]

    for prev_phase, next_name, generator_fn in phase_chain:
        try:
            matches = generator_fn(db)
            return {
                "phase": next_name,
                "matches_created": len(matches),
                "message": f"Se generaron {len(matches)} partidos para {next_name}",
            }
        except (ValueError, Exception):
            continue

    return {"message": "No hay fases pendientes por generar"}


@router.post("/update-teams")
def update_teams_endpoint(
    db: Session = Depends(get_db),
    _admin: User = Depends(get_admin_user),
):
    """Update team names/codes/flags and match dates/venues in-place. Preserves predictions."""
    teams_updated = force_update_teams(db)
    matches_updated = force_update_matches(db)
    return {"detail": f"Se actualizaron {teams_updated} equipos y {matches_updated} partidos correctamente"}


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


@router.put("/{match_id}/result")
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

    is_knockout = match.phase != Phase.GROUP
    is_draw = result.home_score == result.away_score

    if is_knockout and is_draw:
        if result.home_penalties is None or result.away_penalties is None:
            raise HTTPException(
                status_code=400,
                detail="Partido eliminatorio empatado: debes ingresar el resultado de penales.",
            )
        if result.home_penalties == result.away_penalties:
            raise HTTPException(
                status_code=400,
                detail="Los penales no pueden terminar empatados.",
            )

    match.home_score = result.home_score
    match.away_score = result.away_score
    match.home_penalties = result.home_penalties if is_knockout else None
    match.away_penalties = result.away_penalties if is_knockout else None
    match.is_finished = True
    db.commit()

    calculate_points_for_match(db, match)

    if match.phase == Phase.GROUP and match.group_name:
        calculate_group_prediction_points(db, match.group_name)

    db.refresh(match)

    auto_generated = _try_auto_generate_next_phase(db, match.phase)

    response = {
        "id": match.id,
        "match_number": match.match_number,
        "phase": match.phase.value if hasattr(match.phase, 'value') else match.phase,
        "home_score": match.home_score,
        "away_score": match.away_score,
        "home_penalties": match.home_penalties,
        "away_penalties": match.away_penalties,
        "is_finished": match.is_finished,
        "detail": "Resultado guardado y puntos calculados",
        "auto_generated": auto_generated,
    }
    return response


def _try_auto_generate_next_phase(db: Session, current_phase: str) -> dict | None:
    """Try to auto-generate the next knockout phase if all matches in current phase are done."""
    NEXT_PHASE = {
        Phase.GROUP: ("round_of_32", generate_round_of_32),
        Phase.ROUND_OF_32: ("round_of_16", generate_round_of_16),
        Phase.ROUND_OF_16: ("quarter_final", generate_quarter_finals),
        Phase.QUARTER_FINAL: ("semi_final", generate_semi_finals),
        Phase.SEMI_FINAL: ("finals", generate_finals),
    }

    generator_info = NEXT_PHASE.get(current_phase)
    if not generator_info:
        return None

    phase_name, generator_fn = generator_info

    try:
        matches = generator_fn(db)
        return {
            "phase": phase_name,
            "matches_created": len(matches),
            "message": f"Se generaron automáticamente {len(matches)} partidos para la siguiente fase",
        }
    except (ValueError, Exception):
        return None


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
        Match.home_penalties: None,
        Match.away_penalties: None,
        Match.is_finished: False,
    })
    # Reset all remaining prediction points
    db.query(MatchPrediction).update({MatchPrediction.points_earned: 0})
    db.query(GroupPrediction).update({GroupPrediction.points_earned: 0})
    db.query(BonusPrediction).update({BonusPrediction.points_earned: 0})
    db.commit()
    return {"detail": "Todos los resultados y puntos han sido reiniciados"}
