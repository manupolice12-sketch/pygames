from pygame import *
import sys
from .engines.power1.physics import *

class Game:
    """Main class for the Pygame-S engine, handling game initialization, main loop, and core functionalities."""
    def __init__(self, w=800, h=600, title="Pygame-S", icon_path=None):
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

    def set_title(self, title):
        display.set_caption(str(title))

    def set_icon(self, path):
        try:
            icon = image.load(path)
            display.set_icon(icon)
        except FileNotFoundError:
            raise FileNotFoundError(f"The file '{path}' does not exist, check the file.")

    def load_image(self, name, path):
        try:
            self.images[name] = image.load(path).convert_alpha()
        except FileNotFoundError:
            raise FileNotFoundError(f"The file '{path}' does not exist, check the file.")

    def img(self, name, x, y, w=None, h=None):
        try:
            img = self.images.get(name)
            if img:
                if w is not None and h is not None:
                    img = transform.scale(img, (w, h))
                self.screen.blit(img, (x, y))
        except FileNotFoundError:
            raise FileNotFoundError(f"The image '{name}' does not exist, check the name.")

    def load_sound(self, name, path):
        try:
            self.sounds[name] = mixer.Sound(path)
        except FileNotFoundError:
            raise FileNotFoundError(f"The file '{path}' does not exist, check the file.")

    def play_sound(self, name):
        if name in self.sounds:
            self.sounds[name].play()
        else:
            raise NameError(f"Sound '{name}' not found. Make sure to load it first.")

    def start_score_counter(self):
        self.score_active = True

    def start_garbage_collecter(self):
        self.garbage_collection = True

    def clean_up(self):
      if self.garbage_collection:
        b = 150
        def in_bounds(o):
            return (o.rect.right > -b and o.rect.left < self.screen_width + b and
                    o.rect.bottom > -b and o.rect.top < self.screen_height + b)
        self.objects = [o for o in self.objects if in_bounds(o)]
        self.solids  = [o for o in self.solids  if in_bounds(o)]

    def create_surface(self, width,height, color=None, alpha=None):
        if alpha:
            surface = Surface((width, height, SRCALPHA)).convert_alpha()
        else:
            surface = Surface((width,height).convert())
            surface = surface.convert_alpha()
            if color:
                try:
                    surface.fill(color)
                except (ValueError, TypeError):
                    raise NameError(f"The color '{color}' does not exist, please check the color you typed.")
        return surface

    def background(self, color):
        self.screen.fill(color)    

    def start_loop(self):
        self.clean_up()
        for item in self.objects:
            if hasattr(item, 'apply_physics'):
                item.apply_physics(self.solids)
            item.draw()
        if self.score_active:
            text_surface = self.font.render(f"Score: {self.score}", True, "white")
            self.screen.blit(text_surface, (10, 10))

    def show_score(self, x=10, y=10, color="white"):
        score_surf = self.font.render(f"Score: {self.score}", True, color)
        self.screen.blit(score_surf, (x, y))

    def start(self, *objects):
        for item in objects:
            if item not in self.objects:
                self.objects.append(item)

    def make_solid(self, *objects):
        for item in objects:
            if item not in self.solids:
                self.solids.append(item)
                if item not in self.objects:
                    self.objects.append(item)

    def check_key_pressed(self, name):
        keys = key.get_pressed()
        name = name.lower()
        special_keys = {
            "space": K_SPACE, "esc": K_ESCAPE, "up": K_UP,
            "down": K_DOWN, "left": K_LEFT, "right": K_RIGHT,
            "enter": K_RETURN, "shift": K_LSHIFT, "ctrl": K_LCTRL,
            "tab": K_TAB, "backspace": K_BACKSPACE
        }
        if name in special_keys:
            return keys[special_keys[name]]
        key_const = globals().get(f"K_{name.upper()}")
        if key_const is None:
            return False  # Bug fix: was raising TypeError on unknown keys
        return keys[key_const]

    def zoom(self, factor):
        self.screen_width = int(self.screen_width * factor)
        self.screen_height = int(self.screen_height * factor)
        self.screen = display.set_mode((self.screen_width, self.screen_height))

    def set_speed(self, fps):
        self.fps = fps

    def update_screen(self):
        display.flip()
        self.clock.tick(self.fps)

    def process_events(self):
        for e in event.get():
            if e.type == QUIT:
                self.is_running = False
        return self.is_running

    def mainloop(self, game_logic):
        while self.is_running:
            self.process_events()
            game_logic()
            self.start_loop()
            self.update_screen()
        quit()
        sys.exit() #This is to ensure the code exits completely, preventing any lingering processes.
