"""Knockout stage bracket generation for FIFA World Cup 2026."""
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.models.tournament import Match, Phase, Team
from app.services.standings import (
    are_all_group_matches_finished,
    get_all_group_standings,
    get_best_third_place_teams,
)

# ============================================================
# FIFA 2026 Round of 32 bracket structure
# ============================================================

# Fixed R32 matchups: (match_number, home_position, away_position)
# Position format: "1A" = winner of group A, "2B" = runner-up of group B
# None for away means it's a third-place slot (resolved dynamically)
R32_MATCHES = [
    (73, "2A", "2B"),
    (74, "1E", None),   # vs 3rd from A/B/C/D/F
    (75, "1F", "2C"),
    (76, "1C", "2F"),
    (77, "1I", None),   # vs 3rd from C/D/F/G/H
    (78, "2E", "2I"),
    (79, "1A", None),   # vs 3rd from C/E/F/H/I
    (80, "1L", None),   # vs 3rd from E/H/I/J/K
    (81, "1D", None),   # vs 3rd from B/E/F/I/J
    (82, "1G", None),   # vs 3rd from A/E/H/I/J
    (83, "2K", "2L"),
    (84, "1H", "2J"),
    (85, "1B", None),   # vs 3rd from E/F/G/I/J
    (86, "1J", "2H"),
    (87, "1K", None),   # vs 3rd from D/E/I/J/L
    (88, "2D", "2G"),
]

# Third-place assignment: match_number -> list of eligible source groups
THIRD_PLACE_SLOTS = {
    74: ["A", "B", "C", "D", "F"],
    77: ["C", "D", "F", "G", "H"],
    79: ["C", "E", "F", "H", "I"],
    80: ["E", "H", "I", "J", "K"],
    81: ["B", "E", "F", "I", "J"],
    82: ["A", "E", "H", "I", "J"],
    85: ["E", "F", "G", "I", "J"],
    87: ["D", "E", "I", "J", "L"],
}

# Round of 16 matchups: (match_number, winner_of_match_A, winner_of_match_B)
R16_MATCHES = [
    (89, 74, 77),
    (90, 73, 75),
    (91, 76, 78),
    (92, 79, 80),
    (93, 81, 82),
    (94, 83, 84),
    (95, 86, 88),
    (96, 85, 87),
]

# Quarterfinal matchups
QF_MATCHES = [
    (97, 89, 90),
    (98, 93, 94),
    (99, 91, 92),
    (100, 95, 96),
]

# Semifinal matchups
SF_MATCHES = [
    (101, 97, 98),
    (102, 99, 100),
]

# Third place and final (third place uses losers)
THIRD_PLACE_MATCH = (103, 101, 102)  # losers of semis
FINAL_MATCH = (104, 101, 102)        # winners of semis

# Knockout dates (approximate)
KNOCKOUT_DATES = {
    Phase.ROUND_OF_32: datetime(2026, 6, 28, 18, 0, 0, tzinfo=timezone.utc),
    Phase.ROUND_OF_16: datetime(2026, 7, 4, 18, 0, 0, tzinfo=timezone.utc),
    Phase.QUARTER_FINAL: datetime(2026, 7, 9, 18, 0, 0, tzinfo=timezone.utc),
    Phase.SEMI_FINAL: datetime(2026, 7, 14, 20, 0, 0, tzinfo=timezone.utc),
    Phase.THIRD_PLACE: datetime(2026, 7, 18, 20, 0, 0, tzinfo=timezone.utc),
    Phase.FINAL: datetime(2026, 7, 19, 20, 0, 0, tzinfo=timezone.utc),
}

# Phase labels in Spanish
PHASE_LABELS = {
    Phase.ROUND_OF_32: "32avos de Final",
    Phase.ROUND_OF_16: "Octavos de Final",
    Phase.QUARTER_FINAL: "Cuartos de Final",
    Phase.SEMI_FINAL: "Semifinales",
    Phase.THIRD_PLACE: "Tercer Puesto",
    Phase.FINAL: "Final",
}

VENUE_MAP = {
    Phase.ROUND_OF_32: "Por definir",
    Phase.ROUND_OF_16: "Por definir",
    Phase.QUARTER_FINAL: "Por definir",
    Phase.SEMI_FINAL: "Por definir",
    Phase.THIRD_PLACE: "Hard Rock Stadium, Miami",
    Phase.FINAL: "MetLife Stadium, New Jersey",
}


def _assign_third_place_teams(qualifying_groups: list[str]) -> dict[int, str]:
    """Assign 8 qualifying third-place teams to R32 match slots using backtracking.

    Args:
        qualifying_groups: sorted list of 8 group letters whose 3rd-place teams qualified.

    Returns:
        dict mapping match_number -> group letter.
    """
    slots = sorted(THIRD_PLACE_SLOTS.keys())
    remaining = list(qualifying_groups)
    assignment: dict[int, str] = {}

    def backtrack(idx: int) -> bool:
        if idx == len(slots):
            return True
        match_num = slots[idx]
        eligible = THIRD_PLACE_SLOTS[match_num]
        for group in remaining[:]:
            if group in eligible:
                assignment[match_num] = group
                remaining.remove(group)
                if backtrack(idx + 1):
                    return True
                remaining.append(group)
                remaining.sort()
                del assignment[match_num]
        return False

    if not backtrack(0):
        raise ValueError("No valid third-place assignment found")
    return assignment


def _get_team_by_position(
    standings: dict[str, list[dict]], position: str
) -> int:
    """Get team_id from a position string like '1A', '2B'."""
    pos = int(position[0])  # 1 or 2
    group = position[1]
    group_standings = standings.get(group, [])
    if len(group_standings) < pos:
        raise ValueError(f"Group {group} doesn't have {pos} teams in standings")
    return group_standings[pos - 1]["team_id"]


def _get_match_winner(db: Session, match_number: int) -> int:
    """Get the winning team_id from a finished match."""
    match = db.query(Match).filter(Match.match_number == match_number).first()
    if not match or not match.is_finished:
        raise ValueError(f"Partido #{match_number} no está finalizado")
    if match.home_score > match.away_score:
        return match.home_team_id
    elif match.away_score > match.home_score:
        return match.away_team_id
    else:
        raise ValueError(
            f"Partido #{match_number} terminó empatado. "
            "Ingresa el resultado final después de penales."
        )


def _get_match_loser(db: Session, match_number: int) -> int:
    """Get the losing team_id from a finished match."""
    match = db.query(Match).filter(Match.match_number == match_number).first()
    if not match or not match.is_finished:
        raise ValueError(f"Partido #{match_number} no está finalizado")
    if match.home_score > match.away_score:
        return match.away_team_id
    elif match.away_score > match.home_score:
        return match.home_team_id
    else:
        raise ValueError(
            f"Partido #{match_number} terminó empatado. "
            "Ingresa el resultado final después de penales."
        )


def get_knockout_status(db: Session) -> dict:
    """Return status of each knockout phase for admin UI."""
    def phase_status(phase: Phase, expected_count: int) -> dict:
        total = db.query(Match).filter(Match.phase == phase).count()
        finished = db.query(Match).filter(Match.phase == phase, Match.is_finished == True).count()
        return {
            "exists": total > 0,
            "complete": total > 0 and total == finished,
            "total": total,
            "finished": finished,
            "expected": expected_count,
        }

    return {
        "group_phase_complete": are_all_group_matches_finished(db),
        "round_of_32": phase_status(Phase.ROUND_OF_32, 16),
        "round_of_16": phase_status(Phase.ROUND_OF_16, 8),
        "quarter_final": phase_status(Phase.QUARTER_FINAL, 4),
        "semi_final": phase_status(Phase.SEMI_FINAL, 2),
        "third_place": phase_status(Phase.THIRD_PLACE, 1),
        "final": phase_status(Phase.FINAL, 1),
    }


def generate_round_of_32(db: Session) -> list[Match]:
    """Generate 16 Round of 32 matches based on group results."""
    if not are_all_group_matches_finished(db):
        raise ValueError("No todos los partidos de grupo han finalizado")

    existing = db.query(Match).filter(Match.phase == Phase.ROUND_OF_32).count()
    if existing > 0:
        raise ValueError("Los 32avos de final ya fueron generados")

    standings = get_all_group_standings(db)
    third_place_ranking = get_best_third_place_teams(db)
    qualifying_groups = sorted([t["group"] for t in third_place_ranking if t["qualifies"]])

    if len(qualifying_groups) != 8:
        raise ValueError(f"Se esperaban 8 terceros clasificados, se encontraron {len(qualifying_groups)}")

    third_place_assignment = _assign_third_place_teams(qualifying_groups)

    # Build third-place team lookup: group -> team_id
    third_place_teams = {}
    for entry in third_place_ranking:
        if entry["qualifies"]:
            third_place_teams[entry["group"]] = entry["team_id"]

    base_date = KNOCKOUT_DATES[Phase.ROUND_OF_32]
    created = []

    for i, (match_num, home_pos, away_pos) in enumerate(R32_MATCHES):
        home_team_id = _get_team_by_position(standings, home_pos)

        if away_pos is not None:
            away_team_id = _get_team_by_position(standings, away_pos)
        else:
            # Third-place slot
            assigned_group = third_place_assignment[match_num]
            away_team_id = third_place_teams[assigned_group]

        match_date = base_date + timedelta(hours=i * 3)

        match = Match(
            match_number=match_num,
            phase=Phase.ROUND_OF_32,
            home_team_id=home_team_id,
            away_team_id=away_team_id,
            match_date=match_date,
            venue=VENUE_MAP[Phase.ROUND_OF_32],
        )
        db.add(match)
        created.append(match)

    db.commit()
    for m in created:
        db.refresh(m)
    return created


def _generate_from_previous(
    db: Session,
    phase: Phase,
    matchups: list[tuple[int, int, int]],
    use_losers: bool = False,
) -> list[Match]:
    """Generate matches from previous round results."""
    existing = db.query(Match).filter(Match.phase == phase).count()
    if existing > 0:
        raise ValueError(f"Los partidos de {PHASE_LABELS.get(phase, phase.value)} ya fueron generados")

    base_date = KNOCKOUT_DATES[phase]
    created = []
    getter = _get_match_loser if use_losers else _get_match_winner

    for i, (match_num, source_a, source_b) in enumerate(matchups):
        home_team_id = getter(db, source_a)
        away_team_id = getter(db, source_b)

        match = Match(
            match_number=match_num,
            phase=phase,
            home_team_id=home_team_id,
            away_team_id=away_team_id,
            match_date=base_date + timedelta(hours=i * 3),
            venue=VENUE_MAP[phase],
        )
        db.add(match)
        created.append(match)

    db.commit()
    for m in created:
        db.refresh(m)
    return created


def generate_round_of_16(db: Session) -> list[Match]:
    """Generate Round of 16 from Round of 32 results."""
    r32_status = db.query(Match).filter(
        Match.phase == Phase.ROUND_OF_32, Match.is_finished == False
    ).count()
    r32_total = db.query(Match).filter(Match.phase == Phase.ROUND_OF_32).count()
    if r32_total == 0 or r32_status > 0:
        raise ValueError("No todos los 32avos de final han finalizado")
    return _generate_from_previous(db, Phase.ROUND_OF_16, R16_MATCHES)


def generate_quarter_finals(db: Session) -> list[Match]:
    """Generate Quarterfinals from Round of 16 results."""
    unfinished = db.query(Match).filter(
        Match.phase == Phase.ROUND_OF_16, Match.is_finished == False
    ).count()
    total = db.query(Match).filter(Match.phase == Phase.ROUND_OF_16).count()
    if total == 0 or unfinished > 0:
        raise ValueError("No todos los octavos de final han finalizado")
    return _generate_from_previous(db, Phase.QUARTER_FINAL, QF_MATCHES)


def generate_semi_finals(db: Session) -> list[Match]:
    """Generate Semifinals from Quarterfinals results."""
    unfinished = db.query(Match).filter(
        Match.phase == Phase.QUARTER_FINAL, Match.is_finished == False
    ).count()
    total = db.query(Match).filter(Match.phase == Phase.QUARTER_FINAL).count()
    if total == 0 or unfinished > 0:
        raise ValueError("No todos los cuartos de final han finalizado")
    return _generate_from_previous(db, Phase.SEMI_FINAL, SF_MATCHES)


def generate_finals(db: Session) -> list[Match]:
    """Generate Third Place match and Final from Semifinal results."""
    unfinished = db.query(Match).filter(
        Match.phase == Phase.SEMI_FINAL, Match.is_finished == False
    ).count()
    total = db.query(Match).filter(Match.phase == Phase.SEMI_FINAL).count()
    if total == 0 or unfinished > 0:
        raise ValueError("No todas las semifinales han finalizado")

    created = []

    # Third place match (losers of semis)
    tp_num, tp_src_a, tp_src_b = THIRD_PLACE_MATCH
    existing_tp = db.query(Match).filter(Match.phase == Phase.THIRD_PLACE).count()
    if existing_tp == 0:
        tp_match = Match(
            match_number=tp_num,
            phase=Phase.THIRD_PLACE,
            home_team_id=_get_match_loser(db, tp_src_a),
            away_team_id=_get_match_loser(db, tp_src_b),
            match_date=KNOCKOUT_DATES[Phase.THIRD_PLACE],
            venue=VENUE_MAP[Phase.THIRD_PLACE],
        )
        db.add(tp_match)
        created.append(tp_match)

    # Final (winners of semis)
    f_num, f_src_a, f_src_b = FINAL_MATCH
    existing_f = db.query(Match).filter(Match.phase == Phase.FINAL).count()
    if existing_f == 0:
        final_match = Match(
            match_number=f_num,
            phase=Phase.FINAL,
            home_team_id=_get_match_winner(db, f_src_a),
            away_team_id=_get_match_winner(db, f_src_b),
            match_date=KNOCKOUT_DATES[Phase.FINAL],
            venue=VENUE_MAP[Phase.FINAL],
        )
        db.add(final_match)
        created.append(final_match)

    db.commit()
    for m in created:
        db.refresh(m)
    return created


# Dispatcher
PHASE_GENERATORS = {
    "round_of_32": generate_round_of_32,
    "round_of_16": generate_round_of_16,
    "quarter_final": generate_quarter_finals,
    "semi_final": generate_semi_finals,
    "finals": generate_finals,
}
