from datetime import date, datetime

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from catalogue.entities.json_object import JsonObject


class Base(DeclarativeBase):
    pass


class Race(Base):
    __tablename__ = "races"
    __table_args__ = (UniqueConstraint("season", "round"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    season: Mapped[int]
    round_number: Mapped[int] = mapped_column("round")
    name: Mapped[str]
    circuit_id: Mapped[str]
    circuit_name: Mapped[str]
    date: Mapped[date]
    total_laps: Mapped[int | None]


class Driver(Base):
    __tablename__ = "drivers"

    id: Mapped[str] = mapped_column(primary_key=True)
    code: Mapped[str | None]
    given_name: Mapped[str]
    family_name: Mapped[str]


class Result(Base):
    __tablename__ = "results"

    race_id: Mapped[int] = mapped_column(ForeignKey("races.id"), primary_key=True)
    driver_id: Mapped[str] = mapped_column(ForeignKey("drivers.id"), primary_key=True)
    position: Mapped[int | None]
    grid: Mapped[int]
    laps: Mapped[int]
    status: Mapped[str]


class Lap(Base):
    __tablename__ = "laps"

    race_id: Mapped[int] = mapped_column(ForeignKey("races.id"), primary_key=True)
    driver_id: Mapped[str] = mapped_column(ForeignKey("drivers.id"), primary_key=True)
    lap: Mapped[int] = mapped_column(primary_key=True)
    position: Mapped[int]
    time_ms: Mapped[int | None]


class PitStop(Base):
    __tablename__ = "pit_stops"

    race_id: Mapped[int] = mapped_column(ForeignKey("races.id"), primary_key=True)
    driver_id: Mapped[str] = mapped_column(ForeignKey("drivers.id"), primary_key=True)
    stop: Mapped[int] = mapped_column(primary_key=True)
    lap: Mapped[int]
    duration_ms: Mapped[int | None]


class RawResponse(Base):
    __tablename__ = "raw_responses"

    url: Mapped[str] = mapped_column(primary_key=True)
    fetched_at: Mapped[datetime]
    body: Mapped[JsonObject] = mapped_column(JSONB)
