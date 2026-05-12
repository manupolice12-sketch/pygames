"""
Medium Level Game Components

Provides physics-enabled sprites for intermediate game development.

Usage:
    from pygames.medium import PhysicSprite
    sprite = PhysicSprite(app, x, y, width, height)
"""

from .pygames_engine.engines.power1.physics import PhysicSprite
from .pygames_engine.pygames import Game

__all__ = ["PhysicSprite", "Game"]
