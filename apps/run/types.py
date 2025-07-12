from datetime import (
    timedelta,
)
from typing import (
    TypedDict,
)


class Athlete(TypedDict):
    athlete__id: int
    athlete__first_name: str
    athlete__last_name: str
    athlete__username: str


class Challenge(TypedDict):
    full_name: str
    athletes: list[Athlete]


class RunWithTime(TypedDict):
    time: timedelta | None
