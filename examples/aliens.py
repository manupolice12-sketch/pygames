from pygames.advanced import PhysicSprite, Game
from os import path

class Alien:
    def __init__(self, x, y):
        base_dir = path.dirname(__file__)
        path_to_assets = path.join(base_dir, 'assets')      
        
        self.app = Game(500, 500, "Aliens Invasion")
        
        self.app.load_image("alien1", path.join(path_to_assets, "alien1.png"))
        self.app.load_image("background", path.join(path_to_assets, "background.gif"))
        self.app.load_sound("music", path.join(path_to_assets, "house_lo.ogg"))
        
        self.sprite = PhysicSprite(self.app, x, y, width=50, height=50)
        self.sprite.image = self.app.images["alien1"]
        
        self.sprite.gravity = False
        
        self.app.start(self.sprite)

    def start(self):
        def game_logic():
            self.app.background("black")
            self.app.screen.blit(self.app.images["background"], (0, 0))
            
        self.app.play_sound("music")
        self.app.mainloop(game_logic)

if __name__ == "__main__":
    alien = Alien(225, 225)
    alien.start()