from sqlalchemy.orm import Session

from app.core.config import POINTS_EXACT_SCORE, POINTS_CORRECT_RESULT
from app.models.tournament import Match, MatchPrediction


def calculate_points_for_match(db: Session, match: Match):
    """Calculate and update points for all predictions on a finished match."""
    if not match.is_finished or match.home_score is None or match.away_score is None:
        return

    predictions = db.query(MatchPrediction).filter(
        MatchPrediction.match_id == match.id
    ).all()

    actual_home = match.home_score
    actual_away = match.away_score

    for pred in predictions:
        points = 0

        if pred.home_score == actual_home and pred.away_score == actual_away:
            # Exact score match
            points = POINTS_EXACT_SCORE
        elif _same_result(pred.home_score, pred.away_score, actual_home, actual_away):
            # Correct result (win/draw) but wrong score
            points = POINTS_CORRECT_RESULT

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
