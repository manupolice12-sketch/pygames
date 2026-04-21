try:
    import pygame as pg 
except ImportError:
    raise ImportError("pygame or pygame-ce is required. Install it with: pip install pygame-ce")
from ...utils.object_manager import SSprites

class PhysicSprite(SSprites):
    """A sprite class that extends SSprites and incorporates basic physics properties and behaviors, such as gravity and 
    collision detection."""
    def __init__(self, app, x, y, width=50, height=50, color="red", gravity=0.8, max_fall_speed=20,**kwargs):
        super().__init__(app, x, y)
        if not isinstance(width, (int, float)) or not isinstance(height, (int, float)):
            raise TypeError(f"width and height must be numbers, got width={type(width).__name__}, height={type(height).__name__}")
        self.image = app.create_surface(width, height, color=color)
        self.rect = self.image.get_rect(topleft=(x, y))
        self.vel_y = 0
        self.vel_x = 0
        self.gravity = gravity
        self.max_fall_speed = max_fall_speed
        self.on_ground = False

    def apply_physics(self, solids=None, gravity=True):
        """Apply physics to the sprite, including gravity and collision detection."""
        if solids is None:
            solids = []
        
        if gravity:
            self.vel_y += self.gravity
            
        if self.vel_y > self.max_fall_speed:
            self.vel_y = self.max_fall_speed
            
        self.rect.y += self.vel_y
        self.on_ground = False
        
        for solid in solids:
            if self.rect.colliderect(solid.rect):
                if self.vel_y > 0:
                    self.rect.bottom = solid.rect.top
                    self.vel_y = 0
                    self.on_ground = True
                elif self.vel_y < 0:
                    self.rect.top = solid.rect.bottom
                    self.vel_y = 0
                    
        self.rect.x += self.vel_x
        for solid in solids:
            if self.rect.colliderect(solid.rect):
                if self.vel_x > 0:
                    self.rect.right = solid.rect.left
                elif self.vel_x < 0:
                    self.rect.left = solid.rect.right
                    
        if self.rect.bottom > self.pgs.screen_height:
            self.rect.bottom = self.pgs.screen_height
            self.vel_y = 0
            self.on_ground = True

    def jump(self, force=15):
        if not isinstance(force, (int, float)):
            raise TypeError(f"jump force must be a number, got {type(force).__name__}")
        if self.on_ground:
            self.vel_y = -force
            self.on_ground = False
