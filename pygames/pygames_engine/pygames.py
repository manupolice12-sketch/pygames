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

from pygame import *
import sys
from datetime import datetime
from .engines.power1.physics import *

class Game:
    """Main class for the Pygame-S engine, handling game initialization, main loop, and core functionalities."""
    
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
        
        # Setup logging infrastructure
        self.logging_enabled = logging
        self.log_file = "logs.txt"
        
        self.set_title(title)
        if icon_path:
            self.set_icon(icon_path)
            
        self.clock = time.Clock()
        self.font = font.SysFont("Arial", 30)
        self.sounds = {}
        self.images = {}
        mixer.init()
        self.objects = []
        self.solids = []
        self.score = 0
        self.score_active = False
        self.garbage_collection = False
        self.fps = 60
        self.is_running = True
        
        self._log(f"Game engine initialized: {w}x{h}", "SUCCESS")

    def _log(self, message, status="INFO"):
        """Internal method to write logs to a text file for debugging.
        
        Args:
            message: The text to record
            status: The level of the log (INFO, SUCCESS, ERROR)
        """
        if not self.logging_enabled:
            return
            
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [{status}] {message}\n"
        
        try:
            with open(self.log_file, "a") as f:
                f.write(log_entry)
        except Exception:
            # We don't want the logger itself to crash the game
            pass

    def enable_logging(self, log_path="logs.txt"):
        """Turn on the logging system during gameplay.
        
        Args:
            log_path: Optional custom path for the log file
        """
        self.logging_enabled = True
        if log_path:
            self.log_file = log_path
        self._log("Logging system enabled manually", "INFO")

    def disable_logging(self):
        """Turn off the logging system."""
        self._log("Logging system disabled manually", "INFO")
        self.logging_enabled = False

    def set_title(self, title):
        """Set the window title."""
        display.set_caption(str(title))
        self._log(f"Window title changed to: {title}", "INFO")

    def set_icon(self, path):
        """Set the window icon."""
        try:
            icon = image.load(path)
            display.set_icon(icon)
            self._log(f"Window icon loaded: {path}", "SUCCESS")
        except FileNotFoundError:
            self._log(f"Failed to load icon: {path}", "ERROR")
            raise FileNotFoundError(f"The file '{path}' does not exist, check the file.")

    def load_image(self, name, path):
        """Load an image and store it with a name."""
        try:
            self.images[name] = image.load(path).convert_alpha()
            self._log(f"Image '{name}' loaded from: {path}", "SUCCESS")
        except FileNotFoundError:
            self._log(f"Image load error: {path}", "ERROR")
            raise FileNotFoundError(f"The file '{path}' does not exist, check the file.")

    def img(self, name, x, y, w=None, h=None):
        """Draw a loaded image to the screen."""
        img = self.images.get(name)
        if img:
            if w is not None and h is not None:
                img = transform.scale(img, (w, h))
            self.screen.blit(img, (x, y))
        else:
            self._log(f"Requested image '{name}' not found", "ERROR")

    def load_sound(self, name, path):
        """Load a sound and store it with a name."""
        try:
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

    def start_score_counter(self):
        """Enable the automatic score display."""
        self.score_active = True
        self._log("Score counter activated", "INFO")

    def start_garbage_collecter(self):
        """Enable automatic removal of off-screen objects."""
        self.garbage_collection = True
        self._log("Garbage collector activated", "INFO")

    def clean_up(self):
        """Remove objects that have moved too far off-screen."""
        if self.garbage_collection:
            b = 150 # boundary padding
            initial_count = len(self.objects)
            def in_bounds(o):
                return (o.rect.right > -b and o.rect.left < self.screen_width + b and
                        o.rect.bottom > -b and o.rect.top < self.screen_height + b)
            
            self.objects = [o for o in self.objects if in_bounds(o)]
            self.solids = [o for o in self.solids if o in self.objects]
            
            removed = initial_count - len(self.objects)
            if removed > 0:
                self._log(f"Garbage collector removed {removed} objects", "INFO")

    def create_surface(self, width, height, color=None, alpha=None):
        """Create a new pygame Surface."""
        if alpha:
            surface = Surface((width, height), SRCALPHA).convert_alpha()
        else:
            surface = Surface((width, height)).convert()
            surface = surface.convert_alpha()
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

    def start_loop(self):
        """Handle internal logic for drawing and physics."""
        self.clean_up()
        for item in self.objects:
            if hasattr(item, 'apply_physics'):
                item.apply_physics(self.solids)
            item.draw()
        if self.score_active:
            text_surface = self.font.render(f"Score: {self.score}", True, "white")
            self.screen.blit(text_surface, (10, 10))

    def show_score(self, x=10, y=10, color="white"):
        """Manually display the score."""
        score_surf = self.font.render(f"Score: {self.score}", True, color)
        self.screen.blit(score_surf, (x, y))

    def start(self, *objects):
        """Add objects to the main loop."""
        for item in objects:
            if item not in self.objects:
                self.objects.append(item)
                self._log(f"Added {type(item).__name__} to game", "SUCCESS")

    def make_solid(self, *objects):
        """Mark objects as solid for collisions."""
        for item in objects:
            if item not in self.solids:
                self.solids.append(item)
                self._log(f"Marked {type(item).__name__} as solid", "SUCCESS")
            if item not in self.objects:
                self.objects.append(item)

    def check_key_pressed(self, name):
        """Check if a specific key is held down."""
        name = name.lower()
        self.keys = key.get_pressed()
        special_keys = {
            "space": K_SPACE, "esc": K_ESCAPE, "up": K_UP, "down": K_DOWN,
            "left": K_LEFT, "right": K_RIGHT, "enter": K_RETURN, "shift": K_LSHIFT,
            "ctrl": K_LCTRL, "tab": K_TAB, "backspace": K_BACKSPACE
        }
        if name in special_keys:
            return self.keys[special_keys[name]]
        key_const = globals().get(f"K_{name.upper()}")
        return self.keys[key_const] if key_const is not None else False

    def zoom(self, factor):
        """Scale the screen resolution."""
        self.screen_width = int(self.screen_width * factor)
        self.screen_height = int(self.screen_height * factor)
        self.screen = display.set_mode((self.screen_width, self.screen_height))
        self._log(f"Zoom applied: factor {factor}", "INFO")

    def set_speed(self, fps):
        """Set the target frames per second."""
        self.fps = fps

    def update_screen(self):
        """Update the display and maintain frame rate."""
        display.flip()
        self.clock.tick(self.fps)

    def process_events(self):
        """Handle system events like closing the window."""
        for e in event.get():
            if e.type == QUIT:
                self.is_running = False
        return self.is_running

    def mainloop(self, game_logic):
        """Start the main game loop."""
        self._log("Mainloop started", "SUCCESS")
        while self.is_running:
            self.process_events()
            game_logic()
            self.start_loop()
            self.update_screen()
        quit()
        sys.exit()