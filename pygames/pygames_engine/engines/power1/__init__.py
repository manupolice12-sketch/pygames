"""
Power1 Engine - Physics System

This module provides the physics-based sprite system for the game engine.
It includes the PhysicSprite class which extends basic sprites with
gravity, collision detection, and movement capabilities.

Usage:
    from pygames_engine.engines.power1 import PhysicSprite
    sprite = PhysicSprite(app, x, y, width, height)
"""

# Export physics functionality
from .physics import*