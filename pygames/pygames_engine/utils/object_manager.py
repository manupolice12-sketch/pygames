"""
Object Manager Module - Base Sprite Classes

This module provides the base sprite class SSprites which is the foundation
for all game objects in the engine. It handles image loading, positioning,
and basic sprite functionality.

Classes:
    SSprites: Base sprite class for all game objects
"""

try:
    from pygame import sprite, Surface, image, error as pg_error
except ImportError:
    raise ImportError(
        "pygame or pygame-ce is required. "
        "Install it with: pip install pygame-ce"
    )


class SSprites(sprite.Sprite):
    """Base class for sprites in the engine, providing basic functionality."""

    def __init__(self, pgs_instance, x, y, image_path=None, source=None):
        """Initialize a sprite.

        Args:
            pgs_instance: The Game instance
            x: Initial X position
            y: Initial Y position
            image_path: Optional path to an image file to load
            source: Optional pygame Surface to use as the sprite image

        Raises:
            TypeError: If pgs_instance is not a valid Game instance
            TypeError: If x or y are not numbers
            FileNotFoundError: If the image file doesn't exist
        """
        super().__init__()

        if not hasattr(pgs_instance, 'screen') or not hasattr(pgs_instance, 'objects'):
            raise TypeError(f"'{pgs_instance}' is not a valid Game instance.")

        if not isinstance(x, (int, float)) or not isinstance(y, (int, float)):
            pgs_instance._log(
                f"TypeError: Coordinates must be numbers (got x={type(x).__name__})",
                "ERROR"
            )
            raise TypeError(
                f"x and y must be numbers, got x={type(x).__name__}, y={type(y).__name__}"
            )

        self.pgs = pgs_instance

        if source:
            if isinstance(source, Surface):
                self.image = source
            else:
                try:
                    self.image = image.load(source).convert_alpha()
                    self.pgs._log(f"Sprite source loaded from: {source}", "SUCCESS")
                except (FileNotFoundError, pg_error):
                    self.pgs._log(f"Failed to load source: {source}", "ERROR")
                    raise FileNotFoundError(
                        f"The file '{source}' does not exist, check the file."
                    )
        elif image_path:
            try:
                self.image = image.load(image_path).convert_alpha()
                self.pgs._log(f"Sprite image loaded from: {image_path}", "SUCCESS")
            except (FileNotFoundError, pg_error):
                self.pgs._log(f"Image path not found: {image_path}", "ERROR")
                raise FileNotFoundError(
                    f"The file '{image_path}' does not exist, check the file."
                )
        else:
            self.image = self.pgs.create_surface(50, 50, color="white")

        self.rect = self.image.get_rect(topleft=(x, y))
        self.pgs._log(f"Sprite initialized at position ({x}, {y})", "SUCCESS")

    def draw(self):
        """Draw the sprite to the screen.

        This method is called automatically each frame for all active sprites.
        """
        self.pgs.screen.blit(self.image, self.rect)

    def move(self, dx, dy):
        """Move the sprite by a relative amount.

        Args:
            dx: Change in X position (positive = right)
            dy: Change in Y position (positive = down)
        """
        self.rect.x += dx
        self.rect.y += dy
