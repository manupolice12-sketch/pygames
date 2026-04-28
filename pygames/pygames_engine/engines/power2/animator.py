"""
Animator Module - Sprite Animation System

This module provides the Animator class for managing sprite animations.
It supports frame-based animation, hover effects, and rotation.

Classes:
    Animator: Manages sprite animations and effects

Usage:
    from pygames_engine.engines.power2.animator import Animator
    animator = Animator(sprite)
    animator.refresh()
"""

import time
import math
import pygame as pg


class Animator:
    """A class that manages sprite animations, allowing for frame updates based on the target sprite's state and providing
       additional animation effects like hovering and rotating."""
    
    def __init__(self, target, animation_speed=0.1):
        """Initialize the animator for a sprite.
        
        Args:
            target: The sprite to animate (must have 'image' and optionally 'state' and 'animations' attributes)
            animation_speed: Time in milliseconds between frame updates (default: 0.1)
        """
        self.target = target
        self.animation_speed = animation_speed
        self.current_frame = 0
        self.last_update_time = pg.time.get_ticks()
        self.base_y = getattr(target, 'y', 0)
        self.base_image = getattr(target, 'image', None)
        self.last_state = getattr(target, 'state', None)
        self.base_image = target.image.copy()

    def refresh(self):
        """Update the animation frame based on the sprite's current state.
        
        This method should be called each frame to update animations.
        It cycles through frames in the animations dictionary based on
        the sprite's current state.
        """
        if not hasattr(self.target, 'animations') or not hasattr(self.target, 'state'):
            return

        state = self.target.state
        if state not in self.target.animations:
            return

        if self.target.state != self.last_state:
            self.current_frame = 0
            self.last_state = self.target.state
            self.last_update_time = pg.time.get_ticks()

        current_time = pg.time.get_ticks()
        if current_time - self.last_update_time > self.animation_speed:
            frames = self.target.animations[state]
            if not frames:
                return
            self.current_frame = (self.current_frame + 1) % len(frames)
            self.target.image = frames[self.current_frame]
            self.last_update_time = current_time

    def hover(self, amplitude=5, speed=5):
        """Apply a hovering effect to the sprite.
        
        The sprite will move up and down in a smooth sine wave pattern.
        
        Args:
            amplitude: Maximum distance to move up/down in pixels (default: 5)
            speed: Speed of the hover animation (default: 5)
        """
        self.target.rect.y = self.base_y + math.sin(pg.time.get_ticks() * speed) * amplitude

    def rotate_loop(self, speed=100):
        """Continuously rotate the sprite.
        
        The sprite will rotate in a full 360 degree loop.
        
        Args:
            speed: Rotation speed (default: 100)
        """
        angle = (pg.time.get_ticks() * speed) % 360
        self.target.image = pg.transform.rotate(self.base_image, angle)
    

    def set_speed(self, speed):
        """Set the animation frame update speed.
        
        Args:
            speed: Time in milliseconds between frame updates
        """
        self.animation_speed = speed
