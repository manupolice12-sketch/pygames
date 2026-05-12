"""
Advanced Level Game Components

Provides the Player and Animator classes for full-featured game objects
with physics, keyboard controls, and sprite animation.

Usage:
    from pygames.advanced import Player, Animator
    player = Player(app, x, y)
    anim = Animator(player)
"""

from .pygames_engine.engines.power2.player import Player
from .pygames_engine.engines.power2.animator import Animator
from .pygames_engine.engines.power1.physics import PhysicSprite
from .pygames_engine.pygames import Game

__all__ = ["Player", "Animator", "PhysicSprite", "Game"]
