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
        
        # Logging initialization
        if hasattr(target, 'pgs'):
            target.pgs._log(f"Animator initialized for {type(target).__name__}", "SUCCESS")

    def refresh(self, state=None):
        """Update the sprite's image based on its current animation state.
        
        Args:
            state: The name of the animation state (e.g., 'walk', 'idle')
        """
        if state is None:
            state = getattr(self.target, 'state', None)
        
        if state != self.last_state:
            self.current_frame = 0
            self.last_state = state
            if hasattr(self.target, 'pgs'):
                self.target.pgs._log(f"Animation state changed to: {state}", "INFO")

        if state is None or not hasattr(self.target, 'animations'):
            return

        current_time = pg.time.get_ticks()
        if current_time - self.last_update_time > self.animation_speed:
            frames = self.target.animations.get(state)
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
        center = self.target.rect.center
        self.target.rect = self.target.image.get_rect(center=center)