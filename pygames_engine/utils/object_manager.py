try:
    from pygame import*
except ImportError:
    raise ImportError("pygame or pygame-ce is required. Install it with: pip install pygame or pip install pygame-ce")


class SSprites(sprite.Sprite):
    """Base class for sprites in the engine, providing basic functionality."""
    def __init__(self, pgs_instance, x, y, image_path=None, source=None):
        super().__init__()
        if not hasattr(pgs_instance, 'screen') or not hasattr(pgs_instance, 'objects'):
            raise TypeError(f"'{pgs_instance}' is not a valid Game instance.")
        if not isinstance(x, (int, float)) or not isinstance(y, (int, float)):
            raise TypeError(f"x and y must be numbers, got x={type(x).__name__}, y={type(y).__name__}")
        self.pgs = pgs_instance
        if source:
            if isinstance(source, Surface):
                self.image = source
            else:
                try:
                    self.image = image.load(source).convert_alpha()
                except (FileNotFoundError, error):
                    self. raise_file_not_found_error(source)
        elif image_path:
            try:
                self.image = image.load(image_path).convert_alpha()
            except:
                self. raise_file_not_found_error(image_path)
        else:
            self.image = Surface((50, 50))
            self.image.fill("white")

        self.rect = self.image.get_rect(topleft=(x, y))

    def  raise_file_not_found_error(self, name):
        raise FileNotFoundError(f"The file '{name}' does not exist, check the file.")

    def draw(self):
        self.pgs.screen.blit(self.image, self.rect)
        
    def create_surface(self, width,height, color=None, alpha=None):
        if alpha:
            surface = Surface((width, height), SRCALPHA)
        else:
            surface = Surface((width,height))
            surface = surface.convert_alpha()
            if color:
                try:
                    surface.fill(color)
                except (ValueError, TypeError):
                    raise NameError(f"The color '{color}' does not exist, please check the color you typed.")
        return surface

    def move(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy
