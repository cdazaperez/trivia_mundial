"""Knockout stage bracket generation for FIFA World Cup 2026."""
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.tournament import Match, Phase, Team
from app.services.annex_c import FIFA_ANNEX_C
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
    (93, 83, 84),
    (94, 81, 82),
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

# ============================================================
# Official match schedule: date (UTC) and venue per match
# ============================================================

def _utc(y, mo, d, h, m=0):
    return datetime(y, mo, d, h, m, tzinfo=timezone.utc)


MATCH_SCHEDULE = {
    # Round of 32 (June 28 – July 3)
    73: (_utc(2026, 6, 28, 19, 0), "SoFi Stadium, Inglewood"),
    76: (_utc(2026, 6, 29, 17, 0), "NRG Stadium, Houston"),
    74: (_utc(2026, 6, 29, 20, 30), "Gillette Stadium, Foxborough"),
    75: (_utc(2026, 6, 30, 1, 0), "Estadio BBVA, Monterrey"),
    78: (_utc(2026, 6, 30, 17, 0), "AT&T Stadium, Arlington"),
    77: (_utc(2026, 6, 30, 21, 0), "MetLife Stadium, East Rutherford"),
    79: (_utc(2026, 7, 1, 1, 0), "Estadio Azteca, Ciudad de México"),
    80: (_utc(2026, 7, 1, 16, 0), "Mercedes-Benz Stadium, Atlanta"),
    82: (_utc(2026, 7, 1, 20, 0), "Lumen Field, Seattle"),
    81: (_utc(2026, 7, 2, 0, 0), "Levi's Stadium, Santa Clara"),
    84: (_utc(2026, 7, 2, 19, 0), "SoFi Stadium, Inglewood"),
    83: (_utc(2026, 7, 2, 23, 0), "BMO Field, Toronto"),
    85: (_utc(2026, 7, 3, 3, 0), "BC Place, Vancouver"),
    88: (_utc(2026, 7, 3, 18, 0), "AT&T Stadium, Arlington"),
    86: (_utc(2026, 7, 3, 22, 0), "Hard Rock Stadium, Miami Gardens"),
    87: (_utc(2026, 7, 4, 1, 30), "Arrowhead Stadium, Kansas City"),
    # Round of 16 (July 4 – 7)
    90: (_utc(2026, 7, 4, 17, 0), "NRG Stadium, Houston"),
    89: (_utc(2026, 7, 4, 21, 0), "Lincoln Financial Field, Philadelphia"),
    91: (_utc(2026, 7, 5, 20, 0), "MetLife Stadium, East Rutherford"),
    92: (_utc(2026, 7, 6, 0, 0), "Estadio Azteca, Ciudad de México"),
    93: (_utc(2026, 7, 6, 19, 0), "AT&T Stadium, Arlington"),
    94: (_utc(2026, 7, 7, 0, 0), "Lumen Field, Seattle"),
    95: (_utc(2026, 7, 7, 16, 0), "Mercedes-Benz Stadium, Atlanta"),
    96: (_utc(2026, 7, 7, 20, 0), "BC Place, Vancouver"),
    # Quarterfinals (July 9 – 11)
    97: (_utc(2026, 7, 9, 20, 0), "Gillette Stadium, Foxborough"),
    98: (_utc(2026, 7, 10, 22, 0), "SoFi Stadium, Inglewood"),
    99: (_utc(2026, 7, 11, 21, 0), "Hard Rock Stadium, Miami Gardens"),
    100: (_utc(2026, 7, 12, 1, 0), "Arrowhead Stadium, Kansas City"),
    # Semifinals (July 14 – 15)
    101: (_utc(2026, 7, 14, 19, 0), "AT&T Stadium, Arlington"),
    102: (_utc(2026, 7, 15, 19, 0), "Mercedes-Benz Stadium, Atlanta"),
    # Third place (July 18)
    103: (_utc(2026, 7, 18, 21, 0), "Hard Rock Stadium, Miami Gardens"),
    # Final (July 19)
    104: (_utc(2026, 7, 19, 19, 0), "MetLife Stadium, East Rutherford"),
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


def _assign_third_place_teams(qualifying_groups: list[str]) -> dict[int, str]:
    """Assign 8 qualifying third-place teams to R32 match slots using FIFA Annex C.

    Args:
        qualifying_groups: sorted list of 8 group letters whose 3rd-place teams qualified.

    Returns:
        dict mapping match_number -> group letter.
    """
    key = "".join(sorted(qualifying_groups))
    if key not in FIFA_ANNEX_C:
        raise ValueError(
            f"Combinación de terceros {key} no encontrada en la tabla FIFA Anexo C"
        )
    return dict(FIFA_ANNEX_C[key])


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
    elif match.home_penalties is not None and match.away_penalties is not None:
        if match.home_penalties > match.away_penalties:
            return match.home_team_id
        elif match.away_penalties > match.home_penalties:
            return match.away_team_id
        raise ValueError(
            f"Partido #{match_number}: los penales no pueden terminar empatados."
        )
    else:
        raise ValueError(
            f"Partido #{match_number} terminó empatado. "
            "Ingresa el resultado de penales."
        )


def _get_match_loser(db: Session, match_number: int) -> int:
    """Get the losing team_id from a finished match."""
    winner = _get_match_winner(db, match_number)
    match = db.query(Match).filter(Match.match_number == match_number).first()
    if winner == match.home_team_id:
        return match.away_team_id
    return match.home_team_id


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

    group_total = db.query(Match).filter(Match.phase == Phase.GROUP).count()
    group_finished = db.query(Match).filter(
        Match.phase == Phase.GROUP, Match.is_finished == True
    ).count()

    unfinished_matches = []
    if group_total != group_finished:
        from sqlalchemy.orm import joinedload
        unfinished = (
            db.query(Match)
            .options(joinedload(Match.home_team), joinedload(Match.away_team))
            .filter(Match.phase == Phase.GROUP, Match.is_finished != True)
            .order_by(Match.match_number)
            .all()
        )
        unfinished_matches = [
            {
                "match_number": m.match_number,
                "group": m.group_name,
                "home": m.home_team.name if m.home_team else "?",
                "away": m.away_team.name if m.away_team else "?",
            }
            for m in unfinished
        ]

    return {
        "group_phase_complete": group_total > 0 and group_total == group_finished,
        "group_total": group_total,
        "group_finished": group_finished,
        "unfinished_matches": unfinished_matches,
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

    created = []

    for match_num, home_pos, away_pos in R32_MATCHES:
        home_team_id = _get_team_by_position(standings, home_pos)

        if away_pos is not None:
            away_team_id = _get_team_by_position(standings, away_pos)
        else:
            assigned_group = third_place_assignment[match_num]
            away_team_id = third_place_teams[assigned_group]

        match_date, venue = MATCH_SCHEDULE[match_num]

        match = Match(
            match_number=match_num,
            phase=Phase.ROUND_OF_32,
            home_team_id=home_team_id,
            away_team_id=away_team_id,
            match_date=match_date,
            venue=venue,
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

    created = []
    getter = _get_match_loser if use_losers else _get_match_winner

    for match_num, source_a, source_b in matchups:
        home_team_id = getter(db, source_a)
        away_team_id = getter(db, source_b)

        match_date, venue = MATCH_SCHEDULE[match_num]

        match = Match(
            match_number=match_num,
            phase=phase,
            home_team_id=home_team_id,
            away_team_id=away_team_id,
            match_date=match_date,
            venue=venue,
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
        tp_date, tp_venue = MATCH_SCHEDULE[tp_num]
        tp_match = Match(
            match_number=tp_num,
            phase=Phase.THIRD_PLACE,
            home_team_id=_get_match_loser(db, tp_src_a),
            away_team_id=_get_match_loser(db, tp_src_b),
            match_date=tp_date,
            venue=tp_venue,
        )
        db.add(tp_match)
        created.append(tp_match)

    # Final (winners of semis)
    f_num, f_src_a, f_src_b = FINAL_MATCH
    existing_f = db.query(Match).filter(Match.phase == Phase.FINAL).count()
    if existing_f == 0:
        f_date, f_venue = MATCH_SCHEDULE[f_num]
        final_match = Match(
            match_number=f_num,
            phase=Phase.FINAL,
            home_team_id=_get_match_winner(db, f_src_a),
            away_team_id=_get_match_winner(db, f_src_b),
            match_date=f_date,
            venue=f_venue,
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
