import pygame
from pathlib import Path

from settings import (
    BLACK,
    GOAL_SAVED_GIRLS,

    PANEL_COLOR,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    TITLE,
    TEXT_COLOR,
    WHITE,
    YELLOW,
)

MENU_PANEL_SIZE = (1050, 420)
BUTTON_SIZE = (220, 54)
CURSOR_SIZE = (26, 26)
_CURSOR_SURFACE: pygame.Surface | None = None


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def format_elapsed_time(seconds: float) -> str:
    total_seconds = max(0, int(round(seconds)))
    minutes, remaining_seconds = divmod(total_seconds, 60)
    return f"{minutes:02d}:{remaining_seconds:02d}"


def get_cursor_surface() -> pygame.Surface | None:
    global _CURSOR_SURFACE

    if _CURSOR_SURFACE is not None:
        return _CURSOR_SURFACE

    cursor_path = Path(__file__).resolve().parent / "assets" / "reticle.png"
    try:
        cursor_image = pygame.image.load(str(cursor_path)).convert_alpha()
    except pygame.error:
        return None

    black_cursor = cursor_image.copy()
    black_cursor.fill((0, 0, 0, 255), special_flags=pygame.BLEND_RGBA_MULT)
    _CURSOR_SURFACE = pygame.transform.smoothscale(black_cursor, CURSOR_SIZE)
    return _CURSOR_SURFACE


def draw_cursor(surface: pygame.Surface, game) -> None:
    cursor_surface = get_cursor_surface()
    if cursor_surface is None:
        return

    mouse_x, mouse_y = game.get_virtual_mouse_pos()
    surface.blit(
        cursor_surface,
        (
            mouse_x - cursor_surface.get_width() // 2,
            mouse_y - cursor_surface.get_height() // 2,
        ),
    )


def draw_ui_panel(surface: pygame.Surface, rect: pygame.Rect) -> None:
    panel = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    panel.fill(PANEL_COLOR)
    surface.blit(panel, rect.topleft)
    pygame.draw.rect(surface, WHITE, rect, 2)


def get_menu_panel_rect() -> pygame.Rect:
    panel_rect = pygame.Rect((0, 0), MENU_PANEL_SIZE)
    panel_rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
    return panel_rect


def get_main_menu_buttons() -> dict[str, pygame.Rect]:
    start_button_x = 300
    start_button_y = 453

    scoreboard_button_x = 550
    scoreboard_button_y = 453

    quit_button_x = 800
    quit_button_y = 453

    return {
        "start": pygame.Rect(start_button_x, start_button_y, *BUTTON_SIZE),
        "scoreboard": pygame.Rect(scoreboard_button_x, scoreboard_button_y, *BUTTON_SIZE),
        "quit": pygame.Rect(quit_button_x, quit_button_y, *BUTTON_SIZE),
    }


def get_scoreboard_back_button() -> pygame.Rect:
    panel_rect = get_menu_panel_rect()
    return pygame.Rect(panel_rect.centerx - BUTTON_SIZE[0] // 2, panel_rect.bottom - 74, *BUTTON_SIZE)


def get_pause_menu_buttons() -> dict[str, pygame.Rect]:
    continue_button_x = SCREEN_WIDTH // 2 - BUTTON_SIZE[0] // 2
    continue_button_y = 360

    main_menu_button_x = SCREEN_WIDTH // 2 - BUTTON_SIZE[0] // 2
    main_menu_button_y = 440

    return {
        "continue": pygame.Rect(continue_button_x, continue_button_y, *BUTTON_SIZE),
        "main_menu": pygame.Rect(main_menu_button_x, main_menu_button_y, *BUTTON_SIZE),
    }


def draw_button(
    surface: pygame.Surface,
    rect: pygame.Rect,
    label: str,
    font: pygame.font.Font,
    hovered: bool,
) -> None:
    fill_color = YELLOW if hovered else (40, 40, 40)
    border_color = WHITE if hovered else (190, 190, 190)

    pygame.draw.rect(surface, fill_color, rect, border_radius=10)
    pygame.draw.rect(surface, border_color, rect, 2, border_radius=10)

    text = font.render(label, True, BLACK if hovered else WHITE)
    surface.blit(text, text.get_rect(center=rect.center))


def draw_main_menu(surface: pygame.Surface, game) -> None:
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 120))
    surface.blit(overlay, (0, 0))

    panel_rect = get_menu_panel_rect()
    draw_ui_panel(surface, panel_rect)

    title = game.big_font.render(TITLE, True, WHITE)
    subtitle = game.font.render("Rescue the boats before the sea monsters reach shore.", True, TEXT_COLOR)
    controls = game.small_font.render("Aim with mouse, LMB to shoot, 1-4 or scroll to switch weapon", True, WHITE)
    goal = game.small_font.render(f"Goal: save {GOAL_SAVED_GIRLS} boats.", True, WHITE)
    helper = game.small_font.render("Use the buttons below to start, view scores, or quit.", True, WHITE)

    surface.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, panel_rect.y + 78)))
    surface.blit(subtitle, subtitle.get_rect(center=(SCREEN_WIDTH // 2, panel_rect.y + 146)))
    surface.blit(goal, goal.get_rect(center=(SCREEN_WIDTH // 2, panel_rect.y + 212)))
    surface.blit(controls, controls.get_rect(center=(SCREEN_WIDTH // 2, panel_rect.y + 246)))
    surface.blit(helper, helper.get_rect(center=(SCREEN_WIDTH // 2, panel_rect.y + 274)))

    mouse_pos = game.get_virtual_mouse_pos()
    for button_name, rect in get_main_menu_buttons().items():
        draw_button(
            surface,
            rect,
            button_name.replace("_", " ").title(),
            game.font,
            rect.collidepoint(mouse_pos),
        )


def draw_scoreboard(surface: pygame.Surface, game) -> None:
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 150))
    surface.blit(overlay, (0, 0))

    panel_rect = get_menu_panel_rect()
    draw_ui_panel(surface, panel_rect)

    title = game.big_font.render("Scoreboard", True, WHITE)
    subtitle = game.small_font.render("Previous runs", True, TEXT_COLOR)
    surface.blit(title, title.get_rect(center=(panel_rect.centerx, panel_rect.y + 68)))
    surface.blit(subtitle, subtitle.get_rect(center=(panel_rect.centerx, panel_rect.y + 112)))

    header_y = panel_rect.y + 156
    result_header = game.small_font.render("Result", True, YELLOW)
    time_header = game.small_font.render("Time to finish", True, YELLOW)
    kills_header = game.small_font.render("Enemies killed", True, YELLOW)
    date_header = game.small_font.render("Date", True, YELLOW)
    surface.blit(result_header, (panel_rect.x + 40, header_y))
    surface.blit(time_header, (panel_rect.x + 150, header_y))
    surface.blit(kills_header, (panel_rect.x + 420, header_y))
    surface.blit(date_header, (panel_rect.x + 700, header_y))

    if game.scoreboard_entries:
        for index, entry in enumerate(game.scoreboard_entries[:6]):
            row_y = header_y + 46 + index * 34
            result_text = game.small_font.render(entry.get("result", "Victory"), True, WHITE)
            time_text = game.small_font.render(entry["time_to_finish"], True, WHITE)
            kills_text = game.small_font.render(str(entry["enemies_killed"]), True, WHITE)
            date_text = game.small_font.render(str(entry["date"]), True, WHITE)
            surface.blit(result_text, (panel_rect.x + 40, row_y))
            surface.blit(time_text, (panel_rect.x + 150, row_y))
            surface.blit(kills_text, (panel_rect.x + 420, row_y))
            surface.blit(date_text, (panel_rect.x + 700, row_y))
    else:
        empty_text = game.font.render("No runs recorded yet.", True, WHITE)
        surface.blit(empty_text, empty_text.get_rect(center=(panel_rect.centerx, panel_rect.centery)))

    back_button = get_scoreboard_back_button()
    draw_button(
        surface,
        back_button,
        "Back",
        game.font,
        back_button.collidepoint(game.get_virtual_mouse_pos()),
    )


def draw_pause_menu(surface: pygame.Surface, game) -> None:
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 170))
    surface.blit(overlay, (0, 0))

    panel_rect = pygame.Rect(0, 0, 650, 300)
    panel_rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
    draw_ui_panel(surface, panel_rect)

    title = game.big_font.render("Paused", True, WHITE)
    subtitle = game.font.render("Press ESC to continue or use the buttons below.", True, WHITE)
    surface.blit(title, title.get_rect(center=(panel_rect.centerx, panel_rect.y + 70)))
    surface.blit(subtitle, subtitle.get_rect(center=(panel_rect.centerx, panel_rect.y + 122)))

    mouse_pos = game.get_virtual_mouse_pos()
    for button_name, rect in get_pause_menu_buttons().items():
        draw_button(
            surface,
            rect,
            button_name.replace("_", " ").title(),
            game.font,
            rect.collidepoint(mouse_pos),
        )


def draw_ui(surface: pygame.Surface, game) -> None:
    panel_rect = pygame.Rect(14, 14, 320, 150)
    draw_ui_panel(surface, panel_rect)

    weapon = game.current_weapon
    ammo_text = game.font.render(f"{weapon.name}: {weapon.ammo}/{weapon.max_ammo}", True, TEXT_COLOR)
    saved_text = game.font.render(f"Saved: {game.saved_boats}/{GOAL_SAVED_GIRLS}", True, TEXT_COLOR)
    score_text = game.font.render(f"Score: {game.score}", True, TEXT_COLOR)

    surface.blit(ammo_text, (28, 26))
    surface.blit(saved_text, (28, 60))
    surface.blit(score_text, (28, 94))

    bar_rect = pygame.Rect(28, 128, 280, 18)
    pygame.draw.rect(surface, BLACK, bar_rect)
    pygame.draw.rect(surface, WHITE, bar_rect, 2)

    fill = int(bar_rect.width * clamp(weapon.ammo / weapon.max_ammo, 0.0, 1.0))
    if fill > 0:
        pygame.draw.rect(surface, YELLOW, (bar_rect.x, bar_rect.y, fill, bar_rect.height))

    hint = game.small_font.render("Mouse = aim   LMB = shoot   1-4/Scroll = weapon   R = restart", True, WHITE)
    surface.blit(hint, (SCREEN_WIDTH - 440, 20))


_WEAPON_NAME_FONT: pygame.font.Font | None = None
_WEAPON_SLOT_FONT: pygame.font.Font | None = None


def _get_weapon_name_font() -> pygame.font.Font:
    global _WEAPON_NAME_FONT
    if _WEAPON_NAME_FONT is None:
        _WEAPON_NAME_FONT = pygame.font.SysFont("arial", 36, bold=True)
    return _WEAPON_NAME_FONT


def _get_weapon_slot_font() -> pygame.font.Font:
    global _WEAPON_SLOT_FONT
    if _WEAPON_SLOT_FONT is None:
        _WEAPON_SLOT_FONT = pygame.font.SysFont("arial", 14)
    return _WEAPON_SLOT_FONT


WEAPON_COLORS = {
    "Pistol": (200, 200, 200),
    "Shotgun": (180, 140, 80),
    "Rifle": (130, 180, 255),
    "RPG": (255, 140, 60),
}


def draw_weapon_selector(surface: pygame.Surface, game) -> None:
    weapons = game.weapons
    active_index = game.current_weapon_index
    active_weapon = weapons[active_index]

    # Large active weapon name display (top-right area below hints)
    name_font = _get_weapon_name_font()
    weapon_color = WEAPON_COLORS.get(active_weapon.name, WHITE)
    name_text = name_font.render(active_weapon.name.upper(), True, weapon_color)
    name_rect = name_text.get_rect(right=SCREEN_WIDTH - 20, top=46)

    # Background for weapon name
    name_bg = pygame.Surface((name_rect.width + 16, name_rect.height + 8), pygame.SRCALPHA)
    name_bg.fill((0, 0, 0, 100))
    surface.blit(name_bg, (name_rect.x - 8, name_rect.y - 4))
    surface.blit(name_text, name_rect)

    # Bottom weapon selector bar
    slot_width = 90
    slot_height = 56
    gap = 6
    selector_width = len(weapons) * (slot_width + gap) - gap + 20
    start_x = (SCREEN_WIDTH - selector_width) // 2
    y = SCREEN_HEIGHT - slot_height - 14

    panel = pygame.Surface((selector_width, slot_height + 8), pygame.SRCALPHA)
    panel.fill(PANEL_COLOR)
    surface.blit(panel, (start_x, y))
    pygame.draw.rect(surface, WHITE, (start_x, y, selector_width, slot_height + 8), 2)

    slot_font = _get_weapon_slot_font()

    for i, weapon in enumerate(weapons):
        box_x = start_x + 10 + i * (slot_width + gap)
        box_rect = pygame.Rect(box_x, y + 4, slot_width, slot_height)
        w_color = WEAPON_COLORS.get(weapon.name, WHITE)

        if i == active_index:
            # Active weapon: highlighted with weapon color border
            pygame.draw.rect(surface, (30, 30, 30), box_rect, border_radius=6)
            pygame.draw.rect(surface, w_color, box_rect, 3, border_radius=6)
            text_color = WHITE
        else:
            pygame.draw.rect(surface, (40, 40, 40), box_rect, border_radius=6)
            pygame.draw.rect(surface, (80, 80, 80), box_rect, 1, border_radius=6)
            text_color = (160, 160, 160)

        # Key hint (top-left corner)
        key_text = slot_font.render(weapon.key_hint, True, w_color if i == active_index else (120, 120, 120))
        surface.blit(key_text, (box_rect.x + 5, box_rect.y + 2))

        # Weapon name
        name_text = slot_font.render(weapon.name, True, text_color)
        surface.blit(name_text, name_text.get_rect(centerx=box_rect.centerx, top=box_rect.y + 4))

        # Ammo count
        ammo_str = f"{weapon.ammo}"
        ammo_text = slot_font.render(ammo_str, True, text_color)
        surface.blit(ammo_text, ammo_text.get_rect(centerx=box_rect.centerx, top=box_rect.y + 22))

        # Mini ammo bar
        bar_rect = pygame.Rect(box_rect.x + 6, box_rect.bottom - 10, box_rect.width - 12, 5)
        pygame.draw.rect(surface, (20, 20, 20), bar_rect)
        fill_ratio = weapon.ammo / weapon.max_ammo if weapon.max_ammo > 0 else 0
        fill_w = int(bar_rect.width * clamp(fill_ratio, 0.0, 1.0))
        if fill_w > 0:
            bar_color = w_color if i == active_index else (100, 100, 100)
            pygame.draw.rect(surface, bar_color, (bar_rect.x, bar_rect.y, fill_w, bar_rect.height))


def draw_overlay(surface: pygame.Surface, game) -> None:
    if not game.game_over and not game.victory:
        return

    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 150))
    surface.blit(overlay, (0, 0))

    if game.victory:
        title = game.big_font.render(f"YOU SAVED {game.saved_boats}/{GOAL_SAVED_GIRLS} BOATS", True, WHITE)
        subtitle = game.font.render("Press R to play again or ESC to return to the menu", True, WHITE)
    else:
        title = game.big_font.render("GAME OVER", True, WHITE)
        subtitle = game.font.render("A sea monster reached the island. Press R to retry or ESC for menu.", True, WHITE)

    surface.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 30)))
    surface.blit(subtitle, subtitle.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 28)))
