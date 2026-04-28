"""
Object Manager Module - Base Sprite Classes

This module provides the base sprite class SSprites which is the foundation
for all game objects in the engine. It handles image loading, positioning,
and basic sprite functionality.

Classes:
    SSprites: Base sprite class for all game objects

Usage:
    from pygames_engine.utils.object_manager import SSprites
    class MySprite(SSprites):
        pass
"""

try:
    from pygame import*
except ImportError:
    # This checks if the Pygame library is installed on your computer
    raise ImportError("pygame or pygame-ce is required. Install it with: pip install pygame or pip install pygame-ce")


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
        # This ensures the game engine is set up correctly before we add objects
        if not hasattr(pgs_instance, 'screen') or not hasattr(pgs_instance, 'objects'):
            raise TypeError(f"'{pgs_instance}' is not a valid Game instance.")
        
        # We check that the position coordinates are actual numbers to prevent errors
        if not isinstance(x, (int, float)) or not isinstance(y, (int, float)):
            pgs_instance._log(f"TypeError: Coordinates must be numbers (got x={type(x).__name__})", "ERROR")
            raise TypeError(f"x and y must be numbers, got x={type(x).__name__}, y={type(y).__name__}")
        
        self.pgs = pgs_instance
        
        # This section handles loading the visual look of your sprite
        if source:
            # If you provide a direct image surface or a specific source
            if isinstance(source, Surface):
                self.image = source
            else:
                try:
                    self.image = image.load(source).convert_alpha()
                    # Log that the source image was successfully loaded
                    self.pgs._log(f"Sprite source loaded from: {source}", "SUCCESS")
                except (FileNotFoundError, error):
                    # Log an error if the specific source file cannot be found
                    self.pgs._log(f"Failed to load source: {source}", "ERROR")
                    self.raise_file_not_found_error(source)
        elif image_path:
            # If you provide a file path to an image
            try:
                self.image = image.load(image_path).convert_alpha()
                # Log that the image was successfully loaded
                self.pgs._log(f"Sprite image loaded from: {image_path}", "SUCCESS")
            except:
                # Log an error if the image path is broken
                self.pgs._log(f"Image path not found: {image_path}", "ERROR")
                self.raise_file_not_found_error(image_path)
        else:
            # If no image is given, we create a simple white square as a placeholder
            self.image = self.pgs.create_surface(50, 50, color="white")

        # This defines the sprite's position and its hit-box on the screen
        self.rect = self.image.get_rect(topleft=(x, y))
        
        # Log that the sprite has been fully initialized at its starting position
        self.pgs._log(f"Sprite initialized at position ({x}, {y})", "SUCCESS")

    def raise_file_not_found_error(self, name):
        """Raise a FileNotFoundError with a descriptive message.
        
        Args:
            name: The name of the file that wasn't found
        """
        raise FileNotFoundError(f"The file '{name}' does not exist, check the file.")

    def draw(self):
        """Draw the sprite to the screen.
        
        This method is called automatically each frame for all active sprites.
        """
        # This puts the sprite's image onto the game window at its current position
        self.pgs.screen.blit(self.image, self.rect)

    def move(self, dx, dy):
        """Move the sprite by a relative amount.
        
        Args:
            dx: Change in X position (positive = right)
            dy: Change in Y position (positive = down)
        """
        # This changes the position by adding to the current coordinates
        self.rect.x += dx
        self.rect.y += dy