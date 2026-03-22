import math
import random
import sys
import json
import datetime
from pathlib import Path
from typing import List

import pygame

from effects import BloodEffect
from entities import SeaMonster, Boat, Lane, PlayerGun, Projectile, create_weapons
from sound import SoundManager
from ui import (
    draw_cursor,
    draw_main_menu,
    draw_overlay,
    draw_pause_menu,
    draw_scoreboard,
    draw_ui,
    draw_weapon_selector,
    format_elapsed_time,
    get_main_menu_buttons,
    get_pause_menu_buttons,
    get_scoreboard_back_button,
)
from spawning import SpawnDirector
from background import draw_background
from tilemap import TileMap
from settings import (
    AMMO_REWARD,
    FPS,
    GOAL_SAVED_GIRLS,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
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
        pygame.mouse.set_visible(True)

        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("arial", 28)
        self.small_font = pygame.font.SysFont("arial", 22)
        self.big_font = pygame.font.SysFont("arial", 56, bold=True)
        self.running = True
        self.screen_state = "menu"
        self.scoreboard_path = Path(__file__).resolve().parent / "scoreboard.json"
        self.scoreboard_entries = self.load_scoreboard()

        self.sound_manager = SoundManager()

        self.reset()

    def reset(self) -> None:
        self.lanes = self.create_lanes()
        self.gun = PlayerGun()
        self.spawner = SpawnDirector(self.lanes)

        self.weapons = create_weapons()
        self.current_weapon_index = 0
        self.gun.weapon = self.current_weapon

        self.boats: List[Boat] = []
        self.monsters: List[SeaMonster] = []
        self.effects: List[BloodEffect] = []
        self.projectiles: List[Projectile] = []

        self.saved_boats = 0
        self.score = 0
        self.enemies_killed = 0
        self.run_time = 0.0
        self.trigger_held = False
        self.auto_fire_timer = 0.0

        self.game_over = False
        self.victory = False
        self.result_recorded = False

    @property
    def current_weapon(self):
        return self.weapons[self.current_weapon_index]

    @property
    def ammo(self):
        return self.current_weapon.ammo

    def switch_weapon(self, index: int) -> None:
        if 0 <= index < len(self.weapons):
            self.current_weapon_index = index
            self.gun.weapon = self.current_weapon
            self.trigger_held = False
            self.auto_fire_timer = 0.0

    def load_scoreboard(self) -> list[dict[str, int | str]]:
        if not self.scoreboard_path.exists():
            return []

        try:
            with self.scoreboard_path.open("r", encoding="utf-8") as scoreboard_file:
                data = json.load(scoreboard_file)
        except (OSError, json.JSONDecodeError):
            return []

        if not isinstance(data, list):
            return []

        entries: list[dict[str, int | str]] = []
        for item in data:
            if not isinstance(item, dict):
                continue
            time_to_finish = item.get("time_to_finish")
            enemies_killed = item.get("enemies_killed")
            result = item.get("result", "Victory")
            date = item.get("date")
            if (
                isinstance(time_to_finish, str)
                and isinstance(enemies_killed, int)
                and isinstance(result, str)
                and isinstance(date, str )
            ):
                entries.append(
                    {
                        "time_to_finish": time_to_finish,
                        "enemies_killed": enemies_killed,
                        "result": result,
                        "date": date
                    }
                )
        return entries

    def save_scoreboard(self) -> None:
        with self.scoreboard_path.open("w", encoding="utf-8") as scoreboard_file:
            json.dump(self.scoreboard_entries[:20], scoreboard_file, indent=2)

    def record_result(self, result: str) -> None:
        if self.result_recorded:
            return

        self.scoreboard_entries.insert(
            0,
            {
                "time_to_finish": format_elapsed_time(self.run_time),
                "enemies_killed": self.enemies_killed,
                "result": result,
                "date": str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
            },
        )
        self.save_scoreboard()
        self.result_recorded = True

    def start_game(self) -> None:
        self.reset()
        self.screen_state = "game"
        pygame.mouse.set_visible(False)
        self.sound_manager.play_bgm()

    def pause_game(self) -> None:
        self.trigger_held = False
        self.auto_fire_timer = 0.0
        self.screen_state = "pause"
        pygame.mouse.set_visible(True)

    def resume_game(self) -> None:
        self.trigger_held = False
        self.auto_fire_timer = 0.0
        self.screen_state = "game"
        pygame.mouse.set_visible(False)

    def show_main_menu(self) -> None:
        self.trigger_held = False
        self.auto_fire_timer = 0.0
        self.screen_state = "menu"
        pygame.mouse.set_visible(True)
        self.sound_manager.stop_bgm()

    def show_scoreboard(self) -> None:
        self.trigger_held = False
        self.auto_fire_timer = 0.0
        self.screen_state = "scoreboard"
        pygame.mouse.set_visible(True)

    def quit_game(self) -> None:
        self.running = False

    def get_virtual_mouse_pos(self) -> tuple[float, float]:
        mouse_x, mouse_y = pygame.mouse.get_pos()
        return (
            mouse_x * SCREEN_WIDTH / self.monitor_width,
            mouse_y * SCREEN_HEIGHT / self.monitor_height,
        )

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
        max_target_progress = 0.45

        candidates = [
            b for b in self.boats
            if not b.saved and not b.captured and b.progress <= max_target_progress
        ]
        if not candidates:
            return

        target = max(candidates, key=lambda b: b.progress)
        speed = random.uniform(0.18, 0.24)

        monster = SeaMonster(target.lane, speed)
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

        weapon = self.current_weapon
        if not weapon.can_shoot():
            return False

        weapon.consume_ammo()
        self.gun.shoot()

        weapon_names = ["pistol", "shotgun", "rifle", "rpg"]
        self.sound_manager.play(weapon_names[self.current_weapon_index])

        if weapon.projectile_speed > 0:
            # RPG: spawn a projectile
            mx, my = self.gun.muzzle_position()
            self.projectiles.append(
                Projectile(mx, my, self.gun.angle, weapon.projectile_speed,
                           weapon.damage, weapon.explosion_radius)
            )
        else:
            # Hitscan weapons (pistol, rifle, shotgun)
            original_angle = self.gun.angle
            for _ in range(weapon.pellets):
                if weapon.spread > 0:
                    self.gun.angle = original_angle + random.uniform(-weapon.spread, weapon.spread)

                for monster in self.monsters:
                    if monster.dead:
                        continue
                    if self.ray_hits_bear(monster):
                        x, y, _ = monster.get_draw_data()
                        self.effects.append(BloodEffect(x, y))
                        monster.hit(weapon.damage)
                        if monster.dead:
                            self.score += 100
                            self.enemies_killed += 1
                            self.sound_manager.play("monster_dead")

            self.gun.angle = original_angle

        return True

    def update_auto_fire(self, dt: float) -> None:
        self.auto_fire_timer = max(0.0, self.auto_fire_timer - dt)
        if not self.trigger_held:
            return

        shot_cooldown = 1.0 / self.current_weapon.fire_rate
        while self.auto_fire_timer <= 0.0:
            if not self.shoot():
                break
            self.auto_fire_timer += shot_cooldown

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

            if monster.dead:
                continue

            if not monster.has_valid_target():
                candidates = [
                    b for b in self.boats
                    if b.lane.index == monster.lane.index and not b.saved and not b.captured
                ]
                if candidates:
                    monster.target_boat = max(candidates, key=lambda b: b.progress)
                else:
                    monster.target_boat = None

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
                self.record_result("Failed")
                self.sound_manager.play("game_over")
                self.sound_manager.stop_bgm()
                return

        for monster in self.monsters:
            if monster.dead or not monster.has_valid_target():
                continue

            boat = monster.target_boat
            if monster.progress >= boat.progress:
                boat.captured = True
                monster.target_boat = None

        remaining_boats: List[Boat] = []
        for boat in self.boats:
            if boat.saved:
                self.saved_boats += 1
                self.score += 50
                self.sound_manager.play("boat_saved")
                for weapon in self.weapons:
                    weapon.add_ammo(AMMO_REWARD)
                continue
            if boat.captured:
                self.sound_manager.play("boat_sunk")
                continue
            remaining_boats.append(boat)
        self.boats = remaining_boats

        # Update projectiles and check collisions
        for proj in self.projectiles:
            if proj.exploding:
                continue
            hit_something = False
            # Check collision with monsters
            for monster in self.monsters:
                if monster.dead:
                    continue
                mx, my, size = monster.get_draw_data()
                dist = math.hypot(proj.x - mx, proj.y - my)
                if dist <= size * 0.5:
                    hit_something = True
                    break
            # Check collision with boats
            if not hit_something:
                for boat in self.boats:
                    if boat.saved or boat.captured:
                        continue
                    bx, by, bsize = boat.get_draw_data()
                    dist = math.hypot(proj.x - bx, proj.y - by)
                    if dist <= bsize * 0.6:
                        hit_something = True
                        break
            # Check collision with land (only after projectile has crossed water)
            on_land = self.tilemap.is_land_at_pixel(proj.x, proj.y)
            if not on_land:
                proj.crossed_water = True
            if not hit_something and proj.crossed_water and on_land:
                hit_something = True
            if hit_something:
                proj.explode()
                # Area of effect damage to monsters
                for monster in self.monsters:
                    if monster.dead:
                        continue
                    mx, my, size = monster.get_draw_data()
                    dist = math.hypot(proj.x - mx, proj.y - my)
                    if dist <= proj.explosion_radius:
                        self.effects.append(BloodEffect(mx, my))
                        monster.hit(proj.damage)
                        if monster.dead:
                            self.score += 100
                            self.enemies_killed += 1
                            self.sound_manager.play("monster_dead")

        self.projectiles = [p for p in self.projectiles if p.update(dt)]
        self.monsters = [m for m in self.monsters if (not m.remove) and m.progress <= 1.08]
        self.effects = [effect for effect in self.effects if effect.update(dt)]

        if self.saved_boats >= GOAL_SAVED_GIRLS:
            self.victory = True
            self.record_result("Victory")
            self.sound_manager.play("victory")
            self.sound_manager.stop_bgm()

    def update(self, dt: float) -> None:
        if self.screen_state != "game":
            return

        virtual_mouse_x, virtual_mouse_y = self.get_virtual_mouse_pos()

        self.gun.update((virtual_mouse_x, virtual_mouse_y), dt)
        if self.game_over or self.victory:
            return
        self.run_time += dt
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

        if self.screen_state == "menu":
            draw_main_menu(self.game_surface, self)
        elif self.screen_state == "scoreboard":
            draw_scoreboard(self.game_surface, self)
        else:
            for _, _, obj in self.get_sorted_drawables():
                obj.draw(self.game_surface)

            for proj in self.projectiles:
                proj.draw(self.game_surface)

            for effect in self.effects:
                effect.draw(self.game_surface)

            self.gun.draw(self.game_surface)
            draw_ui(self.game_surface, self)
            draw_weapon_selector(self.game_surface, self)
            draw_overlay(self.game_surface, self)
            if self.screen_state == "pause":
                draw_pause_menu(self.game_surface, self)

        if self.screen_state == "game":
            draw_cursor(self.game_surface, self)

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
                    if self.screen_state == "menu":
                        self.quit_game()
                    elif self.screen_state == "pause":
                        self.resume_game()
                    elif self.screen_state == "game" and not (self.game_over or self.victory):
                        self.pause_game()
                    else:
                        self.show_main_menu()
                elif self.screen_state == "menu" and event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    self.start_game()
                elif self.screen_state == "game" and event.key == pygame.K_r:
                    self.reset()
                elif self.screen_state == "game" and event.key in (pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4):
                    self.switch_weapon(event.key - pygame.K_1)
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.screen_state == "menu":
                    self.handle_menu_click()
                elif self.screen_state == "scoreboard":
                    self.handle_scoreboard_click()
                elif self.screen_state == "pause":
                    self.handle_pause_menu_click()
                else:
                    self.trigger_held = True
                    self.auto_fire_timer = 0.0
            elif self.screen_state == "game" and event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                self.trigger_held = False
                self.auto_fire_timer = 0.0
            elif self.screen_state == "game" and event.type == pygame.MOUSEBUTTONDOWN and event.button == 4:
                self.switch_weapon((self.current_weapon_index - 1) % len(self.weapons))
            elif self.screen_state == "game" and event.type == pygame.MOUSEBUTTONDOWN and event.button == 5:
                self.switch_weapon((self.current_weapon_index + 1) % len(self.weapons))

    def handle_menu_click(self) -> None:
        mouse_pos = self.get_virtual_mouse_pos()
        for button_name, rect in get_main_menu_buttons().items():
            if not rect.collidepoint(mouse_pos):
                continue
            if button_name == "start":
                self.start_game()
            elif button_name == "scoreboard":
                self.show_scoreboard()
            elif button_name == "quit":
                self.quit_game()
            return

    def handle_scoreboard_click(self) -> None:
        if get_scoreboard_back_button().collidepoint(self.get_virtual_mouse_pos()):
            self.show_main_menu()

    def handle_pause_menu_click(self) -> None:
        mouse_pos = self.get_virtual_mouse_pos()
        for button_name, rect in get_pause_menu_buttons().items():
            if not rect.collidepoint(mouse_pos):
                continue
            if button_name == "continue":
                self.resume_game()
            elif button_name == "main_menu":
                self.show_main_menu()
            return

    def run(self) -> None:
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            self.handle_events()
            self.update(dt)
            self.draw()

        pygame.quit()
        sys.exit()