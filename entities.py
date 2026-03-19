import math
import random
from dataclasses import dataclass
from typing import List, Optional, Tuple

import pygame

from settings import (
    BEAR_COLOR,
    BEAR_DAMAGED_COLOR,
    BEAR_FLASH_DURATION,
    BEAR_FLASH_INTERVAL,
    BEAR_HITS_TO_KILL,
    BEAR_SPAWN_INTERVAL,
    BLACK,
    GIRL_COLOR,
    GIRL_SPAWN_INTERVAL,
    GUN_COLOR,
    HORIZON_Y,
    PLAYER_COLOR,
    PLAYER_X,
    PLAYER_Y,
    RED,
    SKIN_COLOR,
    WHITE,
    YELLOW,
)


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


class Girl:
    def __init__(self, lane: Lane, speed: float):
        self.lane = lane
        self.speed = speed
        self.progress = 0.0
        self.saved = False
        self.captured = False
        self.capture_bear: Optional["Bear"] = None

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


class Bear:
    def __init__(self, lane: Lane, speed: float):
        self.lane = lane
        self.speed = speed
        self.progress = 0.0
        self.hits = 0
        self.dead = False
        self.remove = False
        self.death_timer = 0.0
        self.grabbing = False
        self.target_girl: Optional[Girl] = None

    def update(self, dt: float) -> None:
        if self.dead:
            self.death_timer -= dt
            if self.death_timer <= 0:
                self.remove = True
            return
        self.progress += self.speed * dt

    def hit(self) -> None:
        self.hits += 1
        if self.hits >= BEAR_HITS_TO_KILL:
            self.dead = True
            self.death_timer = BEAR_FLASH_DURATION
            self.grabbing = False
            self.target_girl = None

    def get_draw_data(self) -> Tuple[float, float, int]:
        x, y = self.lane.position(self.progress)
        scale = 0.34 + self.progress * 1.12
        size = max(14, int(28 * scale))
        return x, y, size

    def draw(self, screen: pygame.Surface) -> None:
        if self.dead:
            flash_on = int(self.death_timer / BEAR_FLASH_INTERVAL) % 2 == 0
            if not flash_on:
                return

        x, y, size = self.get_draw_data()
        body = pygame.Rect(0, 0, int(size * 1.3), size)
        body.center = (int(x), int(y))
        color = BEAR_COLOR if self.hits == 0 else BEAR_DAMAGED_COLOR

        pygame.draw.ellipse(screen, color, body)
        pygame.draw.circle(screen, color, (body.left + size // 4, body.top + size // 4), max(4, size // 5))
        pygame.draw.circle(screen, color, (body.right - size // 4, body.top + size // 4), max(4, size // 5))
        pygame.draw.circle(screen, BLACK, (body.centerx + size // 4, body.centery - size // 9), max(3, size // 8))

        if self.grabbing:
            pygame.draw.circle(screen, RED, (body.centerx, body.centery), max(4, size // 5), 2)


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


class SpawnDirector:
    def __init__(self, lanes: List[Lane]):
        self.lanes = lanes
        self.girl_timer = 0.6
        self.bear_timer = 1.0

    def update(self, dt: float) -> Tuple[bool, bool]:
        spawn_girl = False
        spawn_bear = False

        self.girl_timer -= dt
        self.bear_timer -= dt

        if self.girl_timer <= 0:
            spawn_girl = True
            self.girl_timer = random.uniform(GIRL_SPAWN_INTERVAL - 0.4, GIRL_SPAWN_INTERVAL + 0.5)

        if self.bear_timer <= 0:
            spawn_bear = True
            self.bear_timer = random.uniform(BEAR_SPAWN_INTERVAL - 0.2, BEAR_SPAWN_INTERVAL + 0.3)

        return spawn_girl, spawn_bear