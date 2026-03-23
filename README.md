# Berenspel

Berenspel is a top-down arcade defense game built with `pygame`. You defend the shoreline against sea monsters while rescue boats try to reach land. The goal is to save enough boats before any monster reaches the island.

## Features

- Single-player mode from the main menu
- Multiple weapons with different fire rates and behavior
- Persistent local scoreboard stored in `scoreboard.json`
- Fullscreen presentation with mouse aiming and weapon switching

## Gameplay

You play as a shoreline defender. Boats travel toward safety while sea monsters spawn in the water and try to intercept them. You score points by killing monsters and by saving boats.

The match ends in one of two ways:

- Victory: save `20` boats
- Defeat: a sea monster reaches land

## Controls

- `Mouse`: aim
- `Left Mouse Button`: fire
- `Mouse Wheel`: switch weapon
- `1`, `2`, `3`, `4`: select weapon directly
- `R`: restart the current single-player run
- `ESC`: pause in single-player, or return/quit from menus

## Weapons

- `Pistol`: fast basic sidearm
- `Shotgun`: short-range spread weapon
- `Rifle`: slower, harder-hitting precision weapon
- `RPG`: explosive projectile weapon

## Installation

### Requirements

- Python 3.11 or newer recommended
- `pygame`
- `pytmx`

### Install dependencies

From the `berenspel` directory:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install pygame pytmx
```

If you prefer not to use a virtual environment, install the same packages into your system Python.

## Running the game

From the `berenspel` directory:

```bash
python3 main.py
```

This opens the game in fullscreen mode.

## Main menu

The main menu supports both solo play and multiplayer.

- press 'Start game' to start the game.
- Open `Scoreboard` to view recorded local runs


## Scoreboard

Single-player results are saved locally in `scoreboard.json`. The scoreboard stores:

- completion time
- enemies killed
- result
- date

## Project files

- `main.py`: game entry point
- `game.py`: main gameplay loop and client-side multiplayer integration
- `ui.py`: menu, HUD, pause menu, and scoreboard rendering
- `scoreboard.json`: saved local scores

## Notes

- The game currently expects to be started from the `berenspel` directory so relative asset paths resolve correctly
