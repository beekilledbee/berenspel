import math
import random
import sys
from dataclasses import dataclass
from typing import List, Optional, Tuple

import pygame

#Lars was Hier



# --------------------------------------------------
# Config
# --------------------------------------------------
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60
TITLE = "Bear Shooter Remake"

HORIZON_Y = 115
PLAYER_Y = SCREEN_HEIGHT - 78
PLAYER_X = SCREEN_WIDTH // 2

START_AMMO = 100
AMMO_REWARD = 50
GOAL_SAVED_GIRLS = 20
BEAR_HITS_TO_KILL = 2
BEAR_FLASH_DURATION = 0.5
BEAR_FLASH_INTERVAL = 0.08

GIRL_SPAWN_INTERVAL = 2.1
BEAR_SPAWN_INTERVAL = 1.35

MAX_VISIBLE_AMMO = 100
SHOT_COOLDOWN = 1 / 30

SKY_COLOR = (176, 214, 255)
FIELD_COLOR = (94, 137, 70)
FIELD_DARK = (78, 115, 58)
LANE_COLOR = (190, 205, 150)
TEXT_COLOR = (255, 255, 255)
PANEL_COLOR = (0, 0, 0, 120)
PLAYER_COLOR = (235, 212, 235)
SKIN_COLOR = (255, 220, 198)
GUN_COLOR = (35, 35, 35)
BEAR_COLOR = (128, 75, 38)
BEAR_DAMAGED_COLOR = (154, 90, 58)
GIRL_COLOR = (255, 110, 180)
BLOOD_COLOR = (170, 20, 20)
YELLOW = (255, 220, 80)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (220, 65, 65)


# --------------------------------------------------
# Helpers
# --------------------------------------------------
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


class BloodEffect:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
        self.duration = 0.22
        self.timer = self.duration

    def update(self, dt: float) -> bool:
        self.timer -= dt
        return self.timer > 0

    def draw(self, screen: pygame.Surface) -> None:
        t = self.timer / self.duration
        radius = max(2, int(16 * t))
        pygame.draw.circle(screen, BLOOD_COLOR, (int(self.x), int(self.y)), radius)
        pygame.draw.circle(screen, RED, (int(self.x + 5), int(self.y - 3)), max(2, radius // 2))
        pygame.draw.circle(screen, BLOOD_COLOR, (int(self.x - 7), int(self.y + 2)), max(2, radius // 3))


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


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("arial", 28)
        self.small_font = pygame.font.SysFont("arial", 22)
        self.big_font = pygame.font.SysFont("arial", 56, bold=True)
        self.running = True

        self.reset()

    def reset(self) -> None:
        self.lanes = self.create_lanes()
        self.gun = PlayerGun()
        self.spawner = SpawnDirector(self.lanes)

        self.girls: List[Girl] = []
        self.bears: List[Bear] = []
        self.effects: List[BloodEffect] = []

        self.saved_girls = 0
        self.score = 0
        self.ammo = START_AMMO
        self.trigger_held = False
        self.auto_fire_timer = 0.0

        self.game_over = False
        self.victory = False

    def create_lanes(self) -> List[Lane]:
        horizon_positions = [245, 420, 640, 860, 1035]
        end_positions = [165, 390, 640, 890, 1115]
        return [Lane(i, hx, ex) for i, (hx, ex) in enumerate(zip(horizon_positions, end_positions))]

    def spawn_girl(self) -> None:
        lane = random.choice(self.lanes)
        speed = random.uniform(0.12, 0.16)
        self.girls.append(Girl(lane, speed))

    def spawn_bear(self) -> None:
        lane = random.choice(self.lanes)
        speed = random.uniform(0.18, 0.24)
        self.bears.append(Bear(lane, speed))

    def ray_hits_bear(self, bear: Bear) -> bool:
        origin_x, origin_y = self.gun.x, self.gun.y
        bear_x, bear_y, size = bear.get_draw_data()

        ray_dx = math.cos(self.gun.angle)
        ray_dy = math.sin(self.gun.angle)
        to_x = bear_x - origin_x
        to_y = bear_y - origin_y

        projection = to_x * ray_dx + to_y * ray_dy
        if projection < 0:
            return False

        closest_x = origin_x + ray_dx * projection
        closest_y = origin_y + ray_dy * projection
        distance = math.hypot(bear_x - closest_x, bear_y - closest_y)
        return distance <= size * 0.45

    def shoot(self) -> bool:
        if self.game_over or self.victory:
            return False
        if self.ammo <= 0:
            return False

        self.ammo -= 1
        self.gun.shoot()

        for bear in self.bears:
            if bear.dead:
                continue
            if self.ray_hits_bear(bear):
                x, y, _ = bear.get_draw_data()
                self.effects.append(BloodEffect(x, y))
                bear.hit()
                if bear.dead:
                    self.score += 100
        return True

    def update_auto_fire(self, dt: float) -> None:
        self.auto_fire_timer = max(0.0, self.auto_fire_timer - dt)
        if not self.trigger_held:
            return

        while self.auto_fire_timer <= 0.0:
            if not self.shoot():
                break
            self.auto_fire_timer += SHOT_COOLDOWN

    def update_spawns(self, dt: float) -> None:
        spawn_girl, spawn_bear = self.spawner.update(dt)
        if spawn_girl:
            self.spawn_girl()
        if spawn_bear:
            self.spawn_bear()

    def update_entities(self, dt: float) -> None:
        for girl in self.girls:
            girl.update(dt)
        for bear in self.bears:
            bear.update(dt)

        # Bears grab girls when they catch up on the same lane.
        for bear in self.bears:
            if bear.dead or bear.grabbing:
                continue
            for girl in self.girls:
                if girl.saved or girl.captured:
                    continue
                if bear.lane.index != girl.lane.index:
                    continue
                if bear.progress >= girl.progress:
                    bear.grabbing = True
                    bear.target_girl = girl
                    girl.captured = True
                    girl.capture_bear = bear
                    break

        # If a grabbing bear dies, the captured girl is lost together with that event.
        remaining_girls: List[Girl] = []
        for girl in self.girls:
            if girl.saved:
                self.saved_girls += 1
                self.score += 50
                self.ammo += AMMO_REWARD
                continue
            if girl.captured and girl.capture_bear and girl.capture_bear.dead:
                continue
            remaining_girls.append(girl)
        self.girls = remaining_girls

        self.bears = [bear for bear in self.bears if (not bear.remove) and bear.progress <= 1.08]
        self.effects = [effect for effect in self.effects if effect.update(dt)]

        if any((not bear.dead) and bear.progress >= 1.0 for bear in self.bears):
            self.game_over = True
        if self.saved_girls >= GOAL_SAVED_GIRLS:
            self.victory = True

    def update(self, dt: float) -> None:
        self.gun.update(pygame.mouse.get_pos(), dt)
        if self.game_over or self.victory:
            return
        self.update_auto_fire(dt)
        self.update_spawns(dt)
        self.update_entities(dt)

    def draw_background(self) -> None:
        self.screen.fill(SKY_COLOR)
        pygame.draw.rect(self.screen, FIELD_COLOR, (0, HORIZON_Y, SCREEN_WIDTH, SCREEN_HEIGHT - HORIZON_Y))
        pygame.draw.rect(self.screen, FIELD_DARK, (0, PLAYER_Y + 30, SCREEN_WIDTH, SCREEN_HEIGHT - PLAYER_Y - 30))

        for lane in self.lanes:
            pygame.draw.line(
                self.screen,
                LANE_COLOR,
                (int(lane.horizon_x), HORIZON_Y),
                (int(lane.end_x), PLAYER_Y),
                2,
            )

        pygame.draw.line(self.screen, WHITE, (0, HORIZON_Y), (SCREEN_WIDTH, HORIZON_Y), 2)

    def draw_ui_panel(self, rect: pygame.Rect) -> None:
        panel = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        panel.fill(PANEL_COLOR)
        self.screen.blit(panel, rect.topleft)
        pygame.draw.rect(self.screen, WHITE, rect, 2)

    def draw_ui(self) -> None:
        panel_rect = pygame.Rect(14, 14, 320, 150)
        self.draw_ui_panel(panel_rect)

        ammo_text = self.font.render(f"Ammo: {self.ammo}", True, TEXT_COLOR)
        saved_text = self.font.render(f"Saved: {self.saved_girls}/{GOAL_SAVED_GIRLS}", True, TEXT_COLOR)
        score_text = self.font.render(f"Score: {self.score}", True, TEXT_COLOR)

        self.screen.blit(ammo_text, (28, 26))
        self.screen.blit(saved_text, (28, 60))
        self.screen.blit(score_text, (28, 94))

        bar_rect = pygame.Rect(28, 128, 280, 18)
        pygame.draw.rect(self.screen, BLACK, bar_rect)
        pygame.draw.rect(self.screen, WHITE, bar_rect, 2)
        fill = int(bar_rect.width * clamp(self.ammo / MAX_VISIBLE_AMMO, 0.0, 1.0))
        if fill > 0:
            pygame.draw.rect(self.screen, YELLOW, (bar_rect.x, bar_rect.y, fill, bar_rect.height))

        hint = self.small_font.render("Mouse = aim   Left click = shoot   R = restart", True, WHITE)
        self.screen.blit(hint, (SCREEN_WIDTH - 420, 20))

    def draw_overlay(self) -> None:
        if not self.game_over and not self.victory:
            return

        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0, 0))

        if self.victory:
            title = self.big_font.render("YOU SAVED 20 GIRLS", True, WHITE)
            subtitle = self.font.render("Press R to play again or ESC to quit", True, WHITE)
        else:
            title = self.big_font.render("GAME OVER", True, WHITE)
            subtitle = self.font.render("A bear reached the player. Press R to retry.", True, WHITE)

        self.screen.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 30)))
        self.screen.blit(subtitle, subtitle.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 28)))

    def draw(self) -> None:
        self.draw_background()

        drawables = []
        for girl in self.girls:
            drawables.append((girl.progress, 0, girl))
        for bear in self.bears:
            drawables.append((bear.progress, 1, bear))
        drawables.sort(key=lambda item: item[0])

        for _, kind, obj in drawables:
            obj.draw(self.screen)

        for effect in self.effects:
            effect.draw(self.screen)

        self.gun.draw(self.screen)
        self.draw_ui()
        self.draw_overlay()
        pygame.display.flip()

    def handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_r:
                    self.reset()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.trigger_held = True
                self.auto_fire_timer = 0.0
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                self.trigger_held = False
                self.auto_fire_timer = 0.0

    def run(self) -> None:
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            self.handle_events()
            self.update(dt)
            self.draw()

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    Game().run()
