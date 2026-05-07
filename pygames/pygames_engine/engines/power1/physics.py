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
    raise ImportError(
        "pygame or pygame-ce is required. Install it with: pip install pygame-ce"
    )

from ...utils.object_manager import SSprites


class PhysicSprite(SSprites):
    """A sprite that incorporates basic physics: gravity, velocity, and
    collision detection against solid objects."""

    def __init__(self, app, x, y, width=50, height=50, color="red",
                 gravity=0.8, max_fall_speed=20, **kwargs):
        """Initialize a physics-enabled sprite.

        Args:
            app: The Game instance
            x: Initial X position
            y: Initial Y position
            width: Width of the sprite in pixels (default: 50)
            height: Height of the sprite in pixels (default: 50)
            color: Fill color (default: "red")
            gravity: Gravity acceleration per frame (default: 0.8)
            max_fall_speed: Terminal velocity cap (default: 20)
        """
        super().__init__(app, x, y)

        if not isinstance(width, (int, float)) or not isinstance(height, (int, float)):
            app._log(
                f"TypeError: Width/Height must be numbers "
                f"(got {type(width).__name__})", "ERROR"
            )
            raise TypeError(
                f"width and height must be numbers, "
                f"got width={type(width).__name__}, height={type(height).__name__}"
            )

        self.image = app.create_surface(width, height, color=color)
        self.rect = self.image.get_rect(topleft=(x, y))

        self.vel_y = 0.0
        self.vel_x = 0.0

        self.gravity = gravity
        self.max_fall_speed = max_fall_speed
        self.on_ground = False

        app._log(f"PhysicSprite created at ({x}, {y}) with gravity {gravity}", "SUCCESS")

    def update(self, solids=None):
        """Called automatically by pygame Groups each frame.

        Applies physics against the provided solids.

        Args:
            solids: Iterable of solid sprites (passed from Game.start_loop()).
        """
        self.apply_physics(list(solids) if solids else [])

    def apply_physics(self, solids=None, gravity=True):
        """Apply one frame of physics: gravity, velocity, and collision resolution.

        Vertical and horizontal axes are resolved in separate passes to avoid
        corner-clipping bugs.

        Args:
            solids: List of solid objects to collide with.
            gravity: Whether to apply gravity this frame (default: True).
        """
        if solids is None:
            solids = []

        # --- Gravity ---
        if gravity:
            self.vel_y = min(self.vel_y + self.gravity, self.max_fall_speed)

        # --- Vertical pass ---
        self.rect.y += int(self.vel_y)
        self.on_ground = False

        for solid in solids:
            if solid is self:
                continue
            if self.rect.colliderect(solid.rect):
                if self.vel_y > 0:
                    self.rect.bottom = solid.rect.top
                    self.vel_y = 0.0
                    self.on_ground = True
                elif self.vel_y < 0:
                    self.rect.top = solid.rect.bottom
                    self.vel_y = 0.0

        # --- Screen floor ---
        if self.rect.bottom >= self.pgs.screen_height:
            self.rect.bottom = self.pgs.screen_height
            self.vel_y = 0.0
            self.on_ground = True

        # --- Horizontal pass ---
        self.rect.x += int(self.vel_x)

        for solid in solids:
            if solid is self:
                continue
            if self.rect.colliderect(solid.rect):
                if self.vel_x > 0:
                    self.rect.right = solid.rect.left
                elif self.vel_x < 0:
                    self.rect.left = solid.rect.right

    def jump(self, force=15):
        """Make the sprite jump (only when on the ground).

        Args:
            force: Upward velocity to apply (default: 15).

        Raises:
            TypeError: If force is not a number.
        """
        if not isinstance(force, (int, float)):
            self.pgs._log(
                f"Jump Error: Force must be a number (got {type(force).__name__})",
                "ERROR"
            )
            raise TypeError(f"jump force must be a number, got {type(force).__name__}")

        if self.on_ground:
            self.vel_y = -force
            self.on_ground = False
            self.pgs._log(f"Jump executed with force: {force}", "SUCCESS")
        else:
            self.pgs._log("Jump ignored: Sprite not on ground", "INFO")
