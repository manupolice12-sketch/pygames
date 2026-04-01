from pygames.advanced import *
from os import path

base_dir = path.dirname(__file__)
assets = path.join(base_dir, 'assets')

app = Game(500, 500, "Alien Invasion")
app.start_score_counter()
app.start_garbage_collecter()

app.load_image("alien1", path.join(assets, "alien1.png"))
app.load_image("alien2", path.join(assets, "alien2.png"))
app.load_image("player", path.join(assets, "player1.gif"))
app.load_image("background", path.join(assets, "background.gif"))
app.load_sound("boom", path.join(assets, "boom.wav"))

player = Player(app, 225, 430, width=40, height=50, color="blue", speed=5)
player.image = app.images["player"]
player.rect = player.image.get_rect(topleft=(225, 430))
app.start(player)

bullets = []
aliens = []

ALIEN_ROWS = 2
ALIEN_COLS = 5
alien_dx = 2
alien_move_down = False

for row in range(ALIEN_ROWS):
    for col in range(ALIEN_COLS):
        alien = PhysicSprite(app, 60 + col * 80, 40 + row * 60, width=40, height=40)
        alien.image = app.images["alien1"] if row % 2 == 0 else app.images["alien2"]
        alien.rect = alien.image.get_rect(topleft=(60 + col * 80, 40 + row * 60))
        alien.gravity = 0
        aliens.append(alien)
        app.start(alien)

shoot_cooldown = 0

def game_logic():
    global shoot_cooldown, alien_dx, alien_move_down

    app.img("background", 0, 0, 500, 500)

    if app.check_key_pressed("space") and shoot_cooldown <= 0:
        bullet = PhysicSprite(app, player.rect.centerx - 4, player.rect.top - 10, width=8, height=16, color="yellow")
        bullet.gravity = 0
        bullet.vel_y = -10
        bullets.append(bullet)
        app.start(bullet)
        shoot_cooldown = 20

    if shoot_cooldown > 0:
        shoot_cooldown -= 1

    for bullet in bullets[:]:
        bullet.rect.y += bullet.vel_y
        if bullet.rect.bottom < 0:
            bullets.remove(bullet)
            if bullet in app.objects:
                app.objects.remove(bullet)
            continue
        for alien in aliens[:]:
            if bullet.rect.colliderect(alien.rect):
                app.play_sound("boom")
                app.score += 10
                aliens.remove(alien)
                if alien in app.objects:
                    app.objects.remove(alien)
                bullets.remove(bullet)
                if bullet in app.objects:
                    app.objects.remove(bullet)
                break

    hit_edge = False
    for alien in aliens:
        alien.rect.x += alien_dx
        if alien.rect.right >= 490 or alien.rect.left <= 10:
            hit_edge = True

    if hit_edge:
        alien_dx *= -1
        for alien in aliens:
            alien.rect.y += 20

    player.tick()

app.mainloop(game_logic)