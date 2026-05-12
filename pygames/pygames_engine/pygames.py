"""
Pygames Engine - Main Game Class

This module provides the core Game class for the Pygame-S engine.
It handles game initialization, the main game loop, and provides
various utility methods for game development.

Features:
    - Window and screen management
    - Image and sound loading
    - Sprite and object management via pygame Groups
    - Layered drawing with LayeredUpdates
    - Physics integration
    - Score tracking
    - Input handling

Usage:
    from pygames_engine import Game
    app = Game(800, 600, "My Game")
    app.mainloop(game_logic)
"""

import sys
import os
from datetime import datetime

try:
    import pygame as pg
except ImportError:
    raise ImportError(
        "pygame or pygame-ce is required. "
        "Install it with: pip install pygame-ce"
    )

from .engines.power1.physics import PhysicSprite

LAYER_BACKGROUND = 0
LAYER_DEFAULT    = 1
LAYER_PLAYER     = 2
LAYER_UI         = 3


class Game:
    """Main class for the Pygame-S engine."""

    def __init__(self, w=800, h=600, title="Pygame-S", icon_path=None, logging=False):
        """Initialize the game engine.

        Args:
            w: Screen width in pixels (default: 800)
            h: Screen height in pixels (default: 600)
            title: Window title (default: "Pygame-S")
            icon_path: Optional path to icon image file
            logging: Enable logging to logs.txt (default: False)
        """
        pg.init()
        pg.font.init()
        self.screen_width = w
        self.screen_height = h
        self.screen = pg.display.set_mode((w, h))
        self.logging_enabled = logging
        self._SPECIAL_KEYS = {
            "space": pg.K_SPACE, "esc": pg.K_ESCAPE, "up": pg.K_UP, "down": pg.K_DOWN,
            "left": pg.K_LEFT, "right": pg.K_RIGHT, "enter": pg.K_RETURN,
            "shift": pg.K_LSHIFT, "ctrl": pg.K_LCTRL, "tab": pg.K_TAB,
            "backspace": pg.K_BACKSPACE,
        }
        main_module = sys.modules.get('__main__')
        if main_module and hasattr(main_module, '__file__'):
            base_dir = os.path.dirname(os.path.abspath(main_module.__file__))
            self.log_file = os.path.join(base_dir, "logs.txt")
        else:
            self.log_file = os.path.join(os.getcwd(), "logs.txt")

        self.set_title(title)
        if icon_path:
            self.set_icon(icon_path)

        self.clock = pg.time.Clock()
        self.font = pg.font.SysFont("Arial", 30)
        self.sounds = {}
        self.images = {}
        self.objects = pg.sprite.LayeredUpdates()
        self.solids = pg.sprite.Group()
        self.score = 0
        self.score_active = False
        self.garbage_collection = False
        self.fps = 60
        self.is_running = True
        self._key_state = None
        self._log(f"Game engine initialized: {w}x{h}", "SUCCESS")

    def _log(self, message, status):
        """Write a timestamped entry to the log file (if logging is on)."""
        if not self.logging_enabled:
            return
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            with open(self.log_file, "a") as f:
                f.write(f"[{timestamp}] [{status}] {message}\n")
        except Exception:
            raise IOError(f"Logging error: Could not write to log file at '{self.log_file}'")

    def enable_logging(self, log_path=None):
        """Turn on the logging system.

        Args:
            log_path: Optional custom path for the log file.
        """
        self.logging_enabled = True
        if log_path:
            if not os.path.exists(log_path):
                try:
                    with open(log_path, "w") as f:
                        f.write("")
                except Exception as e:
                    raise IOError(f"Failed to initialize log file at '{log_path}': {e}")
            self.log_file = log_path
        else:
            main_module = sys.modules.get('__main__')
            if main_module and hasattr(main_module, '__file__'):
                base_dir = os.path.dirname(os.path.abspath(main_module.__file__))
                self.log_file = os.path.join(base_dir, "logs.txt")
            else:
                self.log_file = os.path.join(os.getcwd(), "logs.txt")
            try:
                with open(self.log_file, "w") as f:
                    f.write("")
                print(f"Log file initialized at: {self.log_file}")
            except Exception as e:
                raise IOError(f"Failed to initialize log file: {e}")
        self._log("Logging system enabled", "INFO")

    def disable_logging(self):
        """Turn off the logging system."""
        self._log("Logging system disabled manually", "INFO")
        self.logging_enabled = False

    def set_title(self, title):
        """Set the window title."""
        pg.display.set_caption(str(title))
        self._log(f"Window title set to: {title}", "INFO")

    def set_icon(self, path):
        """Set the window icon."""
        try:
            pg.display.set_icon(pg.image.load(path))
            self._log(f"Window icon loaded: {path}", "SUCCESS")
        except FileNotFoundError:
            self._log(f"Failed to load icon: {path}", "ERROR")
            raise FileNotFoundError(f"The file '{path}' does not exist, check the file.")

    def load_image(self, name, path):
        """Load an image and store it under name."""
        try:
            self.images[name] = pg.image.load(path).convert_alpha()
            self._log(f"Image '{name}' loaded from: {path}", "SUCCESS")
        except FileNotFoundError:
            self._log(f"Image load error: {path}", "ERROR")
            raise FileNotFoundError(f"The file '{path}' does not exist, check the file.")

    def img(self, name, x, y, w=None, h=None):
        """Draw a loaded image to the screen.

        Scaled copies are cached after the first scale so this is safe to
        call every frame without a performance penalty.
        """
        src = self.images.get(name)
        if src is None:
            self._log(f"Requested image '{name}' not found", "ERROR")
            return

        if w is not None and h is not None and (w, h) != src.get_size():
            cache_key = f"_scaled_{name}_{w}_{h}"
            if cache_key not in self.images:
                self.images[cache_key] = pg.transform.scale(src, (w, h))
                self._log(f"Image '{name}' scaled and cached at {w}x{h}", "INFO")
            src = self.images[cache_key]

        self.screen.blit(src, (x, y))
        self._log(f"Image '{name}' drawn at ({x}, {y})", "INFO")

    def load_sound(self, name, path):
        """Load a sound and store it under name."""
        try:
            pg.mixer.init()
            self.sounds[name] = pg.mixer.Sound(path)
            self._log(f"Sound '{name}' loaded from: {path}", "SUCCESS")
        except FileNotFoundError:
            self._log(f"Sound load error: {path}", "ERROR")
            raise FileNotFoundError(f"The file '{path}' does not exist, check the file.")

    def play_sound(self, name):
        """Play a loaded sound."""
        if name in self.sounds:
            self.sounds[name].play()
            self._log(f"Playing sound: {name}", "INFO")
        else:
            self._log(f"Sound '{name}' not found", "ERROR")
            raise NameError(f"Sound '{name}' not found.")

    def start_score_counter(self):
        """Enable the automatic score display each frame."""
        self.score_active = True
        self._log("Score counter activated", "INFO")

    def show_score(self, x=10, y=10, color="white"):
        """Manually display the score at a given position."""
        score_surf = self.font.render(f"Score: {self.score}", True, color)
        self.screen.blit(score_surf, (x, y))
        self._log(f"Score ({self.score}) displayed at ({x}, {y})", "INFO")

    def start(self, *objects, layer=LAYER_DEFAULT):
        """Add sprites to the game loop at the given draw layer.

        Args:
            *objects: One or more sprite instances.
            layer: Draw layer (default: LAYER_DEFAULT = 1).
                   Lower numbers are drawn first (further back).
                   Use the LAYER_* constants or any integer.

        Example:
            game.start(background_tile, layer=LAYER_BACKGROUND)
            game.start(player, layer=LAYER_PLAYER)
            game.start(hud_icon, layer=LAYER_UI)
        """
        for item in objects:
            if not self.objects.has(item):
                self.objects.add(item, layer=layer)
                self._log(f"Added {type(item).__name__} to layer {layer}", "SUCCESS")
            else:
                self._log(f"{type(item).__name__} already in game loop, skipping", "INFO")

    def make_solid(self, *objects, layer=LAYER_DEFAULT):
        """Mark sprites as solid for physics collision and add to the game loop.

        Args:
            *objects: Sprites to make solid.
            layer: Draw layer for these sprites (default: LAYER_DEFAULT).
        """
        for item in objects:
            self.solids.add(item)
            if not self.objects.has(item):
                self.objects.add(item, layer=layer)
            self._log(f"Marked {type(item).__name__} as solid on layer {layer}", "SUCCESS")

    def set_layer(self, obj, layer):
        """Move a sprite to a different draw layer.

        Args:
            obj: The sprite to move.
            layer: The new layer number.
        """
        if self.objects.has(obj):
            self.objects.change_layer(obj, layer)
            self._log(f"{type(obj).__name__} moved to layer {layer}", "INFO")
        else:
            self._log(f"{type(obj).__name__} not found in game loop, cannot set layer", "ERROR")

    def get_layer(self, obj):
        """Return the current draw layer of a sprite, or None if not in the game.

        Args:
            obj: The sprite to query.
        """
        if self.objects.has(obj):
            layer = self.objects.get_layer_of_sprite(obj)
            self._log(f"{type(obj).__name__} is on layer {layer}", "INFO")
            return layer
        self._log(f"{type(obj).__name__} not found in game loop", "ERROR")
        return None

    def get_sprites_in_layer(self, layer):
        """Return a list of all sprites in a given layer.

        Args:
            layer: The layer number to query.
        """
        sprites = self.objects.get_sprites_from_layer(layer)
        self._log(f"Layer {layer} contains {len(sprites)} sprite(s)", "INFO")
        return sprites

    def start_garbage_collector(self):
        """Enable automatic removal of off-screen objects."""
        self.garbage_collection = True
        self._log("Garbage collector activated", "INFO")

    def start_garbage_collecter(self):
        """Deprecated alias for start_garbage_collector()."""
        self._log("start_garbage_collecter() is deprecated, use start_garbage_collector()", "INFO")
        self.start_garbage_collector()

    def clean_up(self):
        """Remove sprites that have moved too far off-screen."""
        if not self.garbage_collection:
            return
        margin = 150
        to_remove = [
            o for o in self.objects
            if not (o.rect.right > -margin and o.rect.left < self.screen_width + margin
                    and o.rect.bottom > -margin and o.rect.top < self.screen_height + margin)
        ]
        for o in to_remove:
            o.kill()
        if to_remove:
            self._log(f"Garbage collector removed {len(to_remove)} object(s)", "INFO")

    def create_surface(self, width, height, color=None, alpha=None):
        """Create a new pygame Surface."""
        if alpha:
            surface = pg.Surface((width, height), pg.SRCALPHA).convert_alpha()
            self._log(f"Alpha surface created: {width}x{height}", "SUCCESS")
        else:
            surface = pg.Surface((width, height)).convert_alpha()
            if color:
                try:
                    surface.fill(color)
                    self._log(f"Surface created: {width}x{height}, color={color}", "SUCCESS")
                except (ValueError, TypeError):
                    self._log(f"Invalid color: {color}", "ERROR")
                    raise NameError(f"The color '{color}' does not exist.")
            else:
                self._log(f"Surface created: {width}x{height}", "SUCCESS")
        return surface

    def background(self, color):
        """Fill the entire screen with a color."""
        self.screen.fill(color)
        self._log(f"Background filled with color: {color}", "INFO")

    def check_key_pressed(self, name):
        """Check if a specific key is held down.

        Uses the key state snapshot taken at the start of the frame so
        calling this multiple times per frame never queries the hardware twice.
        """
        if self._key_state is None:
            self._key_state = pg.key.get_pressed()
        name = name.lower()
        if name in self._SPECIAL_KEYS:
            pressed = bool(self._key_state[self._SPECIAL_KEYS[name]])
        else:
            key_const = getattr(pg, f"K_{name.upper()}", None)
            if key_const is None:
                self._log(f"Unknown key name: '{name}'", "ERROR")
                return False
            pressed = bool(self._key_state[key_const])
        self._log(f"Key '{name}' pressed: {pressed}", "INFO")
        return pressed

    def zoom(self, factor):
        """Scale the screen resolution by factor."""
        self.screen_width = int(self.screen_width * factor)
        self.screen_height = int(self.screen_height * factor)
        self.screen = pg.display.set_mode((self.screen_width, self.screen_height))
        self._log(f"Zoom applied: factor={factor}, new size={self.screen_width}x{self.screen_height}", "INFO")

    def set_speed(self, fps):
        """Set the target frames per second."""
        self.fps = fps
        self._log(f"FPS set to: {fps}", "INFO")

    def update_screen(self):
        """Flip the display buffer and tick the clock."""
        pg.display.flip()
        self.clock.tick(self.fps)
        self._log(f"Frame updated at {self.clock.get_fps():.2f} FPS", "INFO")

    def process_events(self):
        """Handle system events and refresh the per-frame key state cache."""
        self._key_state = pg.key.get_pressed()
        for e in pg.event.get():
            if e.type == pg.QUIT:
                self.is_running = False
                self._log("Quit event received, exiting main loop", "INFO")
        return self.is_running

    def start_loop(self):
        """Update all sprites and draw them in layer order."""
        self.clean_up()
        self.objects.update(self.solids)
        self.objects.draw(self.screen)
        if self.score_active:
            text_surface = self.font.render(f"Score: {self.score}", True, "white")
            self.screen.blit(text_surface, (10, 10))
        self._log("Sprites updated and drawn", "INFO")

    def mainloop(self, game_logic):
        """Start the main game loop.

        Args:
            game_logic: A callable invoked once per frame for user logic.
        """
        self._log("Mainloop started", "SUCCESS")
        while self.is_running:
            self.process_events()
            game_logic()
            self.start_loop()
            self.update_screen()
        self._log("Mainloop ended", "SUCCESS")
        pg.quit()
        self._log("Ending game engine session", "INFO")
        sys.exit()