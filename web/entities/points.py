from web.entities.units import Season

SCHEMES = (
    (2010, (25, 18, 15, 12, 10, 8, 6, 4, 2, 1)),
    (2003, (10, 8, 6, 5, 4, 3, 2, 1)),
    (1991, (10, 6, 4, 3, 2, 1)),
    (1961, (9, 6, 4, 3, 2, 1)),
    (1960, (8, 6, 4, 3, 2, 1)),
    (1950, (8, 6, 4, 3, 2)),
)


def points_for(season: Season, rank: int) -> int:
    for since, scheme in SCHEMES:
        if season >= since:
            return scheme[rank - 1] if rank <= len(scheme) else 0
    return 0


def fastest_lap_bonus(season: Season, rank: int) -> int:
    if 1950 <= season <= 1959:
        return 1
    return 1 if 2019 <= season <= 2024 and rank <= 10 else 0
