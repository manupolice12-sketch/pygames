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

import math
import pygame as pg


class Animator:
    """Manages sprite animations, hover, and rotation effects."""

    def __init__(self, target, animation_speed=100):
        """Initialize the animator for a sprite.

        Args:
            target: The sprite to animate (must have 'image'; optionally
                    'state' and 'animations').
            animation_speed: Milliseconds between frame updates (default: 100).
        """
        self.target = target
        self.animation_speed = animation_speed
        self.current_frame = 0
        self.last_update_time = pg.time.get_ticks()
        self.base_y = getattr(target, 'rect', None) and target.rect.y or getattr(target, 'y', 0)
        self.base_image = target.image.copy()
        self.last_state = getattr(target, 'state', None)

        if hasattr(target, 'pgs'):
            target.pgs._log(f"Animator initialized for {type(target).__name__}", "SUCCESS")

    def refresh(self, state=None):
        """Update the sprite's image based on its current animation state.

        Args:
            state: Animation state name (e.g. 'walk', 'idle'). Falls back to
                   target.state if not provided.
        """
        if state is None:
            state = getattr(self.target, 'state', None)

        if state != self.last_state:
            self.current_frame = 0
            self.last_state = state
            if hasattr(self.target, 'pgs'):
                self.target.pgs._log(f"Animation state changed to: {state}", "INFO")

        if state is None or not hasattr(self.target, 'animations'):
            if hasattr(self.target, 'pgs'):
                self.target.pgs._log("Animation skipped: no state or animations defined", "INFO")
            return

        frames = self.target.animations.get(state)
        if not frames:
            if hasattr(self.target, 'pgs'):
                self.target.pgs._log(f"Animation skipped: no frames found for state '{state}'", "INFO")
            return

        current_time = pg.time.get_ticks()
        if current_time - self.last_update_time >= self.animation_speed:
            self.current_frame = (self.current_frame + 1) % len(frames)
            self.target.image = frames[self.current_frame]
            self.last_update_time = current_time
            if hasattr(self.target, 'pgs'):
                self.target.pgs._log(
                    f"Animation frame advanced: state='{state}', frame={self.current_frame}", "INFO"
                )

    def hover(self, amplitude=5, speed=0.005):
        """Apply a smooth sine-wave hover effect to the sprite.

        Do not use on sprites that also have apply_physics running,
        as the two will conflict.

        Args:
            amplitude: Maximum vertical displacement in pixels (default: 5).
            speed: Oscillation speed in cycles per millisecond (default: 0.005).
        """
        self.target.rect.y = int(
            self.base_y + math.sin(pg.time.get_ticks() * speed) * amplitude
        )
        if hasattr(self.target, 'pgs'):
            self.target.pgs._log(
                f"Hover applied: rect.y={self.target.rect.y}, amplitude={amplitude}, speed={speed}",
                "INFO"
            )

    def rotate_loop(self, speed=0.1):
        """Continuously rotate the sprite around its centre.

        Args:
            speed: Degrees per millisecond (default: 0.1).
        """
        angle = (pg.time.get_ticks() * speed) % 360
        rotated = pg.transform.rotate(self.base_image, angle)
        center = self.target.rect.center
        self.target.image = rotated
        self.target.rect = rotated.get_rect(center=center)
        if hasattr(self.target, 'pgs'):
            self.target.pgs._log(f"Rotation applied: angle={angle:.1f}°", "INFO")