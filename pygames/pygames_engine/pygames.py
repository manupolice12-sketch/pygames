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

import pygame
from pygame import (
    display, event, font, image, key, mixer, time, transform,
    Surface, QUIT, SRCALPHA,
    K_SPACE, K_ESCAPE, K_UP, K_DOWN, K_LEFT, K_RIGHT,
    K_RETURN, K_LSHIFT, K_LCTRL, K_TAB, K_BACKSPACE,
    init, quit as pg_quit,
    sprite as sprite_module,
)

from .engines.power1.physics import PhysicSprite  # noqa: F401 – re-exported

# Default layer constants — importable by user code.
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
        init()
        font.init()
        self.screen_width = w
        self.screen_height = h
        self.screen = display.set_mode((w, h))

        self.logging_enabled = logging

        main_module = sys.modules.get('__main__')
        if main_module and hasattr(main_module, '__file__'):
            base_dir = os.path.dirname(os.path.abspath(main_module.__file__))
            self.log_file = os.path.join(base_dir, "logs.txt")
        else:
            self.log_file = os.path.join(os.getcwd(), "logs.txt")

        self.set_title(title)
        if icon_path:
            self.set_icon(icon_path)

        self.clock = time.Clock()
        self.font = font.SysFont("Arial", 30)
        self.sounds = {}
        self.images = {}

        # LayeredUpdates: a Group that draws sprites in layer order.
        # Lower layer numbers are drawn first (furthest back).
        # Layers: LAYER_BACKGROUND=0, LAYER_DEFAULT=1, LAYER_PLAYER=2, LAYER_UI=3
        self.objects = sprite_module.LayeredUpdates()

        # Solids is a plain Group — it only needs to supply a sprite list
        # for collision queries, so layering is not needed here.
        self.solids = sprite_module.Group()

        self.score = 0
        self.score_active = False
        self.garbage_collection = False
        self.fps = 60
        self.is_running = True

        self._key_state = None

        self._log(f"Game engine initialized: {w}x{h}", "SUCCESS")

    # ------------------------------------------------------------------
    # Logging
    # ------------------------------------------------------------------

    def _log(self, message, status="INFO"):
        """Write a timestamped entry to the log file (if logging is on)."""
        if not self.logging_enabled:
            return
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            with open(self.log_file, "a") as f:
                f.write(f"[{timestamp}] [{status}] {message}\n")
        except Exception:
            pass

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
        self._log("Logging system disabled", "INFO")
        self.logging_enabled = False

    # ------------------------------------------------------------------
    # Window management
    # ------------------------------------------------------------------

    def set_title(self, title):
        """Set the window title."""
        display.set_caption(str(title))
        self._log(f"Window title changed to: {title}", "INFO")

    def set_icon(self, path):
        """Set the window icon."""
        try:
            display.set_icon(image.load(path))
            self._log(f"Window icon loaded: {path}", "SUCCESS")
        except FileNotFoundError:
            self._log(f"Failed to load icon: {path}", "ERROR")
            raise FileNotFoundError(f"The file '{path}' does not exist, check the file.")

    # ------------------------------------------------------------------
    # Asset loading
    # ------------------------------------------------------------------

    def load_image(self, name, path):
        """Load an image and store it under name."""
        try:
            self.images[name] = image.load(path).convert_alpha()
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
                self.images[cache_key] = transform.scale(src, (w, h))
            src = self.images[cache_key]

        self.screen.blit(src, (x, y))

    def load_sound(self, name, path):
        """Load a sound and store it under name."""
        try:
            mixer.init()
            self.sounds[name] = mixer.Sound(path)
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

    # ------------------------------------------------------------------
    # Score
    # ------------------------------------------------------------------

    def start_score_counter(self):
        """Enable the automatic score display each frame."""
        self.score_active = True
        self._log("Score counter activated", "INFO")

    def show_score(self, x=10, y=10, color="white"):
        """Manually display the score at a given position."""
        score_surf = self.font.render(f"Score: {self.score}", True, color)
        self.screen.blit(score_surf, (x, y))

    # ------------------------------------------------------------------
    # Object / Group management
    # ------------------------------------------------------------------

    def start(self, *objects, layer=LAYER_DEFAULT):
        """Add sprites to the game loop at the given draw layer.

        Args:
            *objects: One or more SSprites (or subclass) instances.
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
                self._log(
                    f"Added {type(item).__name__} to layer {layer}", "SUCCESS"
                )

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
            self._log(f"Marked {type(item).__name__} as solid", "SUCCESS")

    def set_layer(self, obj, layer):
        """Move a sprite to a different draw layer.

        Args:
            obj: The sprite to move.
            layer: The new layer number.
        """
        if self.objects.has(obj):
            self.objects.change_layer(obj, layer)
            self._log(f"{type(obj).__name__} moved to layer {layer}", "INFO")

    def get_layer(self, obj):
        """Return the current draw layer of a sprite.

        Args:
            obj: The sprite to query.

        Returns:
            Integer layer number, or None if the sprite is not in the game.
        """
        if self.objects.has(obj):
            return self.objects.get_layer_of_sprite(obj)
        return None

    def get_sprites_in_layer(self, layer):
        """Return a list of all sprites in a given layer.

        Args:
            layer: The layer number to query.

        Returns:
            List of sprites in that layer.
        """
        return self.objects.get_sprites_from_layer(layer)

    def start_garbage_collector(self):
        """Enable automatic removal of off-screen objects."""
        self.garbage_collection = True
        self._log("Garbage collector activated", "INFO")

    def start_garbage_collecter(self):
        """Deprecated alias for start_garbage_collector()."""
        self.start_garbage_collector()

    def clean_up(self):
        """Remove sprites that have moved too far off-screen.

        Uses sprite.kill() which removes the sprite from every group it
        belongs to — no manual sync between objects and solids needed.
        """
        if not self.garbage_collection:
            return
        margin = 150
        to_remove = [
            o for o in self.objects
            if not (o.rect.right > -margin and o.rect.left < self.screen_width + margin
                    and o.rect.bottom > -margin and o.rect.top < self.screen_height + margin)
        ]
        for o in to_remove:
            o.kill()  # Removes from self.objects, self.solids, and any other group
        if to_remove:
            self._log(f"Garbage collector removed {len(to_remove)} objects", "INFO")

    def create_surface(self, width, height, color=None, alpha=None):
        """Create a new pygame Surface."""
        if alpha:
            surface = Surface((width, height), SRCALPHA).convert_alpha()
        else:
            surface = Surface((width, height)).convert_alpha()
            if color:
                try:
                    surface.fill(color)
                except (ValueError, TypeError):
                    self._log(f"Invalid color: {color}", "ERROR")
                    raise NameError(f"The color '{color}' does not exist.")
        return surface

    def background(self, color):
        """Fill the entire screen with a color."""
        self.screen.fill(color)

    # ------------------------------------------------------------------
    # Input
    # ------------------------------------------------------------------

    _SPECIAL_KEYS = {
        "space": K_SPACE, "esc": K_ESCAPE, "up": K_UP, "down": K_DOWN,
        "left": K_LEFT, "right": K_RIGHT, "enter": K_RETURN,
        "shift": K_LSHIFT, "ctrl": K_LCTRL, "tab": K_TAB,
        "backspace": K_BACKSPACE,
    }

    def check_key_pressed(self, name):
        """Check if a specific key is held down.

        Uses the key state snapshot taken at the start of the frame so
        calling this multiple times per frame never queries the hardware twice.
        """
        if self._key_state is None:
            self._key_state = key.get_pressed()
        name = name.lower()
        if name in self._SPECIAL_KEYS:
            return self._key_state[self._SPECIAL_KEYS[name]]
        key_const = getattr(pygame, f"K_{name.upper()}", None)
        return bool(self._key_state[key_const]) if key_const is not None else False

    # ------------------------------------------------------------------
    # Screen helpers
    # ------------------------------------------------------------------

    def zoom(self, factor):
        """Scale the screen resolution by factor."""
        self.screen_width = int(self.screen_width * factor)
        self.screen_height = int(self.screen_height * factor)
        self.screen = display.set_mode((self.screen_width, self.screen_height))
        self._log(f"Zoom applied: factor {factor}", "INFO")

    def set_speed(self, fps):
        """Set the target frames per second."""
        self.fps = fps

    def update_screen(self):
        """Flip the display buffer and tick the clock."""
        display.flip()
        self.clock.tick(self.fps)

    def process_events(self):
        """Handle system events and refresh the per-frame key state cache."""
        self._key_state = key.get_pressed()
        for e in event.get():
            if e.type == QUIT:
                self.is_running = False
        return self.is_running

    # ------------------------------------------------------------------
    # Main loop
    # ------------------------------------------------------------------

    def start_loop(self):
        """Update all sprites and draw them in layer order.

        Group.update(solids) passes the solid sprite list into every sprite's
        update() method. Group.draw() then blits all sprites onto the screen
        in layer order (lowest layer number drawn first).
        """
        self.clean_up()

        # Pass solids group into each sprite's update() so physics sprites
        # can resolve collisions without needing a direct Game reference.
        self.objects.update(self.solids)

        # LayeredUpdates.draw() respects layer order automatically.
        self.objects.draw(self.screen)

        if self.score_active:
            text_surface = self.font.render(f"Score: {self.score}", True, "white")
            self.screen.blit(text_surface, (10, 10))

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
        pg_quit()
        sys.exit()
