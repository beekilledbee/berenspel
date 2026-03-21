import pygame

from settings import (
    BLACK,
    GOAL_SAVED_GIRLS,
    MAX_VISIBLE_AMMO,
    PANEL_COLOR,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    TEXT_COLOR,
    WHITE,
    YELLOW,
)


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def draw_ui_panel(surface: pygame.Surface, rect: pygame.Rect) -> None:
    panel = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    panel.fill(PANEL_COLOR)
    surface.blit(panel, rect.topleft)
    pygame.draw.rect(surface, WHITE, rect, 2)


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

    hint = game.small_font.render("Mouse = aim   Left click = shoot   R = restart", True, WHITE)
    surface.blit(hint, (SCREEN_WIDTH - 420, 20))


def draw_overlay(surface: pygame.Surface, game) -> None:
    if not game.game_over and not game.victory:
        return

    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 150))
    surface.blit(overlay, (0, 0))

    if game.victory:
        title = game.big_font.render("YOU SAVED 20 GIRLS", True, WHITE)
        subtitle = game.font.render("Press R to play again or ESC to quit", True, WHITE)
    else:
        title = game.big_font.render("GAME OVER", True, WHITE)
        subtitle = game.font.render("A bear reached the player. Press R to retry.", True, WHITE)

    surface.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 30)))
    surface.blit(subtitle, subtitle.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 28)))