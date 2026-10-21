from hashlib import sha1

TEAM_COLORS = {
    "mclaren": "#ff8000",
    "ferrari": "#e8002d",
    "red_bull": "#3671c6",
    "mercedes": "#27f4d2",
    "aston_martin": "#229971",
    "alpine": "#ff87bc",
    "williams": "#64c4ff",
    "rb": "#6692ff",
    "sauber": "#52e252",
    "haas": "#b6babd",
    "renault": "#fff500",
    "lotus_f1": "#ffb800",
    "force_india": "#f596c8",
    "racing_point": "#f596c8",
    "toro_rosso": "#469bff",
    "alphatauri": "#5e8faa",
    "alfa": "#c92d4b",
    "benetton": "#00a19c",
    "jordan": "#ffd200",
    "brawn": "#b8fd6e",
    "bmw_sauber": "#0054a6",
    "toyota": "#cc1e4a",
    "jaguar": "#0a5c2f",
    "minardi": "#191919",
    "tyrrell": "#1e2a5a",
    "brabham": "#0f6cbf",
    "lotus": "#004225",
}


def team_color(team: str | None) -> str:
    if team in TEAM_COLORS:
        return TEAM_COLORS[team]
    digest = sha1((team or "unknown").encode()).hexdigest()
    return f"#{digest[:6]}"
