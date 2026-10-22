from web.entities.units import Season

SCHEMES = (
    (2010, (25, 18, 15, 12, 10, 8, 6, 4, 2, 1)),
    (2003, (10, 8, 6, 5, 4, 3, 2, 1)),
    (1991, (10, 6, 4, 3, 2, 1)),
    (1961, (9, 6, 4, 3, 2, 1)),
    (1950, (8, 6, 4, 3, 2)),
)
FASTEST_LAP_BONUS_SEASONS = range(2019, 2025)


def points_for(season: Season, rank: int) -> int:
    for since, scheme in SCHEMES:
        if season >= since:
            return scheme[rank - 1] if rank <= len(scheme) else 0
    return 0


def fastest_lap_bonus(season: Season, rank: int) -> int:
    return 1 if season in FASTEST_LAP_BONUS_SEASONS and rank <= 10 else 0
