from typing import Optional, TYPE_CHECKING, Tuple

import pygame

from settings import GIRL_COLOR, RED, SKIN_COLOR

if TYPE_CHECKING:
    from entities.bear_enemy import BearEnemy
    from entities.lane import Lane


class Girl:
    def __init__(self, lane: "Lane", speed: float):
        self.lane = lane
        self.speed = speed
        self.progress = 0.0
        self.saved = False
        self.captured = False
        self.capture_bear: Optional["BearEnemy"] = None

    def update(self, dt: float) -> None:
        if self.saved:
            return
        if self.captured and self.capture_bear is not None:
            self.progress = self.capture_bear.progress
            return
        self.progress += self.speed * dt
        if self.progress >= 1.0:
            self.saved = True

    def get_draw_data(self) -> Tuple[float, float, int]:
        x, y = self.lane.position(self.progress)
        scale = 0.28 + self.progress * 0.95
        size = max(10, int(18 * scale))
        return x, y, size

    def draw(self, screen: pygame.Surface) -> None:
        x, y, size = self.get_draw_data()
        body = pygame.Rect(0, 0, size, int(size * 1.6))
        body.center = (int(x), int(y))
        pygame.draw.ellipse(screen, GIRL_COLOR, body)
        pygame.draw.circle(screen, SKIN_COLOR, (body.centerx, body.top + size // 3), max(4, size // 3))
        if self.captured:
            pygame.draw.line(screen, RED, body.topleft, body.bottomright, 2)
            pygame.draw.line(screen, RED, body.topright, body.bottomleft, 2)