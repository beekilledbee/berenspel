import math
from typing import Tuple

import pygame

from settings import GUN_COLOR, PLAYER_COLOR, PLAYER_X, PLAYER_Y, SKIN_COLOR, WHITE, YELLOW


class PlayerGun:
    def __init__(self):
        self.x = PLAYER_X
        self.y = PLAYER_Y
        self.angle = -math.pi / 2
        self.muzzle_flash = 0.0

    def update(self, mouse_pos: Tuple[int, int], dt: float) -> None:
        mx, my = mouse_pos
        self.angle = math.atan2(my - self.y, mx - self.x)
        self.muzzle_flash = max(0.0, self.muzzle_flash - dt)

    def shoot(self) -> None:
        self.muzzle_flash = 0.08

    def muzzle_position(self) -> Tuple[float, float]:
        barrel_length = 84
        return (
            self.x + math.cos(self.angle) * barrel_length,
            self.y + math.sin(self.angle) * barrel_length,
        )

    def draw(self, screen: pygame.Surface) -> None:
        body = pygame.Rect(0, 0, 116, 74)
        body.center = (self.x, self.y + 22)
        pygame.draw.ellipse(screen, PLAYER_COLOR, body)
        pygame.draw.circle(screen, SKIN_COLOR, (self.x, self.y - 10), 28)

        muzzle_x, muzzle_y = self.muzzle_position()
        pygame.draw.line(screen, GUN_COLOR, (self.x, self.y), (muzzle_x, muzzle_y), 12)

        if self.muzzle_flash > 0:
            flash_size = 16 + int(self.muzzle_flash * 120)
            pygame.draw.circle(screen, YELLOW, (int(muzzle_x), int(muzzle_y)), flash_size)
            pygame.draw.circle(screen, WHITE, (int(muzzle_x), int(muzzle_y)), max(4, flash_size // 2))