"""
Player Module - Player Character Control

This module provides the Player class which extends PhysicSprite with
player-specific controls including keyboard movement and jumping.

Classes:
    Player: Player character with input handling

Usage:
    from pygames_engine.engines.power2.player import Player
    player = Player(pgs, x, y)
"""

from ..power1.physics import PhysicSprite


class Player(PhysicSprite):
    """A player character with keyboard movement and jump controls."""

    def __init__(self, pgs, x, y, width=40, height=60, color="blue", speed=5,
                 left="left", right="right", jump="space"):
        """Initialize a player character.

        Args:
            pgs: The Game instance
            x: Initial X position
            y: Initial Y position
            width: Width in pixels (default: 40)
            height: Height in pixels (default: 60)
            color: Fill color (default: "blue")
            speed: Movement speed in pixels per frame (default: 5)
            left: Key name for moving left (default: "left")
            right: Key name for moving right (default: "right")
            jump: Key name for jumping (default: "space")

        Raises:
            TypeError: If speed is not a number
            ValueError: If speed is negative
        """
        super().__init__(pgs, x, y, width, height, color)

        if not isinstance(speed, (int, float)):
            pgs._log(
                f"TypeError: Player speed must be a number (got {type(speed).__name__})",
                "ERROR"
            )
            raise TypeError(f"speed must be a number, got {type(speed).__name__}")

        if speed < 0:
            pgs._log(f"ValueError: Player speed must be positive (got {speed})", "ERROR")
            raise ValueError(f"speed must be positive, got {speed}")

        self.speed = speed
        self.key_left = left
        self.key_right = right
        self.key_jump = jump

        pgs._log(f"Player initialized at ({x}, {y}), speed={speed}, keys=({left}, {right}, {jump})", "SUCCESS")

    def handle_input(self):
        """Process keyboard input for movement and jumping."""
        if self.pgs.check_key_pressed(self.key_left):
            self.vel_x = -self.speed
            self.pgs._log(f"Player moving left: vel_x={self.vel_x}", "INFO")
        elif self.pgs.check_key_pressed(self.key_right):
            self.vel_x = self.speed
            self.pgs._log(f"Player moving right: vel_x={self.vel_x}", "INFO")
        else:
            self.vel_x = 0

        if self.pgs.check_key_pressed(self.key_jump):
            self.jump()

    def update(self, solids=None):
        """Called automatically by pygame Groups each frame.

        Args:
            solids: Iterable of solid sprites (passed from Game.start_loop()).
        """
        self.handle_input()
        self.apply_physics(list(solids) if solids else [])
        self.pgs._log(f"Player updated at ({self.rect.x}, {self.rect.y})", "INFO")

    def tick(self):
        """Deprecated manual update. Use game.start() and let update() be called automatically."""
        self.pgs._log("tick() called manually — consider using game.start() instead", "INFO")
        self.handle_input()