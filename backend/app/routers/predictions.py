from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from app.core.config import WORLD_CUP_START_DATE, PREDICTION_LOCK_HOURS_BEFORE
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.tournament import Match, MatchPrediction, GroupPrediction, BonusPrediction, Team, Phase
from app.schemas.tournament import (
    PredictionCreate, PredictionResponse,
    GroupPredictionCreate, GroupPredictionResponse,
    BonusPredictionCreate, BonusPredictionResponse,
)

router = APIRouter(prefix="/api/predictions", tags=["predictions"])


def check_admin_cannot_predict(user: User):
    """Admin cannot participate in the contest."""
    if user.is_admin:
        raise HTTPException(
            status_code=403,
            detail="El administrador no puede participar en el concurso de pronósticos.",
        )


def check_group_predictions_locked():
    """Check if group predictions are locked (24h before World Cup starts)."""
    lock_date = datetime.strptime(WORLD_CUP_START_DATE, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    lock_deadline = lock_date - timedelta(hours=PREDICTION_LOCK_HOURS_BEFORE)
    if datetime.now(timezone.utc) >= lock_deadline:
        raise HTTPException(
            status_code=403,
            detail="Los pronósticos de grupos están bloqueados. No se pueden modificar 24 horas antes del inicio del mundial.",
        )


def check_bonus_predictions_locked(db: Session):
    """Check if bonus predictions are locked (when the group phase ends / knockout starts)."""
    first_knockout = (
        db.query(Match)
        .filter(Match.phase != Phase.GROUP)
        .order_by(Match.match_date)
        .first()
    )
    if first_knockout:
        match_date = first_knockout.match_date
        if match_date.tzinfo is None:
            match_date = match_date.replace(tzinfo=timezone.utc)
        lock_time = match_date - timedelta(hours=1)
        if datetime.now(timezone.utc) >= lock_time:
            raise HTTPException(
                status_code=403,
                detail="Las apuestas bonus están bloqueadas. No se pueden modificar una vez iniciada la fase eliminatoria.",
            )


def check_match_prediction_locked(match: Match):
    """Check if a specific match prediction is locked (1h before match starts)."""
    if match.match_date.tzinfo is None:
        match_date = match.match_date.replace(tzinfo=timezone.utc)
    else:
        match_date = match.match_date
    lock_time = match_date - timedelta(hours=1)
    if datetime.now(timezone.utc) >= lock_time:
        raise HTTPException(
            status_code=403,
            detail="No se puede modificar el pronóstico 1 hora antes del partido.",
        )


# --- Match Predictions ---

@router.post("/match", response_model=PredictionResponse, status_code=201)
def create_match_prediction(
    prediction: PredictionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    check_admin_cannot_predict(current_user)

    match = db.query(Match).filter(Match.id == prediction.match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Partido no encontrado")

    if match.is_finished:
        raise HTTPException(status_code=400, detail="El partido ya terminó")

    check_match_prediction_locked(match)

    # Check if prediction already exists
    existing = db.query(MatchPrediction).filter(
        MatchPrediction.user_id == current_user.id,
        MatchPrediction.match_id == prediction.match_id,
    ).first()

    is_knockout = match.phase != Phase.GROUP
    is_draw = prediction.home_score == prediction.away_score

    pen_home = None
    pen_away = None
    if is_knockout and is_draw:
        if prediction.home_penalties is None or prediction.away_penalties is None:
            raise HTTPException(
                status_code=400,
                detail="En fase eliminatoria, si pronosticas empate debes incluir resultado de penales.",
            )
        if prediction.home_penalties == prediction.away_penalties:
            raise HTTPException(
                status_code=400,
                detail="Los penales no pueden terminar empatados.",
            )
        pen_home = prediction.home_penalties
        pen_away = prediction.away_penalties
    elif is_knockout and not is_draw:
        pen_home = None
        pen_away = None

    if existing:
        existing.home_score = prediction.home_score
        existing.away_score = prediction.away_score
        existing.home_penalties = pen_home
        existing.away_penalties = pen_away
        existing.updated_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(existing)
        return existing

    new_prediction = MatchPrediction(
        user_id=current_user.id,
        match_id=prediction.match_id,
        home_score=prediction.home_score,
        away_score=prediction.away_score,
        home_penalties=pen_home,
        away_penalties=pen_away,
    )
    db.add(new_prediction)
    db.commit()
    db.refresh(new_prediction)
    return new_prediction


@router.get("/match", response_model=list[PredictionResponse])
def get_my_predictions(
    phase: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(MatchPrediction).options(
        joinedload(MatchPrediction.match).joinedload(Match.home_team),
        joinedload(MatchPrediction.match).joinedload(Match.away_team),
    ).filter(MatchPrediction.user_id == current_user.id)

    if phase:
        query = query.join(Match).filter(Match.phase == phase)

    return query.all()


@router.get("/match/all", response_model=list[dict])
def get_all_predictions_for_match(
    match_id: int,
    db: Session = Depends(get_db),
    _current_user: User = Depends(get_current_user),
):
    """Get all users' predictions for a finished match."""
    match = db.query(Match).filter(Match.id == match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Partido no encontrado")

    # Only show others' predictions after match is finished
    if not match.is_finished:
        raise HTTPException(status_code=403, detail="Los pronósticos de otros usuarios solo son visibles después del partido")

    predictions = db.query(MatchPrediction).options(
        joinedload(MatchPrediction.user)
    ).filter(MatchPrediction.match_id == match_id).all()

    return [
        {
            "username": p.user.username,
            "full_name": p.user.full_name,
            "home_score": p.home_score,
            "away_score": p.away_score,
            "points_earned": p.points_earned,
        }
        for p in predictions
    ]


# --- Group Predictions ---

@router.post("/group", response_model=GroupPredictionResponse, status_code=201)
def create_group_prediction(
    prediction: GroupPredictionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    check_admin_cannot_predict(current_user)
    check_group_predictions_locked()

    # Validate teams belong to the group
    first_team = db.query(Team).filter(Team.id == prediction.first_place_team_id).first()
    second_team = db.query(Team).filter(Team.id == prediction.second_place_team_id).first()

    if not first_team or not second_team:
        raise HTTPException(status_code=404, detail="Equipo no encontrado")

    if first_team.group_name != prediction.group_name or second_team.group_name != prediction.group_name:
        raise HTTPException(status_code=400, detail="Los equipos deben pertenecer al grupo seleccionado")

    if first_team.id == second_team.id:
        raise HTTPException(status_code=400, detail="Debes seleccionar equipos diferentes")

    existing = db.query(GroupPrediction).filter(
        GroupPrediction.user_id == current_user.id,
        GroupPrediction.group_name == prediction.group_name,
    ).first()

    if existing:
        existing.first_place_team_id = prediction.first_place_team_id
        existing.second_place_team_id = prediction.second_place_team_id
        db.commit()
        db.refresh(existing)
        return existing

    new_pred = GroupPrediction(
        user_id=current_user.id,
        group_name=prediction.group_name,
        first_place_team_id=prediction.first_place_team_id,
        second_place_team_id=prediction.second_place_team_id,
    )
    db.add(new_pred)
    db.commit()
    db.refresh(new_pred)
    return new_pred


@router.get("/group", response_model=list[GroupPredictionResponse])
def get_my_group_predictions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return db.query(GroupPrediction).options(
        joinedload(GroupPrediction.first_place_team),
        joinedload(GroupPrediction.second_place_team),
    ).filter(GroupPrediction.user_id == current_user.id).all()


# --- Bonus Predictions ---

@router.post("/bonus", response_model=BonusPredictionResponse, status_code=201)
def create_bonus_prediction(
    prediction: BonusPredictionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    check_admin_cannot_predict(current_user)
    check_bonus_predictions_locked(db)

    valid_types = ["champion", "runner_up", "top_scorer", "mvp"]
    if prediction.prediction_type not in valid_types:
        raise HTTPException(status_code=400, detail=f"Tipo de predicción inválido. Debe ser: {', '.join(valid_types)}")

    if prediction.prediction_type in ("champion", "runner_up") and not prediction.team_id:
        raise HTTPException(status_code=400, detail="Debes seleccionar un equipo")

    if prediction.prediction_type in ("top_scorer", "mvp") and not prediction.player_name:
        raise HTTPException(status_code=400, detail="Debes ingresar el nombre del jugador")

    existing = db.query(BonusPrediction).filter(
        BonusPrediction.user_id == current_user.id,
        BonusPrediction.prediction_type == prediction.prediction_type,
    ).first()

    if existing:
        existing.team_id = prediction.team_id
        existing.player_name = prediction.player_name
        db.commit()
        db.refresh(existing)
        return existing

    new_pred = BonusPrediction(
        user_id=current_user.id,
        prediction_type=prediction.prediction_type,
        team_id=prediction.team_id,
        player_name=prediction.player_name,
    )
    db.add(new_pred)
    db.commit()
    db.refresh(new_pred)
    return new_pred


@router.get("/bonus", response_model=list[BonusPredictionResponse])
def get_my_bonus_predictions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return db.query(BonusPrediction).options(
        joinedload(BonusPrediction.team)
    ).filter(BonusPrediction.user_id == current_user.id).all()
