import pygame
from sprite import SpriteManager
from event_responder import EventResponderManager

class Screen(object):
    """
    Each screen comes with a unique surface, event responders, and sprites.
    """
    def __init__(self, name, size, offset=(0,0), background=None):
        super(Screen, self).__init__()
        self.name = name
        self.size = size
        self.draw_offset = offset
        self.screen_surface = pygame.Surface(self.size)

        if background:
            self.background = background
        else:
            self.background = pygame.Surface(self.size)
            self.background.fill(pygame.Color(0,0,0))

        self.sprites = SpriteManager()
        self.event_manager = EventResponderManager()

        # pygame.Rect's of areas of the screen that need to be redrawn.
        # Example of drawing a sprite from www.pygame.org/docs/tut/newbieguide.html:
        #   1) Blit background over sprite's current location
        #   2) Append the sprite's current location rect to dirty_rects
        #   3) Move the sprite
        #   4) Draw the sprite at it's new location
        #   5) Append the sprite's new location to dirty_rects
        #   6) Call display.update(self.dirty_rects) once per frame
        self.dirty_rects = []

    def update(self, tick_time):
        """
        Handle sprite and other screen updates. Events will be passed directly
        to our event_manager when the screen is active, so we don't need to
        process them here.
        """
        self.event_manager.tick(tick_time)
        self.sprites.update(tick_time)

    def draw(self):
        """
        Draw to the screen. If dirty_rects is empty, it will redraw the entire
        screen. It is best to keep track of areas that need to be redrawn.
        """
        self.sprites.clear(self.screen_surface, self.background)
        self.dirty_rects += self.sprites.draw(self.screen_surface)

        dirty_rects = self.dirty_rects
        self.dirty_rects = []

        return dirty_rects

    def activate(self):
        self.dirty_rects.append(pygame.Rect((0,0), self.size))

    def deactivate(self):
        pass
