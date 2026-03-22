from dataclasses import dataclass
from typing import Tuple


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


@dataclass
class Lane:
    index: int
    start_x: float
    start_y: float
    end_x: float
    end_y: float

    def position(self, progress: float) -> Tuple[float, float]:
        p = clamp(progress, 0.0, 1.0)
        x = self.start_x + (self.end_x - self.start_x) * p
        y = self.start_y + (self.end_y - self.start_y) * p
        return x, y