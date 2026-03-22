import random
import pygame


class SavedPerson:
    SPRITE_OPTIONS = [
        ("assets/saved_people/Archer_Idle_red.png", 6),
        ("assets/saved_people/Pawn_Idle_blue.png", 8),
        ("assets/saved_people/Pawn_Idle_yellow.png", 8),
        ("assets/saved_people/Monk_Idle_red.png", 6),
        ("assets/saved_people/Warrior_Idle_black.png", 8),
    ]

    FRAME_WIDTH = 192
    FRAME_HEIGHT = 192

    _cache = {}

    def __init__(self, x: float, y: float):
        self.x = x + random.uniform(-18, 18)
        self.y = y + random.uniform(-12, 12)

        sprite_path, frame_count = random.choice(self.SPRITE_OPTIONS)
        self.frames = self.load_frames(sprite_path, frame_count)
        self.frame_count = frame_count

        self.anim_speed = 0.12
        self.anim_offset = random.uniform(0, frame_count * self.anim_speed)

        self.scale = random.uniform(0.45, 0.6)

    def load_frames(cls, filename: str, frame_count: int) -> list[pygame.Surface]:
        key = (filename, frame_count)
        if key in cls._cache:
            return cls._cache[key]

        sheet = pygame.image.load(filename).convert_alpha()
        frames = []

        for i in range(frame_count):
            frame = pygame.Surface((cls.FRAME_WIDTH, cls.FRAME_HEIGHT), pygame.SRCALPHA)
            frame.blit(
                sheet,
                (0, 0),
                pygame.Rect(
                    i * cls.FRAME_WIDTH,
                    0,
                    cls.FRAME_WIDTH,
                    cls.FRAME_HEIGHT
                )
            )
            frames.append(frame)

        cls._cache[key] = frames
        return frames

    def draw(self, screen: pygame.Surface) -> None:
        t = pygame.time.get_ticks() / 1000.0
        frame_index = int((t + self.anim_offset) / self.anim_speed) % self.frame_count
        frame = self.frames[frame_index]

        draw_w = int(frame.get_width() * self.scale)
        draw_h = int(frame.get_height() * self.scale)
        frame_scaled = pygame.transform.scale(frame, (draw_w, draw_h))

        screen.blit(frame_scaled, (int(self.x - draw_w / 2), int(self.y - draw_h / 2)))