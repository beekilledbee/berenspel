import pygame
import pytmx


class TileMap:
    def __init__(self, filename: str):
        self.tmx_data = pytmx.load_pygame(filename)
        self.tile_width = self.tmx_data.tilewidth
        self.tile_height = self.tmx_data.tileheight

        # Foam animation settings
        self.foam_frame_width = 192
        self.foam_frame_height = 192
        self.foam_frame_count = 16
        self.foam_frame_duration = 100  # ms per frame

        self.foam_frames = self.load_foam_frames("assets/Water Foam.png")

    def load_foam_frames(self, filename: str) -> list[pygame.Surface]:
        sheet = pygame.image.load(filename).convert_alpha()
        frames = []

        for i in range(self.foam_frame_count):
            frame = pygame.Surface(
                (self.foam_frame_width, self.foam_frame_height),
                pygame.SRCALPHA
            )
            frame.blit(
                sheet,
                (0, 0),
                pygame.Rect(
                    i * self.foam_frame_width,
                    0,
                    self.foam_frame_width,
                    self.foam_frame_height
                )
            )
            frames.append(frame)

        return frames

    def get_current_foam_frame(self) -> pygame.Surface:
        current_time = pygame.time.get_ticks()
        frame_index = (current_time // self.foam_frame_duration) % self.foam_frame_count
        return self.foam_frames[frame_index]

    def draw(self, surface: pygame.Surface) -> None:
        current_foam_frame = self.get_current_foam_frame()

        for layer in self.tmx_data.visible_layers:
            if isinstance(layer, pytmx.TiledTileLayer):
                for x, y, gid in layer:
                    if gid == 0:
                        continue

                    draw_x = x * self.tile_width
                    draw_y = y * self.tile_height

                    if layer.name == "foam":
                        tile = current_foam_frame
                        draw_x -= 64
                        draw_y -= 64
                    else:
                        tile = self.tmx_data.get_tile_image_by_gid(gid)

                    if tile is not None:
                        surface.blit(tile, (draw_x, draw_y))