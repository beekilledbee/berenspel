import math
import random
import sys
from typing import List

import pygame

from effects import BloodEffect
from entities import Bear, Girl, Lane, PlayerGun, SpawnDirector, clamp
from settings import (
    AMMO_REWARD,
    BLACK,
    FIELD_COLOR,
    FIELD_DARK,
    FPS,
    GOAL_SAVED_GIRLS,
    HORIZON_Y,
    LANE_COLOR,
    MAX_VISIBLE_AMMO,
    PANEL_COLOR,
    PLAYER_Y,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    SHOT_COOLDOWN,
    SKY_COLOR,
    START_AMMO,
    TEXT_COLOR,
    TITLE,
    WHITE,
    YELLOW,
)


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

        for _, _, obj in drawables:
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