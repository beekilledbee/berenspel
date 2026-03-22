import math

import pygame


class Projectile:
    def __init__(self, x: float, y: float, angle: float, speed: float,
                 damage: int, explosion_radius: float):
        self.x = x
        self.y = y
        self.angle = angle
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.damage = damage
        self.explosion_radius = explosion_radius
        self.alive = True
        self.exploding = False
        self.explosion_timer = 0.0
        self.explosion_duration = 0.35
        self.crossed_water = False
        # Smoke trail positions
        self.trail: list[tuple[float, float, float]] = []

    def update(self, dt: float) -> bool:
        if self.exploding:
            self.explosion_timer -= dt
            if self.explosion_timer <= 0:
                self.alive = False
            # Fade trail during explosion
            self.trail = [(x, y, a - dt * 3) for x, y, a in self.trail if a - dt * 3 > 0]
            return self.alive

        # Store trail position
        self.trail.append((self.x, self.y, 1.0))
        if len(self.trail) > 12:
            self.trail.pop(0)
        # Fade older trail points
        self.trail = [(x, y, a - dt * 4) for x, y, a in self.trail if a - dt * 4 > 0]

        self.x += self.vx * dt
        self.y += self.vy * dt

        # Remove if off screen
        if self.x < -50 or self.x > 1330 or self.y < -50 or self.y > 770:
            self.alive = False

        return self.alive

    def explode(self) -> None:
        self.exploding = True
        self.explosion_timer = self.explosion_duration
        self.vx = 0
        self.vy = 0

    def draw(self, screen: pygame.Surface) -> None:
        if self.exploding:
            t = self.explosion_timer / self.explosion_duration
            radius = int(self.explosion_radius * (0.4 + 0.6 * (1.0 - t)))
            # Outer fireball
            alpha = int(180 * t)
            explosion_surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(explosion_surface, (255, 80, 20, alpha), (radius, radius), radius)
            # Middle ring
            mid_r = max(4, int(radius * 0.65))
            pygame.draw.circle(explosion_surface, (255, 160, 40, min(255, alpha + 40)), (radius, radius), mid_r)
            # Hot core
            core_r = max(3, int(radius * 0.3))
            pygame.draw.circle(explosion_surface, (255, 240, 100, min(255, alpha + 60)), (radius, radius), core_r)
            screen.blit(explosion_surface, (int(self.x) - radius, int(self.y) - radius))
        else:
            # Smoke trail
            for tx, ty, ta in self.trail:
                trail_alpha = int(80 * ta)
                trail_r = max(2, int(5 * ta))
                trail_surf = pygame.Surface((trail_r * 2, trail_r * 2), pygame.SRCALPHA)
                pygame.draw.circle(trail_surf, (180, 160, 130, trail_alpha), (trail_r, trail_r), trail_r)
                screen.blit(trail_surf, (int(tx) - trail_r, int(ty) - trail_r))

            # Rocket body (elongated along direction)
            dx = math.cos(self.angle)
            dy = math.sin(self.angle)
            tail_x = self.x - dx * 10
            tail_y = self.y - dy * 10
            tip_x = self.x + dx * 6
            tip_y = self.y + dy * 6
            # Body
            pygame.draw.line(screen, (80, 90, 50), (int(tail_x), int(tail_y)), (int(tip_x), int(tip_y)), 7)
            # Warhead tip
            pygame.draw.circle(screen, (200, 80, 30), (int(tip_x), int(tip_y)), 5)
            pygame.draw.circle(screen, (255, 140, 40), (int(tip_x), int(tip_y)), 3)
            # Exhaust flame at tail
            flame_x = tail_x - dx * 6
            flame_y = tail_y - dy * 6
            pygame.draw.circle(screen, (255, 180, 40), (int(tail_x), int(tail_y)), 4)
            pygame.draw.circle(screen, (255, 100, 20), (int(flame_x), int(flame_y)), 3)
