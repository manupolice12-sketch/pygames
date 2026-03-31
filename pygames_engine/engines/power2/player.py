from ..power1.physics import PhysicSprite
from ...pygames import Game

class Player(PhysicSprite):
    """A player class that extends PhysicSprite and incorporates player-specific properties and behaviors, 
      such as movement controls and jumping mechanics."""
    def __init__(self, app, x, y, width=40, height=60, color="blue", speed=5,
                 left="left", right="right", jump="space"):
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
        self.handle_input()