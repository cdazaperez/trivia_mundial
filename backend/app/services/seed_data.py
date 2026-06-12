"""Seed World Cup 2026 data - Teams, Groups, and Group Stage Matches."""
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.models.tournament import Team, Match, Phase


# World Cup 2026 - 48 teams, 12 groups of 4
# Based on the official FIFA draw of December 5, 2025
TEAMS_DATA = [
    # Group A
    {"name": "México", "code": "MEX", "group": "A", "flag": "🇲🇽"},
    {"name": "Corea del Sur", "code": "KOR", "group": "A", "flag": "🇰🇷"},
    {"name": "Sudáfrica", "code": "RSA", "group": "A", "flag": "🇿🇦"},
    {"name": "Chequia", "code": "CZE", "group": "A", "flag": "🇨🇿"},
    # Group B
    {"name": "Canadá", "code": "CAN", "group": "B", "flag": "🇨🇦"},
    {"name": "Suiza", "code": "SUI", "group": "B", "flag": "🇨🇭"},
    {"name": "Qatar", "code": "QAT", "group": "B", "flag": "🇶🇦"},
    {"name": "Bosnia y Herzegovina", "code": "BIH", "group": "B", "flag": "🇧🇦"},
    # Group C
    {"name": "Brasil", "code": "BRA", "group": "C", "flag": "🇧🇷"},
    {"name": "Marruecos", "code": "MAR", "group": "C", "flag": "🇲🇦"},
    {"name": "Haití", "code": "HAI", "group": "C", "flag": "🇭🇹"},
    {"name": "Escocia", "code": "SCO", "group": "C", "flag": "🏴󠁧󠁢󠁳󠁣󠁴󠁿"},
    # Group D
    {"name": "Estados Unidos", "code": "USA", "group": "D", "flag": "🇺🇸"},
    {"name": "Paraguay", "code": "PAR", "group": "D", "flag": "🇵🇾"},
    {"name": "Australia", "code": "AUS", "group": "D", "flag": "🇦🇺"},
    {"name": "Turquía", "code": "TUR", "group": "D", "flag": "🇹🇷"},
    # Group E
    {"name": "Alemania", "code": "GER", "group": "E", "flag": "🇩🇪"},
    {"name": "Costa de Marfil", "code": "CIV", "group": "E", "flag": "🇨🇮"},
    {"name": "Ecuador", "code": "ECU", "group": "E", "flag": "🇪🇨"},
    {"name": "Curazao", "code": "CUW", "group": "E", "flag": "🇨🇼"},
    # Group F
    {"name": "Países Bajos", "code": "NED", "group": "F", "flag": "🇳🇱"},
    {"name": "Japón", "code": "JPN", "group": "F", "flag": "🇯🇵"},
    {"name": "Túnez", "code": "TUN", "group": "F", "flag": "🇹🇳"},
    {"name": "Suecia", "code": "SWE", "group": "F", "flag": "🇸🇪"},
    # Group G
    {"name": "Bélgica", "code": "BEL", "group": "G", "flag": "🇧🇪"},
    {"name": "Egipto", "code": "EGY", "group": "G", "flag": "🇪🇬"},
    {"name": "Irán", "code": "IRN", "group": "G", "flag": "🇮🇷"},
    {"name": "Nueva Zelanda", "code": "NZL", "group": "G", "flag": "🇳🇿"},
    # Group H
    {"name": "España", "code": "ESP", "group": "H", "flag": "🇪🇸"},
    {"name": "Uruguay", "code": "URU", "group": "H", "flag": "🇺🇾"},
    {"name": "Arabia Saudita", "code": "KSA", "group": "H", "flag": "🇸🇦"},
    {"name": "Cabo Verde", "code": "CPV", "group": "H", "flag": "🇨🇻"},
    # Group I
    {"name": "Francia", "code": "FRA", "group": "I", "flag": "🇫🇷"},
    {"name": "Senegal", "code": "SEN", "group": "I", "flag": "🇸🇳"},
    {"name": "Noruega", "code": "NOR", "group": "I", "flag": "🇳🇴"},
    {"name": "Irak", "code": "IRQ", "group": "I", "flag": "🇮🇶"},
    # Group J
    {"name": "Argentina", "code": "ARG", "group": "J", "flag": "🇦🇷"},
    {"name": "Argelia", "code": "ALG", "group": "J", "flag": "🇩🇿"},
    {"name": "Austria", "code": "AUT", "group": "J", "flag": "🇦🇹"},
    {"name": "Jordania", "code": "JOR", "group": "J", "flag": "🇯🇴"},
    # Group K
    {"name": "Portugal", "code": "POR", "group": "K", "flag": "🇵🇹"},
    {"name": "Colombia", "code": "COL", "group": "K", "flag": "🇨🇴"},
    {"name": "Uzbekistán", "code": "UZB", "group": "K", "flag": "🇺🇿"},
    {"name": "R.D. del Congo", "code": "COD", "group": "K", "flag": "🇨🇩"},
    # Group L
    {"name": "Inglaterra", "code": "ENG", "group": "L", "flag": "🏴󠁧󠁢󠁥󠁮󠁧󠁿"},
    {"name": "Croacia", "code": "CRO", "group": "L", "flag": "🇭🇷"},
    {"name": "Ghana", "code": "GHA", "group": "L", "flag": "🇬🇭"},
    {"name": "Panamá", "code": "PAN", "group": "L", "flag": "🇵🇦"},
]


def seed_teams(db: Session):
    """Create all 48 teams."""
    if db.query(Team).count() > 0:
        return  # Already seeded

    for t in TEAMS_DATA:
        team = Team(name=t["name"], code=t["code"], group_name=t["group"], flag_emoji=t["flag"])
        db.add(team)
    db.commit()


GROUP_MATCHES_DATA = [
    # Group A: MEX, KOR, CZE, RSA
    {"n": 1, "g": "A", "md": 1, "h": "MEX", "a": "RSA", "dt": "2026-06-11T19:00", "v": "Estadio Azteca, Ciudad de México"},
    {"n": 2, "g": "A", "md": 1, "h": "KOR", "a": "CZE", "dt": "2026-06-12T02:00", "v": "Estadio Akron, Guadalajara"},
    {"n": 3, "g": "A", "md": 2, "h": "CZE", "a": "RSA", "dt": "2026-06-18T16:00", "v": "Mercedes-Benz Stadium, Atlanta"},
    {"n": 4, "g": "A", "md": 2, "h": "MEX", "a": "KOR", "dt": "2026-06-19T01:00", "v": "Estadio Akron, Guadalajara"},
    {"n": 5, "g": "A", "md": 3, "h": "CZE", "a": "MEX", "dt": "2026-06-25T01:00", "v": "Estadio Azteca, Ciudad de México"},
    {"n": 6, "g": "A", "md": 3, "h": "RSA", "a": "KOR", "dt": "2026-06-25T01:00", "v": "Estadio BBVA, Monterrey"},
    # Group B: CAN, BIH, QAT, SUI
    {"n": 7, "g": "B", "md": 1, "h": "CAN", "a": "BIH", "dt": "2026-06-12T19:00", "v": "BMO Field, Toronto"},
    {"n": 8, "g": "B", "md": 1, "h": "QAT", "a": "SUI", "dt": "2026-06-13T19:00", "v": "Levi's Stadium, Santa Clara"},
    {"n": 9, "g": "B", "md": 2, "h": "SUI", "a": "BIH", "dt": "2026-06-18T19:00", "v": "SoFi Stadium, Inglewood"},
    {"n": 10, "g": "B", "md": 2, "h": "CAN", "a": "QAT", "dt": "2026-06-18T22:00", "v": "BC Place, Vancouver"},
    {"n": 11, "g": "B", "md": 3, "h": "SUI", "a": "CAN", "dt": "2026-06-24T19:00", "v": "BC Place, Vancouver"},
    {"n": 12, "g": "B", "md": 3, "h": "BIH", "a": "QAT", "dt": "2026-06-24T19:00", "v": "Lumen Field, Seattle"},
    # Group C: BRA, MAR, HAI, SCO
    {"n": 13, "g": "C", "md": 1, "h": "BRA", "a": "MAR", "dt": "2026-06-13T22:00", "v": "MetLife Stadium, East Rutherford"},
    {"n": 14, "g": "C", "md": 1, "h": "HAI", "a": "SCO", "dt": "2026-06-14T01:00", "v": "Gillette Stadium, Foxborough"},
    {"n": 15, "g": "C", "md": 2, "h": "SCO", "a": "MAR", "dt": "2026-06-19T22:00", "v": "Gillette Stadium, Foxborough"},
    {"n": 16, "g": "C", "md": 2, "h": "BRA", "a": "HAI", "dt": "2026-06-20T00:30", "v": "Lincoln Financial Field, Filadelfia"},
    {"n": 17, "g": "C", "md": 3, "h": "SCO", "a": "BRA", "dt": "2026-06-24T22:00", "v": "Hard Rock Stadium, Miami"},
    {"n": 18, "g": "C", "md": 3, "h": "MAR", "a": "HAI", "dt": "2026-06-24T22:00", "v": "Mercedes-Benz Stadium, Atlanta"},
    # Group D: USA, PAR, AUS, TUR
    {"n": 19, "g": "D", "md": 1, "h": "USA", "a": "PAR", "dt": "2026-06-13T01:00", "v": "SoFi Stadium, Inglewood"},
    {"n": 20, "g": "D", "md": 1, "h": "AUS", "a": "TUR", "dt": "2026-06-14T04:00", "v": "BC Place, Vancouver"},
    {"n": 21, "g": "D", "md": 2, "h": "USA", "a": "AUS", "dt": "2026-06-19T19:00", "v": "Lumen Field, Seattle"},
    {"n": 22, "g": "D", "md": 2, "h": "TUR", "a": "PAR", "dt": "2026-06-20T03:00", "v": "Levi's Stadium, Santa Clara"},
    {"n": 23, "g": "D", "md": 3, "h": "TUR", "a": "USA", "dt": "2026-06-26T02:00", "v": "SoFi Stadium, Inglewood"},
    {"n": 24, "g": "D", "md": 3, "h": "PAR", "a": "AUS", "dt": "2026-06-26T02:00", "v": "Levi's Stadium, Santa Clara"},
    # Group E: GER, CUW, CIV, ECU
    {"n": 25, "g": "E", "md": 1, "h": "GER", "a": "CUW", "dt": "2026-06-14T17:00", "v": "NRG Stadium, Houston"},
    {"n": 26, "g": "E", "md": 1, "h": "CIV", "a": "ECU", "dt": "2026-06-14T23:00", "v": "Lincoln Financial Field, Filadelfia"},
    {"n": 27, "g": "E", "md": 2, "h": "GER", "a": "CIV", "dt": "2026-06-20T20:00", "v": "BMO Field, Toronto"},
    {"n": 28, "g": "E", "md": 2, "h": "ECU", "a": "CUW", "dt": "2026-06-21T00:00", "v": "Arrowhead Stadium, Kansas City"},
    {"n": 29, "g": "E", "md": 3, "h": "CUW", "a": "CIV", "dt": "2026-06-25T20:00", "v": "Lincoln Financial Field, Filadelfia"},
    {"n": 30, "g": "E", "md": 3, "h": "ECU", "a": "GER", "dt": "2026-06-25T20:00", "v": "MetLife Stadium, East Rutherford"},
    # Group F: NED, JPN, SWE, TUN
    {"n": 31, "g": "F", "md": 1, "h": "NED", "a": "JPN", "dt": "2026-06-14T20:00", "v": "AT&T Stadium, Arlington"},
    {"n": 32, "g": "F", "md": 1, "h": "SWE", "a": "TUN", "dt": "2026-06-15T02:00", "v": "Estadio BBVA, Monterrey"},
    {"n": 33, "g": "F", "md": 2, "h": "NED", "a": "SWE", "dt": "2026-06-20T17:00", "v": "NRG Stadium, Houston"},
    {"n": 34, "g": "F", "md": 2, "h": "TUN", "a": "JPN", "dt": "2026-06-21T04:00", "v": "Estadio BBVA, Monterrey"},
    {"n": 35, "g": "F", "md": 3, "h": "JPN", "a": "SWE", "dt": "2026-06-25T23:00", "v": "AT&T Stadium, Arlington"},
    {"n": 36, "g": "F", "md": 3, "h": "TUN", "a": "NED", "dt": "2026-06-25T23:00", "v": "Arrowhead Stadium, Kansas City"},
    # Group G: BEL, EGY, IRN, NZL
    {"n": 37, "g": "G", "md": 1, "h": "BEL", "a": "EGY", "dt": "2026-06-15T19:00", "v": "Lumen Field, Seattle"},
    {"n": 38, "g": "G", "md": 1, "h": "IRN", "a": "NZL", "dt": "2026-06-16T01:00", "v": "SoFi Stadium, Inglewood"},
    {"n": 39, "g": "G", "md": 2, "h": "BEL", "a": "IRN", "dt": "2026-06-21T19:00", "v": "SoFi Stadium, Inglewood"},
    {"n": 40, "g": "G", "md": 2, "h": "NZL", "a": "EGY", "dt": "2026-06-22T01:00", "v": "BC Place, Vancouver"},
    {"n": 41, "g": "G", "md": 3, "h": "EGY", "a": "IRN", "dt": "2026-06-27T03:00", "v": "Lumen Field, Seattle"},
    {"n": 42, "g": "G", "md": 3, "h": "NZL", "a": "BEL", "dt": "2026-06-27T03:00", "v": "BC Place, Vancouver"},
    # Group H: ESP, CPV, KSA, URU
    {"n": 43, "g": "H", "md": 1, "h": "ESP", "a": "CPV", "dt": "2026-06-15T16:00", "v": "Mercedes-Benz Stadium, Atlanta"},
    {"n": 44, "g": "H", "md": 1, "h": "KSA", "a": "URU", "dt": "2026-06-15T22:00", "v": "Hard Rock Stadium, Miami"},
    {"n": 45, "g": "H", "md": 2, "h": "ESP", "a": "KSA", "dt": "2026-06-21T16:00", "v": "Mercedes-Benz Stadium, Atlanta"},
    {"n": 46, "g": "H", "md": 2, "h": "URU", "a": "CPV", "dt": "2026-06-21T22:00", "v": "Hard Rock Stadium, Miami"},
    {"n": 47, "g": "H", "md": 3, "h": "CPV", "a": "KSA", "dt": "2026-06-27T00:00", "v": "NRG Stadium, Houston"},
    {"n": 48, "g": "H", "md": 3, "h": "URU", "a": "ESP", "dt": "2026-06-27T00:00", "v": "Estadio Akron, Guadalajara"},
    # Group I: FRA, SEN, IRQ, NOR
    {"n": 49, "g": "I", "md": 1, "h": "FRA", "a": "SEN", "dt": "2026-06-16T19:00", "v": "MetLife Stadium, East Rutherford"},
    {"n": 50, "g": "I", "md": 1, "h": "IRQ", "a": "NOR", "dt": "2026-06-16T22:00", "v": "Gillette Stadium, Foxborough"},
    {"n": 51, "g": "I", "md": 2, "h": "FRA", "a": "IRQ", "dt": "2026-06-22T21:00", "v": "Lincoln Financial Field, Filadelfia"},
    {"n": 52, "g": "I", "md": 2, "h": "NOR", "a": "SEN", "dt": "2026-06-23T00:00", "v": "MetLife Stadium, East Rutherford"},
    {"n": 53, "g": "I", "md": 3, "h": "NOR", "a": "FRA", "dt": "2026-06-26T19:00", "v": "Gillette Stadium, Foxborough"},
    {"n": 54, "g": "I", "md": 3, "h": "SEN", "a": "IRQ", "dt": "2026-06-26T19:00", "v": "BMO Field, Toronto"},
    # Group J: ARG, ALG, AUT, JOR
    {"n": 55, "g": "J", "md": 1, "h": "ARG", "a": "ALG", "dt": "2026-06-17T01:00", "v": "Arrowhead Stadium, Kansas City"},
    {"n": 56, "g": "J", "md": 1, "h": "AUT", "a": "JOR", "dt": "2026-06-17T04:00", "v": "Levi's Stadium, Santa Clara"},
    {"n": 57, "g": "J", "md": 2, "h": "ARG", "a": "AUT", "dt": "2026-06-22T17:00", "v": "AT&T Stadium, Arlington"},
    {"n": 58, "g": "J", "md": 2, "h": "JOR", "a": "ALG", "dt": "2026-06-23T02:00", "v": "Levi's Stadium, Santa Clara"},
    {"n": 59, "g": "J", "md": 3, "h": "JOR", "a": "ARG", "dt": "2026-06-28T02:00", "v": "AT&T Stadium, Arlington"},
    {"n": 60, "g": "J", "md": 3, "h": "ALG", "a": "AUT", "dt": "2026-06-28T02:00", "v": "Arrowhead Stadium, Kansas City"},
    # Group K: POR, COD, UZB, COL
    {"n": 61, "g": "K", "md": 1, "h": "POR", "a": "COD", "dt": "2026-06-17T17:00", "v": "NRG Stadium, Houston"},
    {"n": 62, "g": "K", "md": 1, "h": "UZB", "a": "COL", "dt": "2026-06-18T02:00", "v": "Estadio Azteca, Ciudad de México"},
    {"n": 63, "g": "K", "md": 2, "h": "POR", "a": "UZB", "dt": "2026-06-23T17:00", "v": "NRG Stadium, Houston"},
    {"n": 64, "g": "K", "md": 2, "h": "COL", "a": "COD", "dt": "2026-06-24T02:00", "v": "Estadio Akron, Guadalajara"},
    {"n": 65, "g": "K", "md": 3, "h": "COL", "a": "POR", "dt": "2026-06-27T23:30", "v": "Hard Rock Stadium, Miami"},
    {"n": 66, "g": "K", "md": 3, "h": "COD", "a": "UZB", "dt": "2026-06-27T23:30", "v": "Mercedes-Benz Stadium, Atlanta"},
    # Group L: ENG, CRO, GHA, PAN
    {"n": 67, "g": "L", "md": 1, "h": "ENG", "a": "CRO", "dt": "2026-06-17T20:00", "v": "AT&T Stadium, Arlington"},
    {"n": 68, "g": "L", "md": 1, "h": "GHA", "a": "PAN", "dt": "2026-06-17T23:00", "v": "BMO Field, Toronto"},
    {"n": 69, "g": "L", "md": 2, "h": "ENG", "a": "GHA", "dt": "2026-06-23T20:00", "v": "Gillette Stadium, Foxborough"},
    {"n": 70, "g": "L", "md": 2, "h": "PAN", "a": "CRO", "dt": "2026-06-23T23:00", "v": "BMO Field, Toronto"},
    {"n": 71, "g": "L", "md": 3, "h": "PAN", "a": "ENG", "dt": "2026-06-27T21:00", "v": "MetLife Stadium, East Rutherford"},
    {"n": 72, "g": "L", "md": 3, "h": "CRO", "a": "GHA", "dt": "2026-06-27T21:00", "v": "Lincoln Financial Field, Filadelfia"},
]


def seed_group_matches(db: Session):
    """Create group stage matches - 6 matches per group (round robin), 72 total."""
    if db.query(Match).count() > 0:
        return  # Already seeded

    team_by_code = {t.code: t for t in db.query(Team).all()}

    for m in GROUP_MATCHES_DATA:
        home = team_by_code.get(m["h"])
        away = team_by_code.get(m["a"])
        if not home or not away:
            continue

        match_date = datetime.fromisoformat(m["dt"]).replace(tzinfo=timezone.utc)

        match = Match(
            match_number=m["n"],
            phase=Phase.GROUP,
            group_name=m["g"],
            home_team_id=home.id,
            away_team_id=away.id,
            match_date=match_date,
            venue=m["v"],
            matchday=m["md"],
        )
        db.add(match)

    db.commit()


def force_update_matches(db: Session):
    """Update match dates, venues, and matchups in-place without deleting predictions."""
    team_by_code = {t.code: t for t in db.query(Team).all()}
    updated = 0

    for m in GROUP_MATCHES_DATA:
        home = team_by_code.get(m["h"])
        away = team_by_code.get(m["a"])
        if not home or not away:
            continue

        match_date = datetime.fromisoformat(m["dt"]).replace(tzinfo=timezone.utc)

        db_match = db.query(Match).filter(Match.match_number == m["n"]).first()
        if db_match:
            db_match.home_team_id = home.id
            db_match.away_team_id = away.id
            db_match.match_date = match_date
            db_match.venue = m["v"]
            db_match.matchday = m["md"]
            db_match.group_name = m["g"]
            updated += 1

    db.commit()
    return updated


def force_update_teams(db: Session):
    """Update team names, codes, and flags in-place without deleting predictions.

    Matches teams by group and position (order within group) so that
    existing team IDs and all associated predictions are preserved.
    Uses a two-pass approach to avoid UNIQUE constraint conflicts on code.
    """
    from collections import defaultdict

    # Group seed data by group letter, preserving order
    seed_by_group: dict[str, list[dict]] = defaultdict(list)
    for t in TEAMS_DATA:
        seed_by_group[t["group"]].append(t)

    # Build mapping: db_team -> new seed data
    updates: list[tuple[Team, dict]] = []
    new_teams: list[dict] = []

    for group_letter in sorted(seed_by_group.keys()):
        seed_teams_list = seed_by_group[group_letter]
        db_teams = (
            db.query(Team)
            .filter(Team.group_name == group_letter)
            .order_by(Team.id)
            .all()
        )

        for i, seed_t in enumerate(seed_teams_list):
            if i < len(db_teams):
                updates.append((db_teams[i], seed_t))
            else:
                new_teams.append(seed_t)

    # Pass 1: set all names and codes to temporary unique values to avoid UNIQUE conflicts
    for db_team, _ in updates:
        db_team.name = f"_TMP_NAME_{db_team.id}"
        db_team.code = f"_TMP_{db_team.id}"
    db.flush()

    # Pass 2: apply the real values
    updated = 0
    for db_team, seed_t in updates:
        db_team.name = seed_t["name"]
        db_team.code = seed_t["code"]
        db_team.flag_emoji = seed_t["flag"]
        db_team.group_name = seed_t["group"]
        updated += 1

    for seed_t in new_teams:
        db.add(Team(
            name=seed_t["name"],
            code=seed_t["code"],
            group_name=seed_t["group"],
            flag_emoji=seed_t["flag"],
        ))
        updated += 1

    db.commit()
    return updated


def reseed_all(db: Session):
    """Delete all data and re-seed from scratch. Only works if no predictions exist."""
    from app.models.tournament import MatchPrediction, GroupPrediction, BonusPrediction

    pred_count = (
        db.query(MatchPrediction).count()
        + db.query(GroupPrediction).count()
        + db.query(BonusPrediction).count()
    )
    if pred_count > 0:
        raise ValueError("No se puede re-seedear: ya existen pronósticos de participantes.")

    db.query(Match).delete()
    db.query(Team).delete()
    db.commit()

    seed_teams(db)
    seed_group_matches(db)


def seed_admin(db: Session):
    """Create admin user from environment variables if it doesn't exist."""
    import os
    from app.models.user import User
    from app.core.security import get_password_hash

    admin_user = os.getenv("ADMIN_USERNAME")
    admin_pass = os.getenv("ADMIN_PASSWORD")
    admin_email = os.getenv("ADMIN_EMAIL", "admin@triviamundial.com")
    admin_name = os.getenv("ADMIN_FULLNAME", "Administrador")

    if not admin_user or not admin_pass:
        return

    existing = db.query(User).filter(User.username == admin_user).first()
    if existing:
        if not existing.is_admin:
            existing.is_admin = True
            db.commit()
        return

    admin = User(
        username=admin_user,
        email=admin_email,
        hashed_password=get_password_hash(admin_pass),
        full_name=admin_name,
        is_admin=True,
    )
    db.add(admin)
    db.commit()


def seed_all(db: Session):
    """Seed all initial data."""
    seed_teams(db)
    seed_group_matches(db)
    seed_admin(db)
