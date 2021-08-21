import pygame
from ldpygame.menu import Menu, Button
from ldpygame.game import Game
from ldpygame.sprite import Sprite
from bhgame import BulletHellGame
from levels import GameLevel, StarryBackground

class GameOverMenu(Menu):
    def __init__(self, name, size, offset=(0,0), default_font=None):
        background = BulletHellGame.active_game.images.get('endlevel.png')
        super(GameOverMenu, self).__init__(name, size, offset, background, default_font)

        play = lambda: self.make_level()
        mainmenu = lambda: Game.active_game.activate_screen('mainmenu')
        exit = lambda: Game.active_game.exit()

        # GAME OVER
        bigfont = BulletHellGame.active_game.fonts.get("Lato-Bold.ttf", 72)
        game = bigfont.render("GAME", True, pygame.Color(254, 235, 34))
        over = bigfont.render("OVER", True, pygame.Color(254, 235, 34))
        self.game = Sprite(pygame.Rect((240, 100), (game.get_width(), game.get_height())), self.sprites, game)
        self.over = Sprite(pygame.Rect((250, 175), (over.get_width(), over.get_height())), self.sprites, over)
        self.game.dirty = 2
        self.over.dirty = 2

        # Score
        scorefont = BulletHellGame.active_game.fonts.get("Lato-Bold.ttf", 20)
        white = pygame.Color(255,255,255)
        scoretxt = scorefont.render("Final Score", True, white)
        self.scoretxt = Sprite(pygame.Rect((300, 330), (scoretxt.get_width(), scoretxt.get_height())), self.sprites, scoretxt)
        self.scoretxt.dirty = 2
        self.scorenums = None

        # Buttons
        color = pygame.Color(170, 170, 170)
        acolor = pygame.Color(255, 255, 255)
        self.make_text_button((308,490), "Restart", "Restart", color, acolor, play)
        self.make_text_button((250,520), "Back to Main Menu", "Back to Main Menu", color, acolor, mainmenu)
        self.make_text_button((325,555), "Exit", "Exit", color, acolor, exit)

    def make_text_button(self, pos, string, active_string, color, active_color, callback, font=None):
        if not font:
            font = self.default_font

        img =  font.render(string, True, color)
        aimg = font.render(active_string, True, active_color)

        btn = Button(pygame.Rect(pos, (aimg.get_width(), aimg.get_height())),
                                self.buttons,
                                inactive_image=img,
                                active_image=aimg,
                                down_image=aimg,
                                up_image=img,
                                callback=callback)
        return btn

    def godown(self, *args):
        self.set_active(self.active_btn+1)
        BulletHellGame.active_game.sounds.play_sound('sfx/select1.wav', volume=0.5)

    def goup(self, *args):
        if(self.active_btn == 0):
            self.set_active(len(self.buttons.sprites())-1)
        else:
            self.set_active(self.active_btn-1);
        BulletHellGame.active_game.sounds.play_sound('sfx/select1.wav', volume=0.5)

    def make_level(self):
        BulletHellGame.active_game.score = 0
        BulletHellGame.active_game.remove_screen('main')
        size = BulletHellGame.active_game.size
        s = GameLevel('main', size, background=StarryBackground(size, 100))
        BulletHellGame.active_game.activate_screen(s)

    def activate(self):
        if self.scorenums:
            self.scorenums.kill()
            self.scorenums = None

        # Score
        scorefont = BulletHellGame.active_game.fonts.get("Lato-Bold.ttf", 20)
        white = pygame.Color(255,255,255)
        scorenums = scorefont.render("%d" % BulletHellGame.active_game.score, True, white)
        self.scorenums = Sprite(pygame.Rect((350-(scorenums.get_width()/2), 360),
                                            (scorenums.get_width(), scorenums.get_height())), self.sprites, scorenums)
        self.scorenums.dirty = 2
        return super(GameOverMenu, self).activate()
