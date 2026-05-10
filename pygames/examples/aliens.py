"""
Alien Invasion Example Game
============================
Demonstrates the engine using pygame Groups and LayeredUpdates.

Bullets and bombs are now registered with game.start() so they are
drawn and updated automatically each frame. The player is registered
at LAYER_PLAYER so it always appears in front of the alien grid.

Controls:
    Left / Right Arrow  — move the player
    Space               — shoot

Features demonstrated:
    - Layered drawing (background < aliens < player < bullets/UI)
    - Sprites registered with game.start() / game.make_solid()
    - remove_from_game() / kill() for clean sprite removal
    - Automatic per-frame update() via Group
    - Score tracking
    - Sound effects
    - Garbage collection for off-screen sprites
"""

from pygames.advanced import Player, PhysicSprite, Game
from pygames.pygames_engine.pygames import *
from os import path
import random

# Setup

base_dir = path.dirname(__file__)
assets   = path.join(base_dir, 'assets')
game = Game(500, 500, "Alien Invasion")
game.start_score_counter()
game.start_garbage_collector()
game.enable_logging()
game.load_image("alien1",     path.join(assets, "alien1.png"))
game.load_image("alien2",     path.join(assets, "alien2.png"))
game.load_image("player",     path.join(assets, "player1.gif"))
game.load_image("background", path.join(assets, "background.gif"))
game.load_image("bomb",       path.join(assets, "bomb.gif"))
game.load_sound("boom",       path.join(assets, "boom.wav"))
game.load_sound("background", path.join(assets, "house_lo.ogg"))

# Player

player = Player(game, 225, 430, width=40, height=50, color="blue", speed=5, jump="up")
player.image = game.images["player"]
player.rect  = player.image.get_rect(topleft=(225, 430))
player.gravity = 0  # Top-down style — no gravity on the player

# Registered at LAYER_PLAYER so it draws in front of aliens and background.
# update() is called automatically each frame — no need to call player.tick().
game.start(player, layer=LAYER_PLAYER)

# Aliens

ALIEN_ROWS = 2
ALIEN_COLS = 5
alien_dx   = 2

aliens = []
for row in range(ALIEN_ROWS):
    for col in range(ALIEN_COLS):
        x = 60 + col * 80
        y = 40 + row * 60
        alien = PhysicSprite(game, x, y, width=40, height=40, gravity=0, max_fall_speed=0)
        alien.image = game.images["alien1"] if row % 2 == 0 else game.images["alien2"]
        alien.rect  = alien.image.get_rect(topleft=(x, y))
        aliens.append(alien)
        # Registered at LAYER_DEFAULT — drawn behind the player.
        game.start(alien, layer=LAYER_DEFAULT)

# Cooldown state

shoot_cooldown = 0
bomb_cooldown  = 0

# Game logic 

def game_logic():
    """Called once per frame. Handles bullets, bombs, alien movement,
    and collision. Drawing and physics are handled by the engine groups."""
    global shoot_cooldown, alien_dx, bomb_cooldown

    # Background music — start once
    if not hasattr(game, 'bg_started'):
        game.sounds["background"].play(loops=-1)
        game.bg_started = True

    # Draw background image 
    game.img("background", 0, 0, 500, 500)

    # Player shooting 
    if game.check_key_pressed("space") and shoot_cooldown <= 0:
        bullet = PhysicSprite(
            game, player.rect.centerx - 4, player.rect.top - 10,
            width=8, height=16, color="red"
        )
        # Bullets travel upward under manual control — disable gravity
        bullet.gravity = 0
        # Registered above the player layer so they appear on top
        game.start(bullet, layer=LAYER_UI)
        shoot_cooldown = 20

    if shoot_cooldown > 0:
        shoot_cooldown -= 1

    #  Alien bombs 
    if bomb_cooldown <= 0 and aliens:
        shooter = random.choice(aliens)
        bomb = PhysicSprite(
            game, shooter.rect.centerx - 4, shooter.rect.bottom,
            width=8, height=16, color="orange"
        )
        bomb.image  = game.images["bomb"]
        bomb.gravity = 0
        game.start(bomb, layer=LAYER_DEFAULT)
        bomb_cooldown = 60

    if bomb_cooldown > 0:
        bomb_cooldown -= 1

    #  Bullet movement and collisions 
    for bullet in list(game.objects.get_sprites_from_layer(LAYER_UI)):
        bullet.rect.y -= 10
        # Collide with aliens
        for alien in aliens[:]:
            if bullet.rect.colliderect(alien.rect):
                game.play_sound("boom")
                game.score += 10
                alien.remove_from_game()
                aliens.remove(alien)
                bullet.remove_from_game()
                break

    #  Bomb movement and player collision 
    for bomb in list(game.objects.get_sprites_from_layer(LAYER_DEFAULT)):
        # Only process bombs
        if bomb in aliens:
            continue
        bomb.rect.y += 6
        if bomb.rect.colliderect(player.rect):
            game.score -= 5
            bomb.remove_from_game()

    #  Alien movement 
    hit_edge = False
    for alien in aliens:
        alien.rect.x += alien_dx
        if alien.rect.right >= 490 or alien.rect.left <= 10:
            hit_edge = True

    if hit_edge:
        alien_dx *= -1

# Entry point

if __name__ == "__main__":
    game.mainloop(game_logic)
