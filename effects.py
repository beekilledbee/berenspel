import pygame

from settings import BLOOD_COLOR, RED


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