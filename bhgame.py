from ldpygame.game import Game
from keyed_config_controller import KeyedConfigController

class BulletHellGame(Game):
    def __init__(self, levels, title='Bullet Hell', fps=60, size=(500,700), init=True):
        self.settings = KeyedConfigController("game_preferences.json")
        super(BulletHellGame, self).__init__(title, fps, size, init)

        # Note: This is the total game score and will be used for display by Scoreboard sprites
        self.score = 0

    def remove_screen(self, screen):
        if not isinstance(screen, basestring):
            screen = screen.name

        if screen in self.screens:
            self.screens.pop(screen)
            return True

        return False

    def activate_screen(self, screen):
        if isinstance(screen, basestring):
            if screen == 'credits':
                BulletHellGame.active_game.sounds.load_and_play_song('happydoomday.ogg', volume=0.5)

        return super(BulletHellGame, self).activate_screen(screen)
