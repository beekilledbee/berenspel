from dataclasses import dataclass


@dataclass
class Weapon:
    name: str
    damage: int
    fire_rate: float      # shots per second
    max_ammo: int
    ammo: int
    pellets: int = 1      # projectiles per shot
    spread: float = 0.0   # radians spread angle (per pellet)
    projectile_speed: float = 0.0  # 0 = hitscan, >0 = travel speed (pixels/sec)
    explosion_radius: float = 0.0  # area of effect radius
    barrel_length: int = 84
    barrel_width: int = 12
    barrel_color: tuple = (35, 35, 35)
    flash_color: tuple = (255, 220, 80)
    key_hint: str = ""

    def can_shoot(self) -> bool:
        return self.ammo > 0

    def consume_ammo(self) -> None:
        self.ammo = max(0, self.ammo - 1)

    def add_ammo(self, amount: int) -> None:
        self.ammo = min(self.max_ammo, self.ammo + amount)


def create_weapons() -> list[Weapon]:
    return [
        Weapon(
            name="Pistol",
            damage=1,
            fire_rate=5.0,
            max_ammo=100,
            ammo=100,
            pellets=1,
            barrel_length=70,
            barrel_width=8,
            barrel_color=(35, 35, 35),
            key_hint="1",
        ),
        Weapon(
            name="Shotgun",
            damage=1,
            fire_rate=1.5,
            max_ammo=30,
            ammo=30,
            pellets=6,
            spread=0.12,
            barrel_length=90,
            barrel_width=14,
            barrel_color=(60, 50, 40),
            key_hint="2",
        ),
        Weapon(
            name="Rifle",
            damage=2,
            fire_rate=2.0,
            max_ammo=50,
            ammo=50,
            pellets=1,
            barrel_length=100,
            barrel_width=10,
            barrel_color=(50, 50, 55),
            key_hint="3",
        ),
        Weapon(
            name="RPG",
            damage=3,
            fire_rate=0.5,
            max_ammo=10,
            ammo=10,
            pellets=1,
            projectile_speed=800.0,
            explosion_radius=80.0,
            barrel_length=80,
            barrel_width=18,
            barrel_color=(70, 80, 50),
            flash_color=(255, 140, 40),
            key_hint="4",
        ),
    ]
