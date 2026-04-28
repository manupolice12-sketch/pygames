"""
Physics Module - Sprite Physics System

This module provides the PhysicSprite class which extends the base sprite
class with physics properties like gravity, velocity, and collision detection.

Classes:
    PhysicSprite: Sprite with physics capabilities

Usage:
    from pygames_engine.engines.power1.physics import PhysicSprite
    sprite = PhysicSprite(app, x, y, width, height, color="red")
"""

try:
    import pygame as pg 
except ImportError:
    # This checks if the Pygame library is installed on your computer
    raise ImportError("pygame or pygame-ce is required. Install it with: pip install pygame-ce")

# This connects the physics class to the engine's base object manager
from ...utils.object_manager import SSprites

class PhysicSprite(SSprites):
    """A sprite class that extends SSprites and incorporates basic physics properties and behaviors, such as gravity and 
    collision detection."""
    
    def __init__(self, app, x, y, width=50, height=50, color="red", gravity=0.8, max_fall_speed=20,**kwargs):
        """Initialize a physics-enabled sprite.
        
        Args:
            app: The Game instance
            x: Initial X position
            y: Initial Y position
            width: Width of the sprite in pixels
            height: Height of the sprite in pixels
            color: Fill color for the sprite (default: "red")
            gravity: Gravity acceleration applied each frame (default: 0.8)
            max_fall_speed: Maximum falling speed (default: 20)
            **kwargs: Additional keyword arguments
        """
        super().__init__(app, x, y)
        
        # We ensure the size values are actual numbers to prevent the game from crashing
        if not isinstance(width, (int, float)) or not isinstance(height, (int, float)):
            # If the size is wrong, we log an error so the developer knows why it failed
            app._log(f"TypeError: Width/Height must be numbers (got {type(width).__name__})", "ERROR")
            raise TypeError(f"width and height must be numbers, got width={type(width).__name__}, height={type(height).__name__}")
        
        # Create the physical body and its hit-box (rect) for collision detection
        self.image = app.create_surface(width, height, color=color)
        self.rect = self.image.get_rect(topleft=(x, y))
        
        # Velocity variables: vel_y is vertical speed, vel_x is horizontal speed
        self.vel_y = 0
        self.vel_x = 0
        
        # Physics constants that define how the object moves in the world
        self.gravity = gravity
        self.max_fall_speed = max_fall_speed
        
        # This tracks if the sprite is currently standing on a solid surface
        self.on_ground = False
        
        # Log successful creation of the physics object
        app._log(f"PhysicSprite created at ({x}, {y}) with gravity {gravity}", "SUCCESS")

    def apply_physics(self, solids=None, gravity=True):
        """Apply physics to the sprite, including gravity and collision detection.
        
        This method is called automatically each frame for sprites that have
        physics enabled. It handles:
        - Gravity application
        - Velocity limiting
        - Collision detection with solid objects
        - Screen boundary handling
        
        Args:
            solids: List of solid objects to check collisions against
            gravity: Whether to apply gravity (default: True)
        """
        if solids is None:
            solids = []
        
        # 1. APPLY GRAVITY
        # Pull the object downward by increasing its vertical speed
        if gravity:
            self.vel_y += self.gravity
            
        # 2. TERMINAL VELOCITY
        # Cap the speed so the object doesn't fall too fast (terminal velocity)
        if self.vel_y > self.max_fall_speed:
            self.vel_y = self.max_fall_speed
            
        # 3. VERTICAL MOVEMENT & COLLISIONS
        # Move vertically and check for floor/ceiling collisions
        self.rect.y += self.vel_y
        self.on_ground = False # Assume we are in the air until we hit a floor
        
        for solid in solids:
            # Check if our hit-box touches a solid platform
            if self.rect.colliderect(solid.rect):
                if self.vel_y > 0: # If falling down, snap to the top of the floor
                    self.rect.bottom = solid.rect.top
                    self.vel_y = 0
                    self.on_ground = True # We are now standing on something
                elif self.vel_y < 0: # If jumping up, snap to the bottom of the ceiling
                    self.rect.top = solid.rect.bottom
                    self.vel_y = 0
                    
        # 4. HORIZONTAL MOVEMENT & COLLISIONS
        # Move horizontally and check for wall collisions
        self.rect.x += self.vel_x
        for solid in solids:
            if self.rect.colliderect(solid.rect):
                if self.vel_x > 0: # Hit a wall on the right
                    self.rect.right = solid.rect.left
                elif self.vel_x < 0: # Hit a wall on the left
                    self.rect.left = solid.rect.right
                    
        # 5. SCREEN BOUNDARY
        # Prevent the object from falling off the bottom of the game window
        if self.rect.bottom > self.pgs.screen_height:
            self.rect.bottom = self.pgs.screen_height
            self.vel_y = 0
            # If this is the first time hitting the screen floor, log the event
            if not self.on_ground:
                self.on_ground = True
                self.pgs._log("Sprite reached screen floor boundary", "INFO")

    def jump(self, force=15):
        """Make the sprite jump.
        
        Only works when the sprite is on the ground (not in the air).
        
        Args:
            force: Upward velocity to apply (default: 15)
            
        Raises:
            TypeError: If force is not a number
        """
        # Ensure the jump power is a valid number
        if not isinstance(force, (int, float)):
            self.pgs._log(f"Jump Error: Force must be a number (got {type(force).__name__})", "ERROR")
            raise TypeError(f"jump force must be a number, got {type(force).__name__}")
        
        # Launch upward only if standing on a solid surface or the floor
        if self.on_ground:
            # A negative value moves the object UP in the Pygame coordinate system
            self.vel_y = -force
            self.on_ground = False
            self.pgs._log(f"Jump executed with force: {force}", "SUCCESS")
        else:
            # Log that the jump was ignored because the sprite was mid-air
            self.pgs._log("Jump ignored: Sprite not on ground", "INFO")