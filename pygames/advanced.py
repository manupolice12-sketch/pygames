"""
Advanced Level Game Components

This module provides advanced game functionality including animation and player
controls. It combines features from both power1 and power2 engines along with
medium-level components.

Usage:
    from pygames.advanced import Player, Animator
    player = Player(app, x, y)
"""

# Import advanced features from power2 engine and medium-level components
from .pygames_engine.engines.power2 import *
from .medium import*
from .__init__ import*
