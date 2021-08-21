import pygame
from ldpygame.menu import Menu, Button
from ldpygame.event_responder import KeyUpResponder
from ldpygame.sprite import Sprite
from bhgame import BulletHellGame
from levels import StarryBackground, GameLevel

class MainMenu(Menu):
    def __init__(self, name, size, offset=(0,0), default_font=None):
        """
        Init's the menu, add an additional buttons Group for handling buttons.
        """
        background = BulletHellGame.active_game.images.get('title.png')

        super(MainMenu, self).__init__(name, size, offset, background, default_font)

        play = lambda: self.make_level()
        toggle_music = lambda: BulletHellGame.active_game.sounds.toggle_music()
        credits = lambda: BulletHellGame.active_game.activate_screen('credits')
        exit = lambda: BulletHellGame.active_game.exit()

        bigfont = BulletHellGame.active_game.fonts.get("Lato-Bold.ttf", 72)
        img = bigfont.render("PLAY", True, pygame.Color(255, 193, 48))
        aimg = bigfont.render("PLAY", True, pygame.Color(254, 235, 34))
        playbtn = Button(pygame.Rect(260,260, aimg.get_width(), aimg.get_height()),
                         self.buttons,
                         inactive_image=img,
                         active_image=aimg,
                         down_image=aimg,
                         up_image=img,
                         callback=play)
        playbtn.set_layer(self.buttons, 1)

        # Add lower menu options
        img =  self.default_font.render("Toggle Music", True, pygame.Color(170, 170, 170))
        aimg = self.default_font.render("Toggle Music", True, pygame.Color(255, 255, 255))
        togglemusicbtn = Button(pygame.Rect(275,550,aimg.get_width(), aimg.get_height()),
                                self.buttons,
                                inactive_image=img,
                                active_image=aimg,
                                down_image=aimg,
                                up_image=img,
                                callback=toggle_music)
        togglemusicbtn.set_layer(self.buttons, 1)

        img =  self.default_font.render("Credits", True, pygame.Color(170, 170, 170))
        aimg = self.default_font.render("Credits", True, pygame.Color(255, 255, 255))
        creditsbtn = Button(pygame.Rect(305,580,aimg.get_width(), aimg.get_height()),
                                self.buttons,
                                inactive_image=img,
                                active_image=aimg,
                                down_image=aimg,
                                up_image=img,
                                callback=credits)
        creditsbtn.set_layer(self.buttons, 1)

        img =  self.default_font.render("Exit", True, pygame.Color(170, 170, 170))
        aimg = self.default_font.render("Exit", True, pygame.Color(255, 255, 255))
        exitbtn = Button(pygame.Rect(320,610,aimg.get_width(), aimg.get_height()),
                                self.buttons,
                                inactive_image=img,
                                active_image=aimg,
                                down_image=aimg,
                                up_image=img,
                                callback=exit)
        exitbtn.set_layer(self.buttons, 1)

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
        BulletHellGame.active_game.sounds.load_and_play_song('FranklinWebberMusic/GoldenStreets.ogg', volume=0.6)
        return super(MainMenu, self).activate()
