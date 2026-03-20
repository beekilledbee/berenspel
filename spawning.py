import random
from typing import List

from entities import Lane
from settings import BEAR_SPAWN_INTERVAL, GIRL_SPAWN_INTERVAL


class SpawnDirector:
    def __init__(self, lanes: List[Lane]):
        self.lanes = lanes
        self.girl_timer = 0.6
        self.bear_timer = 1.0

    def update(self, dt: float):
        spawn_girl = False
        spawn_bear = False

        self.girl_timer -= dt
        self.bear_timer -= dt

        if self.girl_timer <= 0:
            spawn_girl = True
            self.girl_timer = random.uniform(
                GIRL_SPAWN_INTERVAL - 0.4,
                GIRL_SPAWN_INTERVAL + 0.5,
            )

        if self.bear_timer <= 0:
            spawn_bear = True
            self.bear_timer = random.uniform(
                BEAR_SPAWN_INTERVAL - 0.2,
                BEAR_SPAWN_INTERVAL + 0.3,
            )

        return spawn_girl, spawn_bear