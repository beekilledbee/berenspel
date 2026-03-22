import pygame
from pathlib import Path

from settings import (
    BLACK,
    GOAL_SAVED_GIRLS,
    MAX_VISIBLE_AMMO,
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
    controls = game.small_font.render("Aim with mouse, hold left click to shoot, R to restart a run", True, WHITE)
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
    subtitle = game.small_font.render("Previous completed runs", True, TEXT_COLOR)
    surface.blit(title, title.get_rect(center=(panel_rect.centerx, panel_rect.y + 68)))
    surface.blit(subtitle, subtitle.get_rect(center=(panel_rect.centerx, panel_rect.y + 112)))

    header_y = panel_rect.y + 156
    time_header = game.small_font.render("Time to finish", True, YELLOW)
    kills_header = game.small_font.render("Enemies killed", True, YELLOW)
    surface.blit(time_header, (panel_rect.x + 90, header_y))
    surface.blit(kills_header, (panel_rect.x + 420, header_y))

    if game.scoreboard_entries:
        for index, entry in enumerate(game.scoreboard_entries[:6]):
            row_y = header_y + 46 + index * 34
            time_text = game.small_font.render(entry["time_to_finish"], True, WHITE)
            kills_text = game.small_font.render(str(entry["enemies_killed"]), True, WHITE)
            surface.blit(time_text, (panel_rect.x + 110, row_y))
            surface.blit(kills_text, (panel_rect.x + 475, row_y))
    else:
        empty_text = game.font.render("No completed runs yet.", True, WHITE)
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

    ammo_text = game.font.render(f"Ammo: {game.ammo}", True, TEXT_COLOR)
    saved_text = game.font.render(f"Saved: {game.saved_boats}/{GOAL_SAVED_GIRLS}", True, TEXT_COLOR)
    score_text = game.font.render(f"Score: {game.score}", True, TEXT_COLOR)

    surface.blit(ammo_text, (28, 26))
    surface.blit(saved_text, (28, 60))
    surface.blit(score_text, (28, 94))

    bar_rect = pygame.Rect(28, 128, 280, 18)
    pygame.draw.rect(surface, BLACK, bar_rect)
    pygame.draw.rect(surface, WHITE, bar_rect, 2)

    fill = int(bar_rect.width * clamp(game.ammo / MAX_VISIBLE_AMMO, 0.0, 1.0))
    if fill > 0:
        pygame.draw.rect(surface, YELLOW, (bar_rect.x, bar_rect.y, fill, bar_rect.height))

    hint = game.small_font.render("Mouse = aim   Left click = shoot   R = restart   ESC = pause", True, WHITE)
    surface.blit(hint, (SCREEN_WIDTH - 420, 20))


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
