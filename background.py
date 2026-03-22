import pygame

from settings import (
    FIELD_COLOR,
    FIELD_DARK,
    HORIZON_Y,
    LANE_COLOR,
    PLAYER_Y,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    SKY_COLOR,
    WHITE,
)


def draw_background(surface: pygame.Surface, lanes) -> None:
    surface.fill(SKY_COLOR)
    pygame.draw.rect(surface, FIELD_COLOR, (0, HORIZON_Y, SCREEN_WIDTH, SCREEN_HEIGHT - HORIZON_Y))
    pygame.draw.rect(surface, FIELD_DARK, (0, PLAYER_Y + 30, SCREEN_WIDTH, SCREEN_HEIGHT - PLAYER_Y - 30))

    for lane in lanes:
        pygame.draw.line(
            surface,
            LANE_COLOR,
            (int(lane.start_x), int(lane.start_y)),
            (int(lane.end_x), int(lane.end_y)),
            2,
        )

    pygame.draw.line(surface, WHITE, (0, HORIZON_Y), (SCREEN_WIDTH, HORIZON_Y), 2)
