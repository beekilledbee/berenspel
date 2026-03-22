import pygame
import pytmx


class TileMap:
    def __init__(self, filename: str):
        self.tmx_data = pytmx.load_pygame(filename)
        self.tile_width = self.tmx_data.tilewidth
        self.tile_height = self.tmx_data.tileheight

        self.foam_frame_width = 192
        self.foam_frame_height = 192
        self.foam_frame_count = 12
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

    def get_foam_frame(self, x: int, y: int) -> pygame.Surface:
        current_time = pygame.time.get_ticks()
        global_frame = (current_time // self.foam_frame_duration) % self.foam_frame_count

        phase_offset = (x * 7 + y * 13) % self.foam_frame_count

        frame_index = (global_frame + phase_offset) % self.foam_frame_count
        return self.foam_frames[frame_index]

    def get_saved_people_points(self) -> list[tuple[float, float]]:
        points = []

        for layer in self.tmx_data.visible_layers:
            if isinstance(layer, pytmx.TiledObjectGroup) and layer.name == "savd peolpe":
                for obj in layer:
                    points.append((obj.x, obj.y))

        return points
    
    def is_land_at_pixel(self, px: float, py: float) -> bool:
        tile_x = int(px // self.tile_width)
        tile_y = int(py // self.tile_height)

        if not (0 <= tile_x < self.tmx_data.width and 0 <= tile_y < self.tmx_data.height):
            return False

        land_layers = {
            "flat ground",
            "flatground 2",
            "flat ground 3",
            "elevated ground",
            "elevated ground 2",
            "elevated ground 3",
            "elevated ground yellow",
        }

        for layer in self.tmx_data.visible_layers:
            if isinstance(layer, pytmx.TiledTileLayer) and layer.name in land_layers:
                gid = layer.data[tile_y][tile_x]
                if gid != 0:
                    return True

        return False

    def draw(self, surface: pygame.Surface) -> None:
        for layer in self.tmx_data.visible_layers:
            if isinstance(layer, pytmx.TiledTileLayer):
                for x, y, gid in layer:
                    if gid == 0:
                        continue

                    draw_x = x * self.tile_width
                    draw_y = y * self.tile_height

                    if layer.name in "foam":
                        tile = self.get_foam_frame(x, y)
                        draw_x -= 64
                        draw_y -= 64
                    else:
                        tile = self.tmx_data.get_tile_image_by_gid(gid)

                        if layer.name == "shadow":
                            draw_x -= 64
                            draw_y -= 64

                    if tile is not None:
                        surface.blit(tile, (draw_x, draw_y))