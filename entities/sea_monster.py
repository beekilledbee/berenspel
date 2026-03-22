from typing import Tuple, Optional, TYPE_CHECKING
import math
import random

import pygame

from entities.enemy import Enemy
from settings import MONSTER_COLOR, MONSTER_DAMAGED_COLOR, BLACK, RED

if TYPE_CHECKING:
    from entities.boat import Boat


MONSTER_BODY_COLOR = (58, 122, 76)
MONSTER_DAMAGED_COLOR = (86, 148, 95)
MONSTER_BELLY_COLOR = (112, 170, 122)
MONSTER_DARK_COLOR = (30, 66, 40)
MONSTER_EYE_COLOR = (15, 15, 15)


class SeaMonster(Enemy):
    def __init__(self, lane, speed: float):
        super().__init__(lane, speed, hp=2)
        self.lateral_offset = random.uniform(-60.0, 60.0)
        self.target_boat: Optional["Boat"] = None

        self.wobble_phase = random.uniform(0.0, 6.28)
        self.wake_particles = []
        self.wake_spawn_timer = 0.0

    def has_valid_target(self) -> bool:
        return (
            self.target_boat is not None
            and not self.target_boat.saved
            and not self.target_boat.captured
        )

    def update(self, dt: float) -> None:
        super().update(dt)

        if self.dead:
            self._update_wake(dt)
            return

        self.wake_spawn_timer -= dt
        if self.wake_spawn_timer <= 0:
            x, y, size = self.get_draw_data()

            self.wake_particles.append({
                "x": x + random.uniform(-size * 0.2, size * 0.2),
                "y": y - size * 0.35 + random.uniform(-3, 3),
                "radius": random.uniform(2.0, 4.0),
                "life": 0.45,
                "max_life": 0.45,
                "vy": random.uniform(-8, -3),
            })
            self.wake_spawn_timer = 0.05

        self._update_wake(dt)

    def _update_wake(self, dt: float) -> None:
        new_particles = []
        for p in self.wake_particles:
            p["life"] -= dt
            if p["life"] <= 0:
                continue

            p["y"] += p["vy"] * dt
            p["radius"] += dt * 2.5
            new_particles.append(p)

        self.wake_particles = new_particles

    def get_draw_data(self) -> Tuple[float, float, int]:
        base_x, y = self.lane.position(self.progress)

        if self.has_valid_target():
            target_x, _ = self.target_boat.lane.position(self.target_boat.progress)
            x = base_x + (target_x - base_x) * min(1.0, self.progress * 1.2)
            x += self.lateral_offset * (1.0 - self.progress) * 0.5
        else:
            x = base_x + self.lateral_offset * (1.0 - self.progress)

        size = 30

        t = pygame.time.get_ticks() / 1000.0
        sway_x = math.sin(t * 4.0 + self.wobble_phase) * max(1.0, size * 0.05)
        bob_y = math.sin(t * 3.1 + self.wobble_phase) * max(1.0, size * 0.04)

        return x + sway_x, y + bob_y, size

    def draw(self, screen: pygame.Surface) -> None:
        if not self.should_flash_draw():
            return

        x, y, size = self.get_draw_data()

        for p in self.wake_particles:
            alpha = int(255 * (p["life"] / p["max_life"]) * 0.4)
            bubble_surface = pygame.Surface(
                (int(p["radius"] * 4), int(p["radius"] * 4)),
                pygame.SRCALPHA
            )
            pygame.draw.circle(
                bubble_surface,
                (215, 240, 255, alpha),
                (bubble_surface.get_width() // 2, bubble_surface.get_height() // 2),
                int(p["radius"])
            )
            screen.blit(
                bubble_surface,
                (
                    int(p["x"] - bubble_surface.get_width() / 2),
                    int(p["y"] - bubble_surface.get_height() / 2),
                ),
            )

        color = MONSTER_COLOR if self.hp == 2 else MONSTER_DAMAGED_COLOR

        body_w = int(size * 1.35)
        body_h = int(size * 1.55)

        head_y = y + body_h * 0.42
        tail_y = y - body_h * 0.45
        left_x = x - body_w * 0.5
        right_x = x + body_w * 0.5

        body_points = [
            (x, tail_y),
            (right_x * 0.92 + x * 0.08, y - body_h * 0.08),
            (right_x, y + body_h * 0.12),
            (x + body_w * 0.22, head_y),
            (x, y + body_h * 0.52),
            (x - body_w * 0.22, head_y),
            (left_x, y + body_h * 0.12),
            (left_x * 0.92 + x * 0.08, y - body_h * 0.08),
        ]

        pygame.draw.polygon(screen, color, body_points)
        pygame.draw.polygon(screen, MONSTER_DARK_COLOR, body_points, 2)

        belly_rect = pygame.Rect(0, 0, int(body_w * 0.48), int(body_h * 0.55))
        belly_rect.center = (int(x), int(y + body_h * 0.12))
        pygame.draw.ellipse(screen, MONSTER_BELLY_COLOR, belly_rect)
        fin_left = [
            (x - body_w * 0.35, y + body_h * 0.02),
            (x - body_w * 0.68, y + body_h * 0.16),
            (x - body_w * 0.38, y + body_h * 0.26),
        ]
        fin_right = [
            (x + body_w * 0.35, y + body_h * 0.02),
            (x + body_w * 0.68, y + body_h * 0.16),
            (x + body_w * 0.38, y + body_h * 0.26),
        ]
        pygame.draw.polygon(screen, color, fin_left)
        pygame.draw.polygon(screen, color, fin_right)

        eye_radius = max(2, int(size * 0.10))
        eye_y = int(y + body_h * 0.22)
        pygame.draw.circle(screen, MONSTER_EYE_COLOR, (int(x - body_w * 0.13), eye_y), eye_radius)
        pygame.draw.circle(screen, MONSTER_EYE_COLOR, (int(x + body_w * 0.13), eye_y), eye_radius)

        # tanden
        mouth_y = int(y + body_h * 0.34)
        pygame.draw.line(
            screen,
            MONSTER_DARK_COLOR,
            (int(x - body_w * 0.12), mouth_y),
            (int(x + body_w * 0.12), mouth_y),
            2,
        )

        pygame.draw.line(
            screen,
            MONSTER_DARK_COLOR,
            (int(x), int(tail_y)),
            (int(x), int(tail_y - body_h * 0.18)),
            max(2, int(size * 0.08)),
        )

        pygame.draw.circle(screen, RED, (int(x), int(y)), max(5, size // 5), 2)