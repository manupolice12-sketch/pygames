# PyGame-S — PyGame Simplified

PyGame-S is a beginner-friendly wrapper around [Pygame](https://www.pygame.org/) that simplifies game development without limiting what you can build. Write less boilerplate, focus more on your game.

---

## Installation

```bash
pip install pygames-simplified
```

### Importing

```python
from pygames.advanced import Player, Animator, PhysicSprite, Game  # Physics + Player + Animator (recommended)
from pygames.medium import PhysicSprite, Game                       # Physics only (no player input)
```

---

## Quick Start

```python
from pygames.advanced import Player, Game
from pygames.pygames_engine.utils.object_manager import SSprites
import pygame

game = Game(800, 600, "My Game")

player = Player(game, 100, 300)
ground = SSprites(game, 0, 550, source=pygame.Surface((800, 50)))
ground.image.fill("green")

game.start(player)
game.make_solid(ground)

def logic():
    game.background("skyblue")
    player.tick()

game.mainloop(logic)
```

---

## Complexity Tiers

| Import | What you get |
|---|---|
| `from pygames.medium import ...` | Core engine + physics (no player input) |
| `from pygames.advanced import ...` | Core engine + physics + controllable player + Animator |

---

## Core — `Game`

```python
game = Game(w=800, h=600, title="My Game", icon_path=None)
```

| Method | Description |
|---|---|
| `game.background(color)` | Fill the screen with a color each frame |
| `game.start(*objects)` | Register objects to be drawn and updated |
| `game.make_solid(*objects)` | Mark objects as collidable |
| `game.check_key_pressed(name)` | Check if a key is held — e.g. `"left"`, `"space"`, `"w"` |
| `game.start_score_counter()` | Display score automatically each frame |
| `game.show_score(x, y, color)` | Manually draw the score at a given position |
| `game.score` | Set or read the current score value |
| `game.start_garbage_collector()` | Auto-remove objects that move off-screen |
| `game.load_image(name, path)` | Load an image by name |
| `game.img(name, x, y, w, h)` | Draw a loaded image (scaled copies are cached) |
| `game.load_sound(name, path)` | Load a sound by name |
| `game.play_sound(name)` | Play a loaded sound |
| `game.set_speed(fps)` | Set target FPS (default 60) |
| `game.zoom(factor)` | Resize the window by a multiplier |
| `game.mainloop(logic)` | Start the game loop |
| `game.create_surface(w, h, color, alpha)` | Create a pygame Surface |
| `game.enable_logging(log_path)` | Enable debug logging to a file |
| `game.disable_logging()` | Disable logging |
| `game._log(message, status)` | Write a log entry (INFO / SUCCESS / ERROR) |

> **Note:** `game.zoom(factor)` is discouraged when PhysicSprites are in use — it resizes the window but does not rescale object positions or physics constants.

> **Note:** `game.start_garbage_collecter()` (old spelling) still works as an alias but is deprecated — prefer `start_garbage_collector()`.

---

## Base Sprite — `SSprites`

```python
obj = SSprites(game, x, y, image_path=None, source=None)
```

The base class for all game objects. Accepts an image path, a raw `Surface`, or defaults to a white square.

| Method | Description |
|---|---|
| `obj.draw()` | Draw the object to the screen |
| `obj.move(dx, dy)` | Move the object by an offset |

---

## Physics — `PhysicSprite`

```python
obj = PhysicSprite(game, x, y, width=50, height=50, color="red")
```

Extends `SSprites` with gravity, velocity, and collision detection.

| Attribute | Description |
|---|---|
| `obj.vel_x` | Horizontal velocity (pixels per frame) |
| `obj.vel_y` | Vertical velocity (pixels per frame) |
| `obj.gravity` | Gravity acceleration per frame (default `0.8`) |
| `obj.max_fall_speed` | Terminal velocity cap (default `20`) |
| `obj.on_ground` | `True` when standing on a solid or the screen floor |

| Method | Description |
|---|---|
| `obj.apply_physics(solids)` | Apply gravity and resolve collisions — called automatically each frame |
| `obj.jump(force=15)` | Jump if currently on the ground |

Vertical and horizontal collisions are resolved in separate passes, which prevents corner-clipping on platform edges.

---

## Player — `Player`

```python
player = Player(game, x, y, width=40, height=60, color="blue", speed=5,
                left="left", right="right", jump="space")
```

Extends `PhysicSprite` with keyboard input. All key bindings are customisable.

| Method | Description |
|---|---|
| `player.tick()` | Process input and update state — call once per frame in your logic function |
| `player.handle_input()` | Reads left, right, and jump keys and sets velocity accordingly |

---

## Animation — `Animator`

```python
from pygames.advanced import Animator

anim = Animator(target, animation_speed=100)
```

Works with sprites that have a `.state` string and an `.animations` dict mapping state names to lists of `Surface` frames.

`animation_speed` is in **milliseconds** — `100` means frames advance every 100 ms (~10 fps).

| Method | Description |
|---|---|
| `anim.refresh()` | Advance the animation frame — call every tick |
| `anim.hover(amplitude=5, speed=0.005)` | Vertical sine-wave float effect |
| `anim.rotate_loop(speed=0.1)` | Continuous rotation (degrees per millisecond) |

> **Note:** `hover()` modifies `rect.y` directly. Do not use it on sprites that also have `apply_physics` running — the two will conflict.

---

## Supported Keys

Pass any of these strings to `game.check_key_pressed()` or as custom key bindings on `Player`:

`"left"`, `"right"`, `"up"`, `"down"`, `"space"`, `"esc"`, `"enter"`, `"shift"`, `"ctrl"`, `"tab"`, `"backspace"`, or any letter/number like `"a"`, `"w"`, `"1"`

---

## Error Handling

| Error | Cause |
|---|---|
| `FileNotFoundError` | Invalid path for image, sound, or icon |
| `TypeError` | Wrong type for width, height, speed, coordinates, or jump force |
| `ValueError` | Negative speed value |
| `NameError` | Invalid colour name or missing sound name |

---

## Logging

Pass `logging=True` to `Game()` or call `game.enable_logging()` at any time. A `logs.txt` file is created in the same directory as your main script. The path is printed to the terminal when the file is first created. Pass a custom path to `enable_logging(log_path)` to write the log elsewhere.

---

## Version

Current release: **v2.5.0**

Inspired by [Pygame Zero](https://pygame-zero.readthedocs.io/), built to be more Pythonic, flexible, and extensible.

## Links

- GitHub: https://github.com/manupolice12-sketch/pygames
- Bug Reports: https://github.com/manupolice12-sketch/pygames/issues
- PyPI: https://pypi.org/project/pygames-simplified/
