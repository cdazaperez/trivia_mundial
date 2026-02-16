"""Seed World Cup 2026 data - Teams, Groups, and Group Stage Matches."""
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.models.tournament import Team, Match, Phase


# World Cup 2026 - 48 teams, 12 groups of 4
TEAMS_DATA = [
    # Group A
    {"name": "Estados Unidos", "code": "USA", "group": "A", "flag": "🇺🇸"},
    {"name": "Por definir A2", "code": "A2", "group": "A", "flag": "🏳️"},
    {"name": "Por definir A3", "code": "A3", "group": "A", "flag": "🏳️"},
    {"name": "Por definir A4", "code": "A4", "group": "A", "flag": "🏳️"},
    # Group B
    {"name": "México", "code": "MEX", "group": "B", "flag": "🇲🇽"},
    {"name": "Por definir B2", "code": "B2", "group": "B", "flag": "🏳️"},
    {"name": "Por definir B3", "code": "B3", "group": "B", "flag": "🏳️"},
    {"name": "Por definir B4", "code": "B4", "group": "B", "flag": "🏳️"},
    # Group C
    {"name": "Canadá", "code": "CAN", "group": "C", "flag": "🇨🇦"},
    {"name": "Por definir C2", "code": "C2", "group": "C", "flag": "🏳️"},
    {"name": "Por definir C3", "code": "C3", "group": "C", "flag": "🏳️"},
    {"name": "Por definir C4", "code": "C4", "group": "C", "flag": "🏳️"},
    # Group D
    {"name": "Brasil", "code": "BRA", "group": "D", "flag": "🇧🇷"},
    {"name": "Por definir D2", "code": "D2", "group": "D", "flag": "🏳️"},
    {"name": "Por definir D3", "code": "D3", "group": "D", "flag": "🏳️"},
    {"name": "Por definir D4", "code": "D4", "group": "D", "flag": "🏳️"},
    # Group E
    {"name": "Argentina", "code": "ARG", "group": "E", "flag": "🇦🇷"},
    {"name": "Por definir E2", "code": "E2", "group": "E", "flag": "🏳️"},
    {"name": "Por definir E3", "code": "E3", "group": "E", "flag": "🏳️"},
    {"name": "Por definir E4", "code": "E4", "group": "E", "flag": "🏳️"},
    # Group F
    {"name": "Francia", "code": "FRA", "group": "F", "flag": "🇫🇷"},
    {"name": "Por definir F2", "code": "F2", "group": "F", "flag": "🏳️"},
    {"name": "Por definir F3", "code": "F3", "group": "F", "flag": "🏳️"},
    {"name": "Por definir F4", "code": "F4", "group": "F", "flag": "🏳️"},
    # Group G
    {"name": "España", "code": "ESP", "group": "G", "flag": "🇪🇸"},
    {"name": "Por definir G2", "code": "G2", "group": "G", "flag": "🏳️"},
    {"name": "Por definir G3", "code": "G3", "group": "G", "flag": "🏳️"},
    {"name": "Por definir G4", "code": "G4", "group": "G", "flag": "🏳️"},
    # Group H
    {"name": "Alemania", "code": "GER", "group": "H", "flag": "🇩🇪"},
    {"name": "Por definir H2", "code": "H2", "group": "H", "flag": "🏳️"},
    {"name": "Por definir H3", "code": "H3", "group": "H", "flag": "🏳️"},
    {"name": "Por definir H4", "code": "H4", "group": "H", "flag": "🏳️"},
    # Group I
    {"name": "Inglaterra", "code": "ENG", "group": "I", "flag": "🏴󠁧󠁢󠁥󠁮󠁧󠁿"},
    {"name": "Por definir I2", "code": "I2", "group": "I", "flag": "🏳️"},
    {"name": "Por definir I3", "code": "I3", "group": "I", "flag": "🏳️"},
    {"name": "Por definir I4", "code": "I4", "group": "I", "flag": "🏳️"},
    # Group J
    {"name": "Portugal", "code": "POR", "group": "J", "flag": "🇵🇹"},
    {"name": "Por definir J2", "code": "J2", "group": "J", "flag": "🏳️"},
    {"name": "Por definir J3", "code": "J3", "group": "J", "flag": "🏳️"},
    {"name": "Por definir J4", "code": "J4", "group": "J", "flag": "🏳️"},
    # Group K
    {"name": "Países Bajos", "code": "NED", "group": "K", "flag": "🇳🇱"},
    {"name": "Por definir K2", "code": "K2", "group": "K", "flag": "🏳️"},
    {"name": "Por definir K3", "code": "K3", "group": "K", "flag": "🏳️"},
    {"name": "Por definir K4", "code": "K4", "group": "K", "flag": "🏳️"},
    # Group L
    {"name": "Japón", "code": "JPN", "group": "L", "flag": "🇯🇵"},
    {"name": "Por definir L2", "code": "L2", "group": "L", "flag": "🏳️"},
    {"name": "Por definir L3", "code": "L3", "group": "L", "flag": "🏳️"},
    {"name": "Por definir L4", "code": "L4", "group": "L", "flag": "🏳️"},
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
    matchday_counter = 1
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

        day_offset = 0
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
