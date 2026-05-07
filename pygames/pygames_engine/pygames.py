"""
Pygames Engine - Main Game Class

This module provides the core Game class for the Pygame-S engine.
It handles game initialization, the main game loop, and provides
various utility methods for game development.

Features:
    - Window and screen management
    - Image and sound loading
    - Sprite and object management
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
    Surface, QUIT, SRCALPHA, K_SPACE, K_ESCAPE, K_UP, K_DOWN,
    K_LEFT, K_RIGHT, K_RETURN, K_LSHIFT, K_LCTRL, K_TAB, K_BACKSPACE,
    init, quit as pg_quit
)

from .engines.power1.physics import PhysicSprite  # noqa: F401 – re-exported


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
        # Use sets for O(1) membership checks in start() / make_solid()
        self.objects: list = []
        self.solids: set = set()
        self.score = 0
        self.score_active = False
        self.garbage_collection = False
        self.fps = 60
        self.is_running = True

        # Cache key state once per frame instead of re-querying per check_key_pressed call
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

        If w and h are given and differ from the image's current size,
        a scaled copy is used. Scaled surfaces are cached to avoid
        recreating them every frame.
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
    # Object management
    # ------------------------------------------------------------------

    def start_garbage_collector(self):
        """Enable automatic removal of off-screen objects."""
        self.garbage_collection = True
        self._log("Garbage collector activated", "INFO")

    # Legacy spelling kept as an alias so existing code doesn't break.
    def start_garbage_collecter(self):
        self.start_garbage_collector()

    def clean_up(self):
        """Remove objects that have moved too far off-screen."""
        if not self.garbage_collection:
            return
        margin = 150
        initial_count = len(self.objects)

        self.objects = [
            o for o in self.objects
            if (o.rect.right > -margin and o.rect.left < self.screen_width + margin
                and o.rect.bottom > -margin and o.rect.top < self.screen_height + margin)
        ]
        # Keep solids in sync; solids is a set so discard is safe.
        self.solids = {o for o in self.solids if o in self.objects}

        removed = initial_count - len(self.objects)
        if removed > 0:
            self._log(f"Garbage collector removed {removed} objects", "INFO")

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

    def start(self, *objects):
        """Add objects to the main loop."""
        for item in objects:
            if item not in self.objects:
                self.objects.append(item)
                self._log(f"Added {type(item).__name__} to game", "SUCCESS")

    def make_solid(self, *objects):
        """Mark objects as solid for physics collision detection."""
        for item in objects:
            self.solids.add(item)
            if item not in self.objects:
                self.objects.append(item)
            self._log(f"Marked {type(item).__name__} as solid", "SUCCESS")

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
        """Handle system events (window close, etc.).

        Also refreshes the per-frame key state cache so check_key_pressed
        always reflects the current frame.
        """
        self._key_state = key.get_pressed()
        for e in event.get():
            if e.type == QUIT:
                self.is_running = False
        return self.is_running

    # ------------------------------------------------------------------
    # Main loop
    # ------------------------------------------------------------------

    def start_loop(self):
        """Apply physics, draw objects, and optionally render the score."""
        self.clean_up()
        solid_list = list(self.solids)
        for item in self.objects:
            if hasattr(item, 'apply_physics'):
                item.apply_physics(solid_list)
            item.draw()
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
