import math
import random
import sys
from typing import List

import pygame

from effects import BloodEffect
from entities import SeaMonster, Boat, Lane, PlayerGun
from ui import draw_overlay, draw_ui
from spawning import SpawnDirector
from background import draw_background
from tilemap import TileMap
from settings import (
    AMMO_REWARD,
    FPS,
    GOAL_SAVED_GIRLS,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    SHOT_COOLDOWN,
    START_AMMO,
    TITLE,
)

class Game:
    def __init__(self):
        pygame.init()

        display_info = pygame.display.Info()
        self.monitor_width = display_info.current_w
        self.monitor_height = display_info.current_h

        self.screen = pygame.display.set_mode(
            (self.monitor_width, self.monitor_height),
            pygame.FULLSCREEN
        )

        self.game_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.tilemap = TileMap("assets/map.tmx")
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

        self.boats: List[Boat] = []
        self.monsters: List[SeaMonster] = []
        self.effects: List[BloodEffect] = []

        self.saved_boats = 0
        self.score = 0
        self.ammo = START_AMMO
        self.trigger_held = False
        self.auto_fire_timer = 0.0

        self.game_over = False
        self.victory = False

    def create_lanes(self) -> List[Lane]:
        return [
            Lane(0, 320, 0, 300, 610),
            Lane(1, 470, 0, 470, 610),
            Lane(2, 640, 0, 640, 610),
            Lane(3, 810, 0, 815, 610),
            Lane(4, 980, 0, 990, 610),
        ]

    def spawn_boat(self) -> None:
        lane = random.choice(self.lanes)
        speed = random.uniform(0.12, 0.16)
        self.boats.append(Boat(lane, speed))

    def spawn_monster(self) -> None:
        lane = random.choice(self.lanes)
        speed = random.uniform(0.18, 0.24)
        monster = SeaMonster(lane, speed)

        candidates = [b for b in self.boats if b.lane == lane and not b.saved and not b.captured]
        if candidates:
            target = max(candidates, key=lambda g: g.progress)
            monster.target_boat = target

        self.monsters.append(monster)

    def ray_hits_bear(self, bear: SeaMonster) -> bool:
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

        for monster in self.monsters:
            if monster.dead:
                continue
            if self.ray_hits_bear(monster):
                x, y, _ = monster.get_draw_data()
                self.effects.append(BloodEffect(x, y))
                monster.hit()
                if monster.dead:
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
            self.spawn_boat()
        if spawn_bear:
            self.spawn_monster()

    def update_entities(self, dt: float) -> None:
        for boat in self.boats:
            boat.update(dt)
        for monster in self.monsters:
            monster.update(dt)

        for boat in self.boats:
            if boat.saved or boat.captured:
                continue

            x, y, size = boat.get_draw_data()
            foot_y = y + size * 0.35

            if self.tilemap.is_land_at_pixel(x, foot_y):
                boat.saved = True

        for monster in self.monsters:
            if monster.dead:
                continue

            x, y, size = monster.get_draw_data()
            foot_y = y + size * 0.35

            if self.tilemap.is_land_at_pixel(x, foot_y):
                self.game_over = True
                return

        for monster in self.monsters:
            if monster.dead or monster.grabbing:
                continue
            for boat in self.boats:
                if boat.saved or boat.captured:
                    continue
                if monster.lane.index != boat.lane.index:
                    continue
                if monster.progress >= boat.progress:
                    monster.grabbing = True
                    monster.target_boat = boat
                    boat.captured = True
                    boat.capture_monster = monster
                    break

        remaining_boats: List[Boat] = []
        for boat in self.boats:
            if boat.saved:
                self.saved_boats += 1
                self.score += 50
                self.ammo += AMMO_REWARD
                continue
            if boat.captured:
                continue
            remaining_boats.append(boat)
        self.boats = remaining_boats

        self.monsters = [m for m in self.monsters if (not m.remove) and m.progress <= 1.08]
        self.effects = [effect for effect in self.effects if effect.update(dt)]

        if self.saved_boats >= GOAL_SAVED_GIRLS:
            self.victory = True

    def update(self, dt: float) -> None:
        mouse_x, mouse_y = pygame.mouse.get_pos()

        virtual_mouse_x = mouse_x * SCREEN_WIDTH / self.monitor_width
        virtual_mouse_y = mouse_y * SCREEN_HEIGHT / self.monitor_height

        self.gun.update((virtual_mouse_x, virtual_mouse_y), dt)
        if self.game_over or self.victory:
            return
        self.update_auto_fire(dt)
        self.update_spawns(dt)
        self.update_entities(dt)

    def get_sorted_drawables(self):
        drawables = [(boat.progress, 0, boat) for boat in self.boats]
        drawables += [(monster.progress, 1, monster) for monster in self.monsters]
        drawables.sort(key=lambda item: item[0])
        return drawables

    def draw(self) -> None:
        self.game_surface.fill((0, 0, 0))
        self.tilemap.draw(self.game_surface)

        for _, _, obj in self.get_sorted_drawables():
            obj.draw(self.game_surface)

        for effect in self.effects:
            effect.draw(self.game_surface)

        self.gun.draw(self.game_surface)
        draw_ui(self.game_surface, self)
        draw_overlay(self.game_surface, self)

        scaled_surface = pygame.transform.smoothscale(
            self.game_surface,
            (self.monitor_width, self.monitor_height)
        )
        self.screen.blit(scaled_surface, (0, 0))
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