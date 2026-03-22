from typing import Optional, Tuple

import pygame

from settings import BEAR_FLASH_DURATION, BEAR_FLASH_INTERVAL


class Enemy:
    def __init__(self, lane, speed: float, hp: int):
        self.lane = lane
        self.speed = speed
        self.progress = 0.0
        self.hp = hp
        self.dead = False
        self.remove = False
        self.death_timer = 0.0
        self.grabbing = False
        self.target_boat: Optional[object] = None

    def update(self, dt: float) -> None:
        if self.dead:
            self.death_timer -= dt
            if self.death_timer <= 0:
                self.remove = True
            return
        self.progress += self.speed * dt

    def hit(self, damage: int = 1) -> None:
        self.hp -= damage
        if self.hp <= 0:
            self.dead = True
            self.death_timer = BEAR_FLASH_DURATION
            self.grabbing = False
            self.target_boat = None

    def should_flash_draw(self) -> bool:
        if not self.dead:
            return True
        return int(self.death_timer / BEAR_FLASH_INTERVAL) % 2 == 0

    def get_draw_data(self) -> Tuple[float, float, int]:
        raise NotImplementedError

    def draw(self, screen: pygame.Surface) -> None:
        raise NotImplementedError