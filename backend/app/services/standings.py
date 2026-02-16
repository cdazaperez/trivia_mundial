"""Group standings calculation service."""
from sqlalchemy.orm import Session

from app.models.tournament import Team, Match, Phase


def calculate_group_standings(db: Session, group_name: str) -> list[dict]:
    """Calculate standings for a single group.

    Returns list of dicts sorted by: points desc, goal_difference desc, goals_for desc.
    """
    teams = db.query(Team).filter(Team.group_name == group_name).all()
    matches = (
        db.query(Match)
        .filter(Match.phase == Phase.GROUP, Match.group_name == group_name, Match.is_finished == True)
        .all()
    )

    stats: dict[int, dict] = {}
    for team in teams:
        stats[team.id] = {
            "team_id": team.id,
            "team_name": team.name,
            "team_code": team.code,
            "team_flag": team.flag_emoji,
            "played": 0,
            "won": 0,
            "drawn": 0,
            "lost": 0,
            "goals_for": 0,
            "goals_against": 0,
            "goal_difference": 0,
            "points": 0,
            "position": 0,
        }

    for match in matches:
        if match.home_team_id not in stats or match.away_team_id not in stats:
            continue

        home = stats[match.home_team_id]
        away = stats[match.away_team_id]

        home["played"] += 1
        away["played"] += 1
        home["goals_for"] += match.home_score
        home["goals_against"] += match.away_score
        away["goals_for"] += match.away_score
        away["goals_against"] += match.home_score

        if match.home_score > match.away_score:
            home["won"] += 1
            home["points"] += 3
            away["lost"] += 1
        elif match.home_score < match.away_score:
            away["won"] += 1
            away["points"] += 3
            home["lost"] += 1
        else:
            home["drawn"] += 1
            away["drawn"] += 1
            home["points"] += 1
            away["points"] += 1

    for s in stats.values():
        s["goal_difference"] = s["goals_for"] - s["goals_against"]

    standings = sorted(
        stats.values(),
        key=lambda s: (s["points"], s["goal_difference"], s["goals_for"]),
        reverse=True,
    )

    for i, s in enumerate(standings):
        s["position"] = i + 1

    return standings


def get_all_group_standings(db: Session) -> dict[str, list[dict]]:
    """Calculate standings for all 12 groups."""
    groups = sorted(set(
        r[0] for r in db.query(Team.group_name).filter(Team.group_name.isnot(None)).distinct().all()
    ))
    return {group: calculate_group_standings(db, group) for group in groups}


def are_all_group_matches_finished(db: Session) -> bool:
    """Check if all group stage matches are finished."""
    total = db.query(Match).filter(Match.phase == Phase.GROUP).count()
    finished = db.query(Match).filter(Match.phase == Phase.GROUP, Match.is_finished == True).count()
    return total > 0 and total == finished


def get_best_third_place_teams(db: Session) -> list[dict]:
    """Rank all third-place teams and return the best 8."""
    all_standings = get_all_group_standings(db)

    third_place = []
    for group, standings in all_standings.items():
        if len(standings) >= 3:
            entry = standings[2]  # 0-indexed position 2 = 3rd place
            entry["group"] = group
            third_place.append(entry)

    # Sort by points desc, goal_difference desc, goals_for desc
    third_place.sort(
        key=lambda s: (s["points"], s["goal_difference"], s["goals_for"]),
        reverse=True,
    )

    # Mark top 8 as qualifying
    for i, entry in enumerate(third_place):
        entry["qualifies"] = i < 8

    return third_place
