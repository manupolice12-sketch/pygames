"""
Pygames Package - Simplified Game Development Framework

This package provides a simplified interface for creating 2D games using Pygame.
It re-exports core functionality from the pygames_engine subpackage for easy access.

Modules:
    - pygames_engine: Core game engine implementation
    - utils: Utility functions for game development

Usage:
    from pygames import Game
    game = Game(800, 600, "My Game")
    game.mainloop(game_logic)
"""

# Re-export all public symbols from the game engine module
# This provides a simplified import path for users
from pygames_engine.pygames import*
from pygames_engine.utils import*