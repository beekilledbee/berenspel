import math
from typing import Tuple, Optional

import pygame

from settings import PLAYER_COLOR, PLAYER_X, PLAYER_Y, SKIN_COLOR, WHITE
from entities.weapon import Weapon


class PlayerGun:
    def __init__(self):
        self.x = PLAYER_X
        self.y = PLAYER_Y
        self.angle = -math.pi / 2
        self.muzzle_flash = 0.0
        self._weapon: Optional[Weapon] = None

    @property
    def weapon(self) -> Optional[Weapon]:
        return self._weapon

    @weapon.setter
    def weapon(self, weapon: Optional[Weapon]) -> None:
        self._weapon = weapon

    def update(self, mouse_pos: Tuple[int, int], dt: float) -> None:
        mx, my = mouse_pos
        self.angle = math.atan2(my - self.y, mx - self.x)
        self.muzzle_flash = max(0.0, self.muzzle_flash - dt)

    def shoot(self) -> None:
        self.muzzle_flash = 0.08

    def muzzle_position(self) -> Tuple[float, float]:
        barrel_length = self._weapon.barrel_length if self._weapon else 84
        return (
            self.x + math.cos(self.angle) * barrel_length,
            self.y + math.sin(self.angle) * barrel_length,
        )

    def _draw_pistol(self, screen: pygame.Surface) -> None:
        muzzle_x, muzzle_y = self.muzzle_position()
        # Thin barrel
        pygame.draw.line(screen, (35, 35, 35), (self.x, self.y), (int(muzzle_x), int(muzzle_y)), 8)

        if self.muzzle_flash > 0:
            flash_size = 12 + int(self.muzzle_flash * 100)
            pygame.draw.circle(screen, (255, 220, 80), (int(muzzle_x), int(muzzle_y)), flash_size)
            pygame.draw.circle(screen, WHITE, (int(muzzle_x), int(muzzle_y)), max(3, flash_size // 2))

    def _draw_shotgun(self, screen: pygame.Surface) -> None:
        muzzle_x, muzzle_y = self.muzzle_position()
        dx = math.cos(self.angle)
        dy = math.sin(self.angle)
        perp_x = -dy
        perp_y = dx

        # Double barrel effect - two parallel lines
        offset = 4
        for sign in (-1, 1):
            sx = self.x + perp_x * offset * sign
            sy = self.y + perp_y * offset * sign
            ex = muzzle_x + perp_x * offset * sign
            ey = muzzle_y + perp_y * offset * sign
            pygame.draw.line(screen, (60, 50, 40), (int(sx), int(sy)), (int(ex), int(ey)), 7)

        # Wooden stock - thicker section near player
        stock_end_x = self.x + dx * 30
        stock_end_y = self.y + dy * 30
        pygame.draw.line(screen, (100, 65, 30), (int(self.x), int(self.y)), (int(stock_end_x), int(stock_end_y)), 16)

        if self.muzzle_flash > 0:
            flash_size = 20 + int(self.muzzle_flash * 160)
            # Wide spread flash
            for sign in (-1, 0, 1):
                fx = muzzle_x + perp_x * sign * 8
                fy = muzzle_y + perp_y * sign * 8
                pygame.draw.circle(screen, (255, 200, 60), (int(fx), int(fy)), max(4, flash_size // 2))
            pygame.draw.circle(screen, WHITE, (int(muzzle_x), int(muzzle_y)), max(4, flash_size // 3))

    def _draw_rifle(self, screen: pygame.Surface) -> None:
        muzzle_x, muzzle_y = self.muzzle_position()
        dx = math.cos(self.angle)
        dy = math.sin(self.angle)

        # Long sleek barrel
        pygame.draw.line(screen, (50, 50, 55), (self.x, self.y), (int(muzzle_x), int(muzzle_y)), 10)

        # Scope on top - small rectangle along the barrel
        scope_start = 0.3
        scope_end = 0.6
        barrel_len = self._weapon.barrel_length if self._weapon else 100
        perp_x = -dy
        perp_y = dx
        scope_offset = 7
        s1x = self.x + dx * barrel_len * scope_start + perp_x * scope_offset
        s1y = self.y + dy * barrel_len * scope_start + perp_y * scope_offset
        s2x = self.x + dx * barrel_len * scope_end + perp_x * scope_offset
        s2y = self.y + dy * barrel_len * scope_end + perp_y * scope_offset
        pygame.draw.line(screen, (20, 20, 20), (int(s1x), int(s1y)), (int(s2x), int(s2y)), 5)
        # Scope lens circles
        pygame.draw.circle(screen, (100, 180, 255), (int(s1x), int(s1y)), 4)
        pygame.draw.circle(screen, (100, 180, 255), (int(s2x), int(s2y)), 4)

        if self.muzzle_flash > 0:
            flash_size = 10 + int(self.muzzle_flash * 80)
            pygame.draw.circle(screen, (255, 255, 200), (int(muzzle_x), int(muzzle_y)), flash_size)
            pygame.draw.circle(screen, WHITE, (int(muzzle_x), int(muzzle_y)), max(3, flash_size // 2))

    def _draw_rpg(self, screen: pygame.Surface) -> None:
        muzzle_x, muzzle_y = self.muzzle_position()
        dx = math.cos(self.angle)
        dy = math.sin(self.angle)

        # Thick launcher tube
        pygame.draw.line(screen, (70, 80, 50), (self.x, self.y), (int(muzzle_x), int(muzzle_y)), 18)
        # Inner dark tube
        inner_start_x = self.x + dx * 20
        inner_start_y = self.y + dy * 20
        pygame.draw.line(screen, (40, 45, 30), (int(inner_start_x), int(inner_start_y)),
                         (int(muzzle_x), int(muzzle_y)), 12)

        # Rear exhaust opening
        rear_x = self.x - dx * 10
        rear_y = self.y - dy * 10
        pygame.draw.circle(screen, (50, 50, 50), (int(rear_x), int(rear_y)), 10)
        pygame.draw.circle(screen, (30, 30, 30), (int(rear_x), int(rear_y)), 6)

        # Grip/handle underneath
        perp_x = -dy
        perp_y = dx
        grip_x = self.x + dx * 25 + perp_x * 14
        grip_y = self.y + dy * 25 + perp_y * 14
        pygame.draw.line(screen, (90, 70, 40),
                         (int(self.x + dx * 20), int(self.y + dy * 20)),
                         (int(grip_x), int(grip_y)), 8)

        # Warhead tip at muzzle - orange/red cone
        tip_x = muzzle_x + dx * 8
        tip_y = muzzle_y + dy * 8
        pygame.draw.circle(screen, (200, 80, 30), (int(tip_x), int(tip_y)), 7)
        pygame.draw.circle(screen, (255, 140, 40), (int(tip_x), int(tip_y)), 4)

        if self.muzzle_flash > 0:
            flash_size = 22 + int(self.muzzle_flash * 180)
            # Backblast effect from rear
            pygame.draw.circle(screen, (255, 140, 40), (int(rear_x), int(rear_y)), flash_size)
            pygame.draw.circle(screen, (255, 220, 80), (int(rear_x), int(rear_y)), max(4, flash_size // 2))
            # Smaller front flash
            pygame.draw.circle(screen, (255, 140, 40), (int(muzzle_x), int(muzzle_y)), max(4, flash_size // 3))

    def draw(self, screen: pygame.Surface) -> None:
        # Draw player body
        body = pygame.Rect(0, 0, 116, 74)
        body.center = (self.x, self.y + 22)
        pygame.draw.ellipse(screen, PLAYER_COLOR, body)
        pygame.draw.circle(screen, SKIN_COLOR, (self.x, self.y - 10), 28)

        # Draw weapon-specific visuals
        weapon_name = self._weapon.name if self._weapon else "Pistol"
        if weapon_name == "Shotgun":
            self._draw_shotgun(screen)
        elif weapon_name == "Rifle":
            self._draw_rifle(screen)
        elif weapon_name == "RPG":
            self._draw_rpg(screen)
        else:
            self._draw_pistol(screen)