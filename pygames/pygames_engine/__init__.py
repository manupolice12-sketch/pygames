"""
Pygames Engine Package - Core Game Engine

This package contains the core game engine implementation including:
- Main Game class for game initialization and loop management
- Sprite classes for game objects
- Physics and animation systems

Submodules:
    - pygames: Main Game class and core functionality
    - engines: Game engines (power1 for physics, power2 for animation)
    - utils: Utility functions and object management
"""

# Re-export core game functionality
from .pygames import*
from .utils.object_manager import*