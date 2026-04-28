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
from ...pygames import*

class Player(PhysicSprite):
    """A player class that extends PhysicSprite and incorporates player-specific properties and behaviors, 
      such as movement controls and jumping mechanics."""
    
    def __init__(self, app, x, y, width=40, height=60, color="blue", speed=5,
                 left="left", right="right", jump="space"):
        """Initialize a player character.
        
        Args:
            app: The Game instance
            x: Initial X position
            y: Initial Y position
            width: Width of the player in pixels (default: 40)
            height: Height of the player in pixels (default: 60)
            color: Fill color for the player (default: "blue")
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
            raise TypeError(f"speed must be a number, got {type(speed).__name__}")
        if speed < 0:
            raise ValueError(f"speed must be positive, got {speed}")
        self.speed = speed
        self.key_left = left
        self.key_right = right
        self.key_jump = jump

    def handle_input(self):
        """Handle player input for movement and jumping left and right movement based on the arror keys and jumping based on
        the assigned space key"""
        if self.pgs.check_key_pressed(self.key_left):
            self.vel_x = -self.speed
        elif self.pgs.check_key_pressed(self.key_right):
            self.vel_x = self.speed
        else:
            self.vel_x = 0
        if self.pgs.check_key_pressed(self.key_jump):
            self.jump()

    def tick(self):
        """Update player state each frame.
        
        This method should be called each frame to process player input
        and update the player's position.
        """
        self.handle_input()