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
    {"name": "Repechaje UEFA D", "code": "UD4", "group": "A", "flag": "🏳️"},
    # Group B
    {"name": "Canadá", "code": "CAN", "group": "B", "flag": "🇨🇦"},
    {"name": "Suiza", "code": "SUI", "group": "B", "flag": "🇨🇭"},
    {"name": "Qatar", "code": "QAT", "group": "B", "flag": "🇶🇦"},
    {"name": "Repechaje UEFA A", "code": "UA4", "group": "B", "flag": "🏳️"},
    # Group C
    {"name": "Brasil", "code": "BRA", "group": "C", "flag": "🇧🇷"},
    {"name": "Marruecos", "code": "MAR", "group": "C", "flag": "🇲🇦"},
    {"name": "Haití", "code": "HAI", "group": "C", "flag": "🇭🇹"},
    {"name": "Escocia", "code": "SCO", "group": "C", "flag": "🏴󠁧󠁢󠁳󠁣󠁴󠁿"},
    # Group D
    {"name": "Estados Unidos", "code": "USA", "group": "D", "flag": "🇺🇸"},
    {"name": "Paraguay", "code": "PAR", "group": "D", "flag": "🇵🇾"},
    {"name": "Australia", "code": "AUS", "group": "D", "flag": "🇦🇺"},
    {"name": "Repechaje UEFA C", "code": "UC4", "group": "D", "flag": "🏳️"},
    # Group E
    {"name": "Alemania", "code": "GER", "group": "E", "flag": "🇩🇪"},
    {"name": "Costa de Marfil", "code": "CIV", "group": "E", "flag": "🇨🇮"},
    {"name": "Ecuador", "code": "ECU", "group": "E", "flag": "🇪🇨"},
    {"name": "Curazao", "code": "CUW", "group": "E", "flag": "🇨🇼"},
    # Group F
    {"name": "Países Bajos", "code": "NED", "group": "F", "flag": "🇳🇱"},
    {"name": "Japón", "code": "JPN", "group": "F", "flag": "🇯🇵"},
    {"name": "Túnez", "code": "TUN", "group": "F", "flag": "🇹🇳"},
    {"name": "Repechaje UEFA B", "code": "UB4", "group": "F", "flag": "🏳️"},
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
    {"name": "Repechaje Intercon. 2", "code": "IC2", "group": "I", "flag": "🏳️"},
    # Group J
    {"name": "Argentina", "code": "ARG", "group": "J", "flag": "🇦🇷"},
    {"name": "Argelia", "code": "ALG", "group": "J", "flag": "🇩🇿"},
    {"name": "Austria", "code": "AUT", "group": "J", "flag": "🇦🇹"},
    {"name": "Jordania", "code": "JOR", "group": "J", "flag": "🇯🇴"},
    # Group K
    {"name": "Portugal", "code": "POR", "group": "K", "flag": "🇵🇹"},
    {"name": "Colombia", "code": "COL", "group": "K", "flag": "🇨🇴"},
    {"name": "Uzbekistán", "code": "UZB", "group": "K", "flag": "🇺🇿"},
    {"name": "Repechaje Intercon. 1", "code": "IC1", "group": "K", "flag": "🏳️"},
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


def seed_group_matches(db: Session):
    """Create group stage matches - 6 matches per group (round robin), 72 total."""
    if db.query(Match).count() > 0:
        return  # Already seeded

    match_number = 1
    base_date = datetime(2026, 6, 11, 18, 0, 0, tzinfo=timezone.utc)

    groups = sorted(set(t["group"] for t in TEAMS_DATA))

    for group in groups:
        group_teams = db.query(Team).filter(Team.group_name == group).all()
        if len(group_teams) != 4:
            continue

        # Round robin: 6 matches per group
        matchups = [
            (0, 1), (2, 3),  # Matchday 1
            (0, 2), (1, 3),  # Matchday 2
            (0, 3), (1, 2),  # Matchday 3
        ]

        for i, (h, a) in enumerate(matchups):
            matchday = (i // 2) + 1
            hour_offset = (i % 2) * 3  # 3 hours apart

            from datetime import timedelta
            match_date = base_date + timedelta(
                days=(ord(group) - ord('A')) + (matchday - 1) * 12,
                hours=hour_offset,
            )

            match = Match(
                match_number=match_number,
                phase=Phase.GROUP,
                group_name=group,
                home_team_id=group_teams[h].id,
                away_team_id=group_teams[a].id,
                match_date=match_date,
                venue=f"Estadio {group}{matchday}",
                matchday=matchday,
            )
            db.add(match)
            match_number += 1

    db.commit()


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

    # Pass 1: set all codes to temporary unique values to avoid UNIQUE conflicts
    for db_team, _ in updates:
        db_team.code = f"_TMP_{db_team.id}"
    db.flush()

    # Pass 2: apply the real values
    updated = 0
    for db_team, seed_t in updates:
        changed = False
        if db_team.name != seed_t["name"]:
            db_team.name = seed_t["name"]
            changed = True
        if db_team.code != seed_t["code"]:
            db_team.code = seed_t["code"]
            changed = True
        else:
            # Code was already correct but we changed it to _TMP, restore it
            db_team.code = seed_t["code"]
        if db_team.flag_emoji != seed_t["flag"]:
            db_team.flag_emoji = seed_t["flag"]
            changed = True
        if db_team.group_name != seed_t["group"]:
            db_team.group_name = seed_t["group"]
            changed = True
        if changed:
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
