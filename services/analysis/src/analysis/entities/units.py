from enum import StrEnum
from typing import NewType

Season = NewType("Season", int)
RoundNumber = NewType("RoundNumber", int)
LapNumber = NewType("LapNumber", int)
Position = NewType("Position", int)
Milliseconds = NewType("Milliseconds", int)
Distance = NewType("Distance", float)


class DriverStatus(StrEnum):
    RUNNING = "running"
    FINISHED = "finished"
    OUT = "out"
