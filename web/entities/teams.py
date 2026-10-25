from collections.abc import Iterable
from dataclasses import dataclass
from hashlib import sha1
from typing import Protocol

TEAM_NAMES = {
    "mclaren": "McLaren",
    "ferrari": "Ferrari",
    "red_bull": "Red Bull",
    "mercedes": "Mercedes",
    "aston_martin": "Aston Martin",
    "alpine": "Alpine",
    "williams": "Williams",
    "rb": "RB",
    "sauber": "Sauber",
    "haas": "Haas",
    "renault": "Renault",
    "lotus_f1": "Lotus",
    "force_india": "Force India",
    "racing_point": "Racing Point",
    "toro_rosso": "Toro Rosso",
    "alphatauri": "AlphaTauri",
    "alfa": "Alfa Romeo",
    "benetton": "Benetton",
    "jordan": "Jordan",
    "brawn": "Brawn",
    "bmw_sauber": "BMW Sauber",
    "toyota": "Toyota",
    "jaguar": "Jaguar",
    "minardi": "Minardi",
    "tyrrell": "Tyrrell",
    "brabham": "Brabham",
    "lotus": "Lotus",
}

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


def team_name(team: str | None) -> str:
    if team is None:
        return ""
    return TEAM_NAMES.get(team, team.replace("_", " ").title())


def driver_label(code: str | None, driver_id: str) -> str:
    return code or driver_id[:3].upper()


@dataclass(frozen=True, slots=True)
class LineStyle:
    color: str
    dashed: bool


class TeamMember(Protocol):
    @property
    def driver_id(self) -> str: ...

    @property
    def team(self) -> str | None: ...


def line_styles(drivers: Iterable[TeamMember]) -> dict[str, LineStyle]:
    seen_teams: set[str | None] = set()
    styles = {}
    for driver in drivers:
        styles[driver.driver_id] = LineStyle(team_color(driver.team), driver.team in seen_teams)
        seen_teams.add(driver.team)
    return styles
