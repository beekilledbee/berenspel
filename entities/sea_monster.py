from typing import Tuple, Optional, TYPE_CHECKING
import random

import pygame

from entities.enemy import Enemy
from settings import BEAR_COLOR, BEAR_DAMAGED_COLOR, BLACK, RED

if TYPE_CHECKING:
    from entities.boat import Boat


class SeaMonster(Enemy):
    def __init__(self, lane, speed: float):
        super().__init__(lane, speed, hp=2)
        self.lateral_offset = random.uniform(-60.0, 60.0)
        self.target_boat: Optional["Boat"] = None

    def get_draw_data(self) -> Tuple[float, float, int]:
        base_x, y = self.lane.position(self.progress)

        if self.target_boat is not None and not self.target_boat.saved:
            target_x, _ = self.target_boat.lane.position(self.target_boat.progress)
            x = base_x + (target_x - base_x) * self.progress
            x += self.lateral_offset * (1.0 - self.progress) * 0.5
        else:
            x = base_x + self.lateral_offset * (1.0 - self.progress)

        scale = 0.34 + self.progress * 1.12
        size = max(14, int(28 * scale))
        return x, y, size

    def draw(self, screen: pygame.Surface) -> None:
        if not self.should_flash_draw():
            return

        x, y, size = self.get_draw_data()
        body = pygame.Rect(0, 0, int(size * 1.3), size)
        body.center = (int(x), int(y))
        color = BEAR_COLOR if self.hp == 2 else BEAR_DAMAGED_COLOR

        pygame.draw.ellipse(screen, color, body)
        pygame.draw.circle(screen, color, (body.left + size // 4, body.top + size // 4), max(4, size // 5))
        pygame.draw.circle(screen, color, (body.right - size // 4, body.top + size // 4), max(4, size // 5))
        pygame.draw.circle(screen, BLACK, (body.centerx + size // 4, body.centery - size // 9), max(3, size // 8))

        if self.grabbing:
            pygame.draw.circle(screen, RED, (body.centerx, body.centery), max(4, size // 5), 2)