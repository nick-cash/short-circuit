# Python
import sys

# Pygame
import pygame

# Framework
from clock import GameClock
from screen import Screen
from timer import TimerManager
from event_responder import EventResponderManager
from sprite import Sprite, SpriteManager
from asset_manager import ImageManager, FontManager, SoundManager

class Game(object):
    active_game = None

    """
    This is the top-level framework object. You should only instantiate one.
    Subclass for game customization.
    """
    def __init__(self, title='Untitled', fps=60, size=(360,240), init=True):
        """
        Performs all game initializion. This function calls pygame.init(),
        so it should not be called elsewhere.
        """
        self.fps = fps
        self.size = size
        self.title = title
        self.active_screen = None
        self.screens = {}

        Game.active_game = self

        if init:
            self.pygame_init()

    def pygame_init(self):
        """
        Run pygame.init() and all the initialization that has to occur
        afterwards. Must be run -once- before run()
        """
        pygame.init()
        pygame.display.set_mode(self.size)
        pygame.display.set_caption(self.title)

        self.clock = GameClock(self.fps)
        self.screen_surface = pygame.display.get_surface()

        # This could be inherited, but I like this syntax better
        self.timers = TimerManager()

        # Manage dem assets, yo
        self.images = ImageManager()
        self.sounds = SoundManager(self)
        self.fonts = FontManager()

        # This is in addition to event managers on screens. The only stuff that
        # should go here would be game-wide events that are not screen-specific
        self.event_manager = EventResponderManager()

    def activate_screen(self, screen):
        """
        Changes to a new screen. Can take either screen object or screen name.
        Returns whether the screen was added to the screenlist or not.
        """
        if self.active_screen:
            self.active_screen.deactivate()

        if type(screen) is str:
            screen = self.screens[screen]

        self.active_screen = screen
        self.active_screen.activate()

        # Keep track of it if we aren't already
        return self.add_screen(self.active_screen)

    def add_screen(self, screen):
        added = False

        if screen.name not in self.screens:
            self.screens[screen.name] = screen
            added = True

        return added

    def run(self):
        """
        Run until we are done.
        """
        assert(self.active_screen),"Must have an active screen to run"

        while True:
            self.tick()
            self.draw()

    def tick(self):
        """
        Handle input and update game logic. No drawing is performed in this
        function.
        """
        self.clock.tick()

        self.handle_events()
        self.event_manager.tick(self.clock.tick_time)
        self.active_screen.update(self.clock.tick_time)

    def handle_events(self):
        """
        Handle input from keyboard, mouse, and timers
        """
        for event in pygame.event.get():
            self.event_manager.send_event(event)
            self.active_screen.event_manager.send_event(event)

    def draw(self):
        """
        Draw to the screen. If dirty_rects is empty, it will redraw the entire
        screen. It is best to keep track of areas that need to be redrawn.
        """
        dirty_rects = []

        # Perform blits
        dirty_rects += self.active_screen.draw()
        self.screen_surface.blit(self.active_screen.screen_surface,
                                 self.active_screen.draw_offset)

        # Update the screen
        pygame.display.update(dirty_rects)

    def exit(self):
        pygame.quit()
        sys.exit(0)
