import pygame


class SoundManager:
    def __init__(self):
        pygame.mixer.init()

        self.sounds = {
            "pistol":       pygame.mixer.Sound("assets/sounds/rifleshooting.mp3"),
            "shotgun":      pygame.mixer.Sound("assets/sounds/Shotgun.mp3"),
            "rifle":        pygame.mixer.Sound("assets/sounds/machinegun2.mp3"),
            "rpg":          pygame.mixer.Sound("assets/sounds/shotgun2.mp3"),
            "monster_dead": pygame.mixer.Sound("assets/sounds/Monsterdead.mp3"),
            "boat_saved":   pygame.mixer.Sound("assets/sounds/Boatsave.wav"),
            "boat_sunk":    pygame.mixer.Sound("assets/sounds/Boatsink.mp3"),
            "game_over":    pygame.mixer.Sound("assets/sounds/Gamelost.mp3"),
            "victory":      pygame.mixer.Sound("assets/sounds/Victory.mp3"),
        }

        self.sounds["pistol"].set_volume(0.15)
        self.sounds["shotgun"].set_volume(0.6)
        self.sounds["rifle"].set_volume(0.4)
        self.sounds["rpg"].set_volume(0.3)
        self.sounds["boat_saved"].set_volume(0.8)
        self.sounds["boat_sunk"].set_volume(0.8)


        self.bgm_path = "assets/sounds/Oceanwaves.mp3"

    def play(self, name: str) -> None:
        if name in self.sounds:
            self.sounds[name].play()

    def play_bgm(self) -> None:
        pygame.mixer.music.load(self.bgm_path)
        pygame.mixer.music.play(-1)  

    def stop_bgm(self) -> None:
        pygame.mixer.music.stop()

    def play_bgm(self) -> None:
        pygame.mixer.music.load(self.bgm_path)
        pygame.mixer.music.set_volume(0.7)  
        pygame.mixer.music.play(-1)