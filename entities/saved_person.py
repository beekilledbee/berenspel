import random
import pygame

from settings import SKIN_COLOR

CLOTHES = [
    (220, 120, 170),
    (120, 170, 230),
    (230, 190, 90),
    (140, 220, 140),
    (210, 140, 90),
]


class SavedPerson:
    def __init__(self, x: float, y: float):
        self.x = x + random.uniform(-16, 16)
        self.y = y + random.uniform(-10, 10)
        self.color = random.choice(CLOTHES)
        self.size = random.randint(18, 24)

    def draw(self, screen: pygame.Surface) -> None:
        head_radius = max(5, self.size // 4)
        body_w = int(self.size * 0.7)
        body_h = int(self.size * 1.0)

        pygame.draw.circle(
            screen,
            SKIN_COLOR,
            (int(self.x), int(self.y - body_h * 0.45)),
            head_radius
        )

        body_rect = pygame.Rect(0, 0, body_w, body_h)
        body_rect.center = (int(self.x), int(self.y))
        pygame.draw.ellipse(screen, self.color, body_rect)