# PyGame-S — PyGame Simplified

PyGame-S is a beginner-friendly wrapper around [Pygame](https://www.pygame.org/) that simplifies game development without limiting what you can build. Write less boilerplate, focus more on your game.

---

## Installation

```bash
pip install pygames-simplified
```

### Importing

```python
from pygames.advanced import *   # Physics + Player + Animator(recommended)
from pygames.medium import *     # Physics only (no player input)
```

---

## Quick Start

```python
from pygames.advanced import *

game = Game(800, 600, "My Game")

player = Player(game, 100, 300)
ground = SSprites(game, 0, 550, source=Surface((800, 50)))
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
| `from pygames.medium import *` | Core engine + physics (no player input) |
| `from pygames.advanced import *` | Core engine + physics + controllable player + Animator |

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
| `game.check_key_pressed(name)` | Check if a key is pressed — e.g. `"left"`, `"space"`, `"w"` |
| `game.start_score_counter()` | Display score on screen |
| `game.score` | Set or update the score value |
| `game.start_garbage_collecter()` | Auto-remove off-screen objects |
| `game.load_image(name, path)` | Load an image by name |
| `game.img(name, x, y, w, h)` | Draw a loaded image |
| `game.load_sound(name, path)` | Load a sound by name |
| `game.play_sound(name)` | Play a loaded sound |
| `game.set_speed(fps)` | Set target FPS (default 60) |
| `game.zoom(factor)` | Resize the window by a multiplier |
| `game.mainloop(logic)` | Start the game loop |
| `game.create_surface(width, height, color, alpha)` | Create a surface |
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

## Physics — `PhysicSprite` (medium)

```python
obj = PhysicSprite(game, x, y, width=50, height=50, color="red")
```

Extends `SSprites` with gravity, collision, and velocity.

| Attribute | Description |
|---|---|
| `obj.vel_x` | Horizontal velocity |
| `obj.vel_y` | Vertical velocity |
| `obj.gravity` | Gravity strength (default `0.8`) |
| `obj.max_fall_speed` | Max fall speed to prevent tunnelling (default `20`) |
| `obj.on_ground` | `True` if standing on a solid |

| Method | Description |
|---|---|
| `obj.apply_physics(solids)` | Apply gravity and collision — called automatically |
| `obj.jump(force=15)` | Jump if on the ground |

---

## Player — `Player` (advanced)

```python
player = Player(game, x, y, width=40, height=60, color="blue", speed=5,
                left="left", right="right", jump="space")
```

Extends `PhysicSprite` with keyboard input. Key bindings are fully customisable.

| Method | Description |
|---|---|
| `player.tick()` | Process input — call this in your game logic function |
| `player.handle_input()` | Handles left, right, and jump keys |

---

## Animation — `Animator` (advanced)

```python
from pygames.advanced import Animation

anim = Animator(target, animation_speed=0.1)
```

Works with objects that have a `.state` string and an `.animations` dict mapping state names to lists of `Surface` frames.

| Method | Description |
|---|---|
| `anim.refresh()` | Advance animation frame — call every game loop tick |
| `anim.hover(amplitude=5, speed=5)` | Vertical sine-wave floating motion |
| `anim.rotate_loop(speed=100)` | Continuous rotation |
| `anim.set_speed(speed)` | Change frame interval |

---

## Supported Keys

Pass any of these strings to `game.check_key_pressed()` or as custom key bindings:

`"left"`, `"right"`, `"up"`, `"down"`, `"space"`, `"esc"`, `"enter"`, `"shift"`, `"ctrl"`, `"tab"`, `"backspace"`, or any letter/number like `"a"`, `"w"`, `"1"`

---

## Native Pygame

Since PyGame-S uses `from pygame import *` internally, all Pygame features are available directly:

```python
from pygames.advanced import *

mixer.music.load("background.mp3")
mixer.music.play(-1)

draw.rect(game.screen, "red", (100, 100, 50, 50))
```

---

## Error Handling

| Error | Cause |
|---|---|
| `FileNotFoundError` | Invalid file path for image, sound, or icon |
| `TypeError` | Wrong type passed to width, height, speed, or jump force |
| `ValueError` | Negative speed value |
| `NameError` | Invalid colour name or missing sound |

---

## Version

Current release: **v2.1.7**

Inspired by [Pygame Zero](https://pygame-zero.readthedocs.io/), built to be more Pythonic, flexible, and extensible.

## Links

- GitHub: https://github.com/manupolice12-sketch/pygames
- Bug Reports: https://github.com/manupolice12-sketch/pygames/issues
- PyPI: https://pypi.org/project/pygames-simplified/
