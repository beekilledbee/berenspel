from dataclasses import dataclass
from typing import Tuple

from settings import HORIZON_Y, PLAYER_Y


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


@dataclass
class Lane:
    index: int
    horizon_x: float
    end_x: float

    def position(self, progress: float) -> Tuple[float, float]:
        p = clamp(progress, 0.0, 1.0)
        x = self.horizon_x + (self.end_x - self.horizon_x) * p
        y = HORIZON_Y + (PLAYER_Y - HORIZON_Y) * p
        return x, y