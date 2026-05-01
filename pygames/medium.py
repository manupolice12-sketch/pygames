"""
Medium Level Game Components

This module provides intermediate-level game functionality that builds upon
the basic engine. It re-exports physics-based sprites from the power1 engine.

Usage:
    from pygames.medium import PhysicSprite
    player = PhysicSprite(app, x, y, width, height)
"""

# Import physics sprite functionality from the power1 engine
# This provides a higher-level abstraction for physics-based game objects
from .pygames_engine.engines.power1 import*
from .__init__ import*