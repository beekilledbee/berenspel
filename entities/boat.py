from typing import Optional, TYPE_CHECKING, Tuple
import math
import random

import pygame

from settings import GIRL_COLOR, RED, SKIN_COLOR

if TYPE_CHECKING:
    from entities.sea_monster import SeaMonster
    from entities.lane import Lane


BOAT_HULL_COLOR = (120, 78, 45)
BOAT_INNER_COLOR = (158, 108, 66)
BOAT_EDGE_COLOR = (80, 48, 28)
BOAT_SEAT_COLOR = (95, 62, 38)
PASSENGER_CLOTHES = [
    (220, 120, 170),
    (120, 170, 230),
    (230, 190, 90),
]


class Boat:
    def __init__(self, lane: "Lane", speed: float):
        self.lane = lane
        self.speed = speed
        self.progress = 0.0
        self.saved = False
        self.captured = False
        self.capture_monster: Optional["SeaMonster"] = None
        self.wake_particles = []
        self.wake_spawn_timer = 0.0

        self.bob_phase = self.lane.index * 0.9
        self.passenger_count = random.randint(1, 4)

    def update(self, dt: float) -> None:
        if self.saved or self.captured:
            return

        self.progress += self.speed * dt

        self.wake_spawn_timer -= dt
        if self.wake_spawn_timer <= 0:
            x, y, size = self.get_draw_data()

            hull_h = int(size * 2.0)
            stern_y = y - hull_h * 0.55

            self.wake_particles.append({
                "x": x + random.uniform(-4, 4),
                "y": stern_y + random.uniform(-2, 2),
                "radius": random.uniform(2.5, 4.5),
                "life": 0.55,
                "max_life": 0.55,
                "vy": random.uniform(-8, -3),
            })

            self.wake_spawn_timer = 0.06

        new_particles = []
        for p in self.wake_particles:
            p["life"] -= dt
            if p["life"] <= 0:
                continue

            p["y"] += p["vy"] * dt
            p["radius"] += dt * 3.0
            new_particles.append(p)

        self.wake_particles = new_particles

    def rotate_point(self, px: float, py: float, cx: float, cy: float, angle: float) -> tuple[float, float]:
        dx = px - cx
        dy = py - cy
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        return (
            cx + dx * cos_a - dy * sin_a,
            cy + dx * sin_a + dy * cos_a,
        )

    def get_draw_data(self) -> Tuple[float, float, int]:
        x, y = self.lane.position(self.progress)

        size = 34

        t = pygame.time.get_ticks() / 1000.0
        bob_y = math.sin(t * 3.2 + self.bob_phase) * max(1.5, size * 0.05)
        sway_x = math.sin(t * 2.2 + self.bob_phase) * max(1.0, size * 0.035)

        return x + sway_x, y + bob_y, size

    def draw(self, screen: pygame.Surface) -> None:
        for p in self.wake_particles:
            alpha = int(255 * (p["life"] / p["max_life"]) * 0.45)
            bubble_surface = pygame.Surface(
                (int(p["radius"] * 4), int(p["radius"] * 4)),
                pygame.SRCALPHA
            )
            pygame.draw.circle(
                bubble_surface,
                (220, 240, 255, alpha),
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

        x, y, size = self.get_draw_data()

        t = pygame.time.get_ticks() / 1000.0
        tilt = math.sin(t * 2.4 + self.bob_phase) * 0.08

        hull_w = int(size * 1.2)
        hull_h = int(size * 2.0)

        stern_y = y - hull_h * 0.55
        bow_y = y + hull_h * 0.55
        left_x = x - hull_w * 0.5
        right_x = x + hull_w * 0.5

        hull_points = [
            (left_x, y + hull_h * 0.18),
            (left_x * 0.985 + x * 0.015, stern_y),
            (right_x * 0.985 + x * 0.015, stern_y),
            (right_x, y + hull_h * 0.18),
            (x, bow_y),
        ]
        hull_points = [self.rotate_point(px, py, x, y, tilt) for px, py in hull_points]

        pygame.draw.polygon(screen, BOAT_HULL_COLOR, hull_points)
        pygame.draw.polygon(screen, BOAT_EDGE_COLOR, hull_points, 2)

        inner_margin_x = hull_w * 0.15
        inner_margin_top = hull_h * 0.18
        inner_margin_bottom = hull_h * 0.15

        inner_points = [
            (left_x + inner_margin_x, y + hull_h * 0.12),
            (left_x + inner_margin_x, stern_y + inner_margin_top),
            (right_x - inner_margin_x, stern_y + inner_margin_top),
            (right_x - inner_margin_x, y + hull_h * 0.12),
            (x, bow_y - inner_margin_bottom),
        ]
        inner_points = [self.rotate_point(px, py, x, y, tilt) for px, py in inner_points]

        pygame.draw.polygon(screen, BOAT_INNER_COLOR, inner_points)

        seat_y1 = y - hull_h * 0.18
        seat_y2 = y + hull_h * 0.02
        seat_y3 = y + hull_h * 0.22
        seat_x1 = x - hull_w * 0.24
        seat_x2 = x + hull_w * 0.24

        seat1_start = self.rotate_point(seat_x1, seat_y1, x, y, tilt)
        seat1_end = self.rotate_point(seat_x2, seat_y1, x, y, tilt)
        seat2_start = self.rotate_point(seat_x1, seat_y2, x, y, tilt)
        seat2_end = self.rotate_point(seat_x2, seat_y2, x, y, tilt)
        seat3_start = self.rotate_point(seat_x1, seat_y3, x, y, tilt)
        seat3_end = self.rotate_point(seat_x2, seat_y3, x, y, tilt)

        pygame.draw.line(screen, BOAT_SEAT_COLOR, seat1_start, seat1_end, 2)
        pygame.draw.line(screen, BOAT_SEAT_COLOR, seat2_start, seat2_end, 2)
        pygame.draw.line(screen, BOAT_SEAT_COLOR, seat3_start, seat3_end, 2)

        passenger_positions = []

        if self.passenger_count == 1:
            passenger_positions = [
                (x, y + hull_h * 0.08),
            ]
        elif self.passenger_count == 2:
            passenger_positions = [
                (x - hull_w * 0.14, y + hull_h * 0.02),
                (x + hull_w * 0.14, y + hull_h * 0.02),
            ]
        elif self.passenger_count == 3:
            passenger_positions = [
                (x - hull_w * 0.16, y - hull_h * 0.02),
                (x + hull_w * 0.16, y - hull_h * 0.02),
                (x, y + hull_h * 0.18),
            ]
        elif self.passenger_count == 4:
            passenger_positions = [
                (x - hull_w * 0.16, y - hull_h * 0.06),
                (x + hull_w * 0.16, y - hull_h * 0.06),
                (x - hull_w * 0.16, y + hull_h * 0.18),
                (x + hull_w * 0.16, y + hull_h * 0.18),
            ]

        head_radius = max(4, int(size * 0.18))
        body_w = max(7, int(size * 0.22))
        body_h = max(9, int(size * 0.28))

        for i, (px, py) in enumerate(passenger_positions):
            rpx, rpy = self.rotate_point(px, py, x, y, tilt)

            head_x, head_y = self.rotate_point(px, py - body_h * 0.45, x, y, tilt)
            pygame.draw.circle(screen, SKIN_COLOR, (int(head_x), int(head_y)), head_radius)

            body_rect = pygame.Rect(0, 0, body_w, body_h)
            body_rect.center = (int(rpx), int(rpy))
            pygame.draw.ellipse(screen, PASSENGER_CLOTHES[i % len(PASSENGER_CLOTHES)], body_rect)

        if self.captured:
            cross_pad = 5
            rect = pygame.Rect(
                int(left_x) + cross_pad,
                int(stern_y) + cross_pad,
                int(hull_w) - cross_pad * 2,
                int(hull_h) - cross_pad * 2,
            )
            cross_tl = self.rotate_point(rect.left, rect.top, x, y, tilt)
            cross_br = self.rotate_point(rect.right, rect.bottom, x, y, tilt)
            cross_tr = self.rotate_point(rect.right, rect.top, x, y, tilt)
            cross_bl = self.rotate_point(rect.left, rect.bottom, x, y, tilt)

            pygame.draw.line(screen, RED, cross_tl, cross_br, 2)
            pygame.draw.line(screen, RED, cross_tr, cross_bl, 2)