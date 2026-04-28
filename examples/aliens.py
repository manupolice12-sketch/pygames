"""
Alien Invasion Example Game

This module demonstrates a complete game using the pygames engine.
It features a player ship that can shoot at aliens, aliens that drop bombs,
and a scoring system.

Game Controls:
    - Left/Right Arrow Keys: Move the player
    - Space: Shoot bullets

Features:
    - Player movement and shooting
    - Alien movement and bomb dropping
    - Collision detection
    - Score tracking
    - Sound effects

Usage:
    Run this file directly to play the game:
    python examples/aliens.py
"""

from pygames_engine import Game
from pygames.advanced import *
from os import path
import random

# Get the directory path for this file
base_dir = path.dirname(__file__)
assets = path.join(base_dir, 'assets')

# Create the game instance with 500x500 window
app = Game(500, 500, "Alien Invasion")
app.start_score_counter()
app.start_garbage_collecter()

# Load all required assets (images and sounds)
app.load_image("alien1", path.join(assets, "alien1.png"))
app.load_image("alien2", path.join(assets, "alien2.png"))
app.load_image("player", path.join(assets, "player1.gif"))
app.load_image("background", path.join(assets, "background.gif"))
app.load_sound("boom", path.join(assets, "boom.wav"))
app.load_image("bomb", path.join(assets, "bomb.gif"))
app.load_sound("background", path.join(assets, "house_lo.ogg"))

# Create the player sprite
player = Player(app, 225, 430, width=40, height=50, color="blue", speed=5, jump="up")
player.image = app.images["player"]
player.rect = player.image.get_rect(topleft=(225, 430))
player.gravity = 0  # Disable gravity for the player (top-down style game)
app.start(player)

# Initialize game object lists
bullets = []
bombs = []
aliens = []

# Alien grid configuration
ALIEN_ROWS = 2
ALIEN_COLS = 5
alien_dx = 2  # Horizontal movement speed for aliens

# Create the alien grid
for row in range(ALIEN_ROWS):
    for col in range(ALIEN_COLS):
        alien = PhysicSprite(app, 60 + col * 80, 40 + row * 60, width=40, height=40, gravity=0, max_fall_speed=0)
        alien.image = app.images["alien1"] if row % 2 == 0 else app.images["alien2"]
        alien.rect = alien.image.get_rect(topleft=(60 + col * 80, 40 + row * 60))
        aliens.append(alien)

# Cooldown timers to prevent excessive shooting/bombing
shoot_cooldown = 0
bomb_cooldown = 0

def game_logic():
    """Main game logic function - called each frame to update game state.
    
    This function handles:
    - Background music playback
    - Background image drawing
    - Player shooting (space key)
    - Alien bomb dropping
    - Bullet movement and collision
    - Bomb movement and collision
    - Alien movement and edge bouncing
    - Player updates
    """
    global shoot_cooldown, alien_dx, bomb_cooldown

    # Start background music on first frame
    if not hasattr(app, 'bg_started'):
        app.sounds["background"].play(loops=-1)
        app.bg_started = True

    # Draw the background image
    app.img("background", 0, 0, 500, 500)

    # Handle player shooting
    if app.check_key_pressed("space") and shoot_cooldown <= 0:
        bullet = PhysicSprite(app, player.rect.centerx - 4, player.rect.top - 10, width=8, height=16, color="red")
        bullets.append(bullet)
        shoot_cooldown = 20

    # Update shoot cooldown
    if shoot_cooldown > 0:
        shoot_cooldown -= 1

    # Handle alien bomb dropping
    if bomb_cooldown <= 0 and aliens:
        # Randomly select an alien to drop a bomb
        shooter = random.choice(aliens)
        bomb = PhysicSprite(app, shooter.rect.centerx - 4, shooter.rect.bottom, width=8, height=16, color="red")
        bombs.append(bomb)
        bomb.image = app.images["bomb"]
        bomb_cooldown = 60

    # Update bomb cooldown
    if bomb_cooldown > 0:
        bomb_cooldown -= 1

    # Update bullets - move up and check for collisions with aliens
    for bullet in bullets[:]:
        bullet.rect.y -= 10
        app.screen.blit(bullet.image, bullet.rect)
        if bullet.rect.bottom < 0:
            bullets.remove(bullet)
            continue
        for alien in aliens[:]:
            if bullet.rect.colliderect(alien.rect):
                app.play_sound("boom")
                app.score += 10
                aliens.remove(alien)
                bullets.remove(bullet)
                break

    # Update bombs - move down and check for collision with player
    for bomb in bombs[:]:
        bomb.rect.y += 6
        app.screen.blit(bomb.image, bomb.rect)
        if bomb.rect.top > 500:
            bombs.remove(bomb)
            continue
        if bomb.rect.colliderect(player.rect):
            app.score -= 5
            bombs.remove(bomb)

    # Handle alien movement and edge bouncing
    hit_edge = False
    for alien in aliens:
        alien.rect.x += alien_dx
        if alien.rect.right >= 490 or alien.rect.left <= 10:
            hit_edge = True

    # Reverse direction when any alien hits the edge
    if hit_edge:
        alien_dx *= -1
        # for alien in aliens:
        #     alien.rect.y += 20

    # Draw all aliens
    for alien in aliens:
        app.screen.blit(alien.image, alien.rect)

    # Update player (handle input)
    player.tick()

# Start the main game loop
app.mainloop(game_logic)