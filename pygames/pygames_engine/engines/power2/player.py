"""
Player Module - Player Character Control

This module provides the Player class which extends PhysicSprite with
player-specific controls including keyboard movement and jumping.

Classes:
    Player: Player character with input handling

Usage:
    from pygames_engine.engines.power2.player import Player
    player = Player(app, x, y)
"""

from ..power1.physics import PhysicSprite


class Player(PhysicSprite):
    """A player character with keyboard movement and jump controls."""

    def __init__(self, app, x, y, width=40, height=60, color="blue", speed=5,
                 left="left", right="right", jump="space"):
        """Initialize a player character.

        Args:
            app: The Game instance
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
        super().__init__(app, x, y, width, height, color)

        if not isinstance(speed, (int, float)):
            app._log(
                f"TypeError: Player speed must be a number (got {type(speed).__name__})",
                "ERROR"
            )
            raise TypeError(f"speed must be a number, got {type(speed).__name__}")

        if speed < 0:
            app._log(f"ValueError: Player speed must be positive (got {speed})", "ERROR")
            raise ValueError(f"speed must be positive, got {speed}")

        self.speed = speed
        self.key_left = left
        self.key_right = right
        self.key_jump = jump

        app._log(f"Player initialized at ({x}, {y}) with speed {speed}", "SUCCESS")

    def handle_input(self):
        """Process keyboard input for movement and jumping."""
        if self.pgs.check_key_pressed(self.key_left):
            self.vel_x = -self.speed
        elif self.pgs.check_key_pressed(self.key_right):
            self.vel_x = self.speed
        else:
            self.vel_x = 0

        if self.pgs.check_key_pressed(self.key_jump):
            self.jump()

    def update(self, solids=None):
        """Called automatically by pygame Groups each frame.

        Processes input first, then applies physics. This means you no longer
        need to call player.tick() manually — it is handled by the group.
        tick() is kept as an alias for backwards compatibility.

        Args:
            solids: Iterable of solid sprites (passed from Game.start_loop()).
        """
        self.handle_input()
        self.apply_physics(list(solids) if solids else [])

    def tick(self):
        """Process input and update physics for this frame.

        Kept for backwards compatibility. When the player is registered with
        game.start(), update() is called automatically and tick() is not
        needed. Only call tick() manually if you are managing the player
        outside of the engine loop.
        """
        self.handle_input()
