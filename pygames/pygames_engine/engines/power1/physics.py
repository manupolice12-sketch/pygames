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
    """
    A game object that reacts to gravity and can collide with solid platforms.
    It tells the game engine what's happening through a logging system.
    """
    
    def __init__(self, app, x, y, width=50, height=50, color="red", gravity=0.8, max_fall_speed=20, **kwargs):
        """
        Sets up the sprite with its starting position, size, and physics rules.
        """
        super().__init__(app, x, y)
        
        # We ensure the size values are actual numbers to prevent the game from crashing
        if not isinstance(width, (int, float)) or not isinstance(height, (int, float)):
            # If the size is wrong, we log an error so you know why it crashed
            app._log(f"TypeError: Width/Height must be numbers (got {type(width).__name__})", "ERROR")
            raise TypeError(f"width and height must be numbers, got width={type(width).__name__}, height={type(height).__name__}")
        
        # This creates the physical 'body' and 'hit-box' (rect) of the object
        self.image = app.create_surface(width, height, color=color)
        self.rect = self.image.get_rect(topleft=(x, y))
        
        # Movement speeds: vel_y is up/down speed, vel_x is left/right speed
        self.vel_y = 0
        self.vel_x = 0
        
        # Physics rules: How strong gravity is and how fast the object can fall
        self.gravity = gravity
        self.max_fall_speed = max_fall_speed
        
        # This tracks if the sprite is currently standing on a solid surface
        self.on_ground = False
        
        # Tell the system we successfully created the object
        app._log(f"PhysicSprite created at ({x}, {y}) with gravity {gravity}", "SUCCESS")

    def apply_physics(self, solids=None, gravity=True):
        """
        This calculates gravity, movement, and collisions every frame of the game.
        """
        if solids is None:
            solids = []
        
        # 1. APPLY GRAVITY
        # We pull the object downward by increasing its vertical speed (vel_y)
        if gravity:
            self.vel_y += self.gravity
            
        # 2. TERMINAL VELOCITY
        # We cap the speed so the object doesn't fall through the floor by moving too fast
        if self.vel_y > self.max_fall_speed:
            self.vel_y = self.max_fall_speed
            
        # 3. VERTICAL MOVEMENT & COLLISIONS
        # Move the object up or down first
        self.rect.y += self.vel_y
        self.on_ground = False # Assume we are in the air until we hit a floor
        
        for solid in solids:
            # Check if our hit-box is touching a solid platform
            if self.rect.colliderect(solid.rect):
                if self.vel_y > 0: # If we are falling down
                    self.rect.bottom = solid.rect.top # Snap us to the top of the floor
                    self.vel_y = 0 # Stop moving down
                    self.on_ground = True # We are now standing on something
                elif self.vel_y < 0: # If we are moving up (hitting a ceiling)
                    self.rect.top = solid.rect.bottom # Snap us to the bottom of the ceiling
                    self.vel_y = 0 # Stop moving up
                    
        # 4. HORIZONTAL MOVEMENT & COLLISIONS
        # Move the object left or right
        self.rect.x += self.vel_x
        for solid in solids:
            if self.rect.colliderect(solid.rect):
                if self.vel_x > 0: # If moving right, stop at the left side of the wall
                    self.rect.right = solid.rect.left
                elif self.vel_x < 0: # If moving left, stop at the right side of the wall
                    self.rect.left = solid.rect.right
                    
        # 5. SCREEN BOUNDARY
        # Prevent the object from falling off the very bottom of the game window
        if self.rect.bottom > self.pgs.screen_height:
            self.rect.bottom = self.pgs.screen_height
            self.vel_y = 0
            # If this is the first time we hit the floor, log it
            if not self.on_ground:
                self.on_ground = True
                self.pgs._log("Sprite reached screen floor boundary", "INFO")

    def jump(self, force=15):
        """
        Launches the sprite upward, but only if it is standing on the ground.
        """
        # Ensure the jump power is a number
        if not isinstance(force, (int, float)):
            self.pgs._log(f"Jump Error: Force must be a number (got {type(force).__name__})", "ERROR")
            raise TypeError(f"jump force must be a number, got {type(force).__name__}")
        
        # You can only jump if you are standing on a solid object or the floor
        if self.on_ground:
            # In Pygame, a negative number moves you UP the screen
            self.vel_y = -force
            self.on_ground = False
            self.pgs._log(f"Jump executed with force: {force}", "SUCCESS")
        else:
            # Log this so you can see why your character isn't jumping in mid-air
            self.pgs._log("Jump ignored: Sprite not on ground", "INFO")