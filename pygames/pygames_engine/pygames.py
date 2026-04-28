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
        self.logging_enabled = logging
        self.log_file = None

    def set_title(self, title):
        """Set the window title.
        
        Args:
            title: String to display in window title bar
        """
        display.set_caption(str(title))
        self._log(f"Window title set to: {title}", "SUCCESS")

    def _log(self, message, status="INFO"):
        """Write a log message to logs.txt.
        
        Args:
            message: The log message to write
            status: Status level (SUCCESS, ERROR, INFO)
        """
        if not self.logging_enabled or self.log_file is None:
            return
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [{status}] {message}\n"
        try:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(log_entry)
        except Exception:
            pass

    def enable_logging(self, log_path="logs.txt"):
        """Enable logging and optionally set the log file path.
        
        Args:
            log_path: Optional custom path for the log file
        """
        self.logging_enabled = True
        if log_path:
            self.log_file = log_path
        else:
            self.log_file = "logs.txt"
        self._log("Logging enabled", "INFO")

    def disable_logging(self):
        """Disable logging."""
        self.logging_enabled = False
        self._log("Logging disabled", "INFO")

    def set_icon(self, path):
        """Set the window icon from an image file.
        
        Args:
            path: Path to the icon image file
            
        Raises:
            FileNotFoundError: If the icon file doesn't exist
        """
        try:
            icon = image.load(path)
            display.set_icon(icon)
            self._log(f"Icon loaded from: {path}", "SUCCESS")
        except FileNotFoundError:
            self._log(f"Icon file not found: {path}", "ERROR")
            raise FileNotFoundError(f"The file '{path}' does not exist, check the file.")

    def load_image(self, name, path):
        """Load an image and store it with a given name.
        
        Args:
            name: Key to store the image under for later retrieval
            path: Path to the image file
            
        Raises:
            FileNotFoundError: If the image file doesn't exist
        """
        try:
            self.images[name] = image.load(path).convert_alpha()
            self._log(f"Image '{name}' loaded from: {path}", "SUCCESS")
        except FileNotFoundError:
            self._log(f"Image file not found: {path}", "ERROR")
            raise FileNotFoundError(f"The file '{path}' does not exist, check the file.")

    def img(self, name, x, y, w=None, h=None):
        """Draw a loaded image to the screen.
        
        Args:
            name: Key of the image to draw (must be loaded first)
            x: X coordinate for image placement
            y: Y coordinate for image placement
            w: Optional width to scale the image to
            h: Optional height to scale the image to
            
        Raises:
            FileNotFoundError: If the image name doesn't exist
        """
        try:
            img = self.images.get(name)
            if img:
                if w is not None and h is not None:
                    img = transform.scale(img, (w, h))
                self.screen.blit(img, (x, y))
        except FileNotFoundError:
            raise FileNotFoundError(f"The image '{name}' does not exist, check the name.")

    def load_sound(self, name, path):
        """Load a sound file and store it with a given name.
        
        Args:
            name: Key to store the sound under for later retrieval
            path: Path to the sound file
            
        Raises:
            FileNotFoundError: If the sound file doesn't exist
        """
        try:
            self.sounds[name] = mixer.Sound(path)
            self._log(f"Sound '{name}' loaded from: {path}", "SUCCESS")
        except FileNotFoundError:
            self._log(f"Sound file not found: {path}", "ERROR")
            raise FileNotFoundError(f"The file '{path}' does not exist, check the file.")

    def play_sound(self, name):
        """Play a loaded sound by name.
        
        Args:
            name: Key of the sound to play
            
        Raises:
            NameError: If the sound hasn't been loaded
        """
        if name in self.sounds:
            self.sounds[name].play()
            self._log(f"Playing sound: {name}", "SUCCESS")
        else:
            self._log(f"Sound '{name}' not found. Make sure to load it first.", "ERROR")
            raise NameError(f"Sound '{name}' not found. Make sure to load it first.")

    def start_score_counter(self):
        """Enable score tracking and display during the game."""
        self.score_active = True
        self._log("Score counter enabled", "SUCCESS")

    def start_garbage_collecter(self):
        """Enable automatic cleanup of objects outside the screen bounds."""
        self.garbage_collection = True
        self._log("Garbage collector enabled", "SUCCESS")
        """Enable automatic cleanup of objects outside the screen bounds."""
        self.garbage_collection = True

    def clean_up(self):
        """Remove objects that are far outside the screen bounds.
        
        This method is called automatically if garbage collection is enabled.
        It helps improve performance by removing off-screen objects.
        """
        if self.garbage_collection:
           b = 150
        def in_bounds(o):
            return (o.rect.right > -b and o.rect.left < self.screen_width + b and
                    o.rect.bottom > -b and o.rect.top < self.screen_height + b)
        self.objects = [o for o in self.objects if in_bounds(o)]
        self.solids  = [o for o in self.solids  if in_bounds(o)]

    def create_surface(self, width, height, color=None, alpha=None):
        """Create a new surface (blank image) for game objects.
        
        Args:
            width: Width of the surface in pixels
            height: Height of the surface in pixels
            color: Optional color to fill the surface with
            alpha: Optional alpha channel value for transparency
            
        Returns:
            A pygame Surface object
            
        Raises:
            NameError: If an invalid color is provided
        """
        if alpha:
            surface = Surface((width, height, SRCALPHA)).convert_alpha()
        else:
            surface = Surface((width, height)).convert()
            surface = surface.convert_alpha()
            if color:
                try:
                    surface.fill(color)
                except (ValueError, TypeError):
                    self._log(f"Invalid color: {color}", "ERROR")
                    raise NameError(f"The color '{color}' does not exist, please check the color you typed.")
        self._log(f"Surface created: {width}x{height}, color={color}", "SUCCESS")
        return surface

    def background(self, color):
        """Fill the screen with a solid color.
        
        Args:
            color: Color value (RGB tuple or color name string)
        """
        self.screen.fill(color)
        self._log(f"Background set to: {color}", "INFO")    

    def start_loop(self):
        """Update and draw all game objects each frame.
        
        This method is called automatically at the start of each frame
        in the main loop. It handles physics updates and rendering.
        """
        self.clean_up()
        for item in self.objects:
            if hasattr(item, 'apply_physics'):
                item.apply_physics(self.solids)
            item.draw()
        if self.score_active:
            text_surface = self.font.render(f"Score: {self.score}", True, "white")
            self.screen.blit(text_surface, (10, 10))

    def show_score(self, x=10, y=10, color="white"):
        """Display the current score at a specific position.
        
        Args:
            x: X coordinate for score display
            y: Y coordinate for score display
            color: Color of the score text
        """
        score_surf = self.font.render(f"Score: {self.score}", True, color)
        self.screen.blit(score_surf, (x, y))

    def start(self, *objects):
        """Add objects to the game for tracking and rendering.
        
        Args:
            *objects: Sprite objects to add to the game
        """
        for item in objects:
            if item not in self.objects:
                self.objects.append(item)
                self._log(f"Object added: {type(item).__name__}", "SUCCESS")

    def make_solid(self, *objects):
        """Mark objects as solid (collidable) in the game.
        
        Solid objects will have physics collisions applied to them.
        
        Args:
            *objects: Sprite objects to mark as solid
        """
        for item in objects:
            if item not in self.solids:
                self.solids.append(item)
                self._log(f"Object marked solid: {type(item).__name__}", "SUCCESS")
            if item not in self.objects:
                self.objects.append(item)

    def check_key_pressed(self, name):
        name = name.lower()
        special_keys = {
            "space": K_SPACE, "esc": K_ESCAPE, "up": K_UP,
            "down": K_DOWN, "left": K_LEFT, "right": K_RIGHT,
            "enter": K_RETURN, "shift": K_LSHIFT, "ctrl": K_LCTRL,
            "tab": K_TAB, "backspace": K_BACKSPACE
        }
        if name in special_keys:
            return self.keys[special_keys[name]]
        key_const = globals().get(f"K_{name.upper()}")
        if key_const is None:
            return False  # Bug fix: was raising TypeError on unknown keys
        return self.keys[key_const]

    def zoom(self, factor):
        """Resize the game window.
        
        Args:
            factor: Multiplier for the new size (e.g., 2.0 doubles the size)
        """
        self.screen_width = int(self.screen_width * factor)
        self.screen_height = int(self.screen_height * factor)
        self.screen = display.set_mode((self.screen_width, self.screen_height))

    def set_speed(self, fps):
        """Set the target frames per second.
        
        Args:
            fps: Target frame rate (higher = smoother but more CPU usage)
        """
        self.fps = fps

    def update_screen(self):
        """Update the display with the current frame.
        
        This should be called at the end of each frame in the game loop.
        """
        display.flip()
        self.clock.tick(self.fps)

    def process_events(self):
        """Process pygame events (quit, input, etc.).
        
        Returns:
            True if the game should continue running, False to quit
        """
        for e in event.get():
            if e.type == QUIT:
                self.is_running = False
        return self.is_running

    def mainloop(self, game_logic):
        """Start the main game loop.
        
        This method runs the game until the window is closed or
        the game is quit. It calls the provided game_logic function
        each frame to update game state.
        
        Args:
            game_logic: Function to call each frame for game updates
        """
        while self.is_running:
            self.process_events()
            game_logic()
            self.start_loop()
            self.update_screen()
        quit()
        sys.exit() #This is to ensure the code exits completely, preventing any lingering processes.
