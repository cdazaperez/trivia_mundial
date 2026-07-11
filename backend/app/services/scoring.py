import unicodedata

from sqlalchemy.orm import Session

from app.core.config import (
    POINTS_EXACT_SCORE,
    POINTS_CORRECT_RESULT,
    POINTS_PENALTY_WINNER,
    POINTS_GROUP_QUALIFIER,
    POINTS_GROUP_FIRST,
    POINTS_CHAMPION,
    POINTS_RUNNER_UP,
    POINTS_TOP_SCORER,
    POINTS_MVP,
)
from app.models.tournament import Match, MatchPrediction, GroupPrediction, BonusPrediction, Phase, Team


def calculate_points_for_match(db: Session, match: Match):
    """Calculate and update points for all predictions on a finished match."""
    if not match.is_finished or match.home_score is None or match.away_score is None:
        return

    predictions = db.query(MatchPrediction).filter(
        MatchPrediction.match_id == match.id
    ).all()

    actual_home = match.home_score
    actual_away = match.away_score
    is_knockout = match.phase != Phase.GROUP
    actual_went_to_penalties = (
        is_knockout
        and actual_home == actual_away
        and match.home_penalties is not None
        and match.away_penalties is not None
    )

    for pred in predictions:
        points = 0

        if pred.home_score == actual_home and pred.away_score == actual_away:
            points = POINTS_EXACT_SCORE
        elif _same_result(pred.home_score, pred.away_score, actual_home, actual_away):
            points = POINTS_CORRECT_RESULT

        if actual_went_to_penalties and pred.home_penalties is not None and pred.away_penalties is not None:
            pred_pen_winner = "home" if pred.home_penalties > pred.away_penalties else "away"
            actual_pen_winner = "home" if match.home_penalties > match.away_penalties else "away"
            if pred_pen_winner == actual_pen_winner:
                points += POINTS_PENALTY_WINNER

        pred.points_earned = points

    db.commit()


def _same_result(pred_home: int, pred_away: int, actual_home: int, actual_away: int) -> bool:
    """Check if prediction has the same result type (home win, draw, away win)."""
    pred_result = _get_result(pred_home, pred_away)
    actual_result = _get_result(actual_home, actual_away)
    return pred_result == actual_result


def _get_result(home: int, away: int) -> str:
    if home > away:
        return "home"
    elif home < away:
        return "away"
    return "draw"


def calculate_group_prediction_points(db: Session, group_name: str):
    """Calculate points for group predictions once all group matches are finished."""
    from app.services.standings import calculate_group_standings

    group_matches = db.query(Match).filter(
        Match.phase == Phase.GROUP,
        Match.group_name == group_name,
    ).all()

    if not group_matches or not all(m.is_finished for m in group_matches):
        return 0

    standings = calculate_group_standings(db, group_name)
    if len(standings) < 2:
        return 0

    actual_first_id = standings[0]["team_id"]
    actual_second_id = standings[1]["team_id"]
    qualifiers = {actual_first_id, actual_second_id}

    predictions = db.query(GroupPrediction).filter(
        GroupPrediction.group_name == group_name
    ).all()

    updated = 0
    for pred in predictions:
        points = 0
        if pred.first_place_team_id == actual_first_id:
            points += POINTS_GROUP_FIRST
        elif pred.first_place_team_id in qualifiers:
            points += POINTS_GROUP_QUALIFIER

        if pred.second_place_team_id == actual_second_id:
            points += POINTS_GROUP_FIRST
        elif pred.second_place_team_id in qualifiers:
            points += POINTS_GROUP_QUALIFIER

        pred.points_earned = points
        if points > 0:
            updated += 1

    db.commit()
    return updated


def _normalize_name(name: str) -> str:
    """Normalize a player name for fuzzy comparison: strip, lowercase, remove accents/diacritics, normalize punctuation."""
    name = name.strip().lower()
    name = unicodedata.normalize("NFD", name)
    name = "".join(c for c in name if unicodedata.category(c) != "Mn")
    name = name.replace("-", " ").replace(".", " ").replace("'", "")
    name = " ".join(name.split())
    return name


def _names_match(prediction_name: str, actual_name: str) -> bool:
    """Check if a predicted player name matches the actual name using flexible matching."""
    norm_pred = _normalize_name(prediction_name)
    norm_actual = _normalize_name(actual_name)

    if norm_pred == norm_actual:
        return True

    if norm_pred in norm_actual or norm_actual in norm_pred:
        return True

    pred_parts = set(norm_pred.split())
    actual_parts = set(norm_actual.split())
    if pred_parts and actual_parts and pred_parts.issubset(actual_parts):
        return True
    if pred_parts and actual_parts and actual_parts.issubset(pred_parts):
        return True

    return False


def calculate_bonus_prediction_points(db: Session, prediction_type: str, team_id: int | None = None, player_name: str | None = None):
    """Calculate points for a specific bonus prediction type. Admin sets the actual result."""
    points_map = {
        "champion": POINTS_CHAMPION,
        "runner_up": POINTS_RUNNER_UP,
        "top_scorer": POINTS_TOP_SCORER,
        "mvp": POINTS_MVP,
    }

    max_points = points_map.get(prediction_type, 0)
    if max_points == 0:
        return 0

    predictions = db.query(BonusPrediction).filter(
        BonusPrediction.prediction_type == prediction_type
    ).all()

    updated = 0
    for pred in predictions:
        points = 0
        if prediction_type in ("champion", "runner_up"):
            if team_id and pred.team_id == team_id:
                points = max_points
        else:
            if player_name and pred.player_name and _names_match(pred.player_name, player_name):
                points = max_points
        pred.points_earned = points
        if points > 0:
            updated += 1

    db.commit()
    return updated
