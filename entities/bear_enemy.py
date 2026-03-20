from typing import Tuple

import pygame

from entities.enemy import Enemy
from settings import BEAR_COLOR, BEAR_DAMAGED_COLOR, BLACK, RED


class BearEnemy(Enemy):
    def __init__(self, lane, speed: float):
        super().__init__(lane, speed, hp=2)

    def get_draw_data(self) -> Tuple[float, float, int]:
        x, y = self.lane.position(self.progress)
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