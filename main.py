from __future__ import print_function
import pygame
from ldpygame.menu import RotatingImageMenu
from bhgame import BulletHellGame
from ldpygame.event_responder import KeyUpResponder, QuitResponder
from mainmenu import MainMenu
from gameovermenu import GameOverMenu

# Callbacks
def exit_game(event):
    BulletHellGame.active_game.exit()

def game_over(event):
    BulletHellGame.active_game.activate_screen('gameover')

def toggle_music(event):
    BulletHellGame.active_game.sounds.toggle_music()

# Setup Functions
def make_menus():
  # Main menu turn on!
  main = MainMenu('mainmenu', g.size, default_font=g.fonts.get('Lato-Bold.ttf',21))

  credit_images = [
    g.images.get('credits1.png'),
    g.images.get('credits2.png'),
    g.images.get('credits3.png'),
  ]
  credits = RotatingImageMenu('credits', g.size, credit_images, interval=10000, default_font=g.fonts.get('Lato-Bold.ttf',21))

  # Game Over
  go = GameOverMenu('gameover', g.size, default_font=g.fonts.get('Lato-Bold.ttf',21))

  return [main, credits, go]

# Make the game
if __name__ == "__main__":
  levels = None
  g = BulletHellGame(levels, title='Short Circuit', size=(700,700))

  # Add some global input handlers
  g.event_manager.add_event_responder(KeyUpResponder((pygame.K_ESCAPE), None, -1, exit_game))
  g.event_manager.add_event_responder(KeyUpResponder((pygame.K_m), None, -1, toggle_music))
  g.event_manager.add_event_responder(QuitResponder(exit_game))

  # Make menus
  menus = make_menus()

  # Make this screen our active screen
  for menu in menus:
    g.add_screen(menu)
  g.activate_screen('mainmenu')

  # And off we go
  g.run()
