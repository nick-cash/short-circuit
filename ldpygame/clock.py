import pygame

class Clock(object):
    """
    Framework abstraction of pygame clocks.
    """
    def __init__(self):
        self.clock = pygame.time.Clock()
        self.elapsed_time = 0
        self.last_time = 0

        # Time inbetween ticks
        self.tick_time = 0

    def tick(self):
        """
        Call however fast you want to update your time, but keep in mind most
        systems have limited time resolution of ~10ms
        """
        miliseconds = self.clock.tick()

        self.last_time = self.elapsed_time
        self.elapsed_time += miliseconds

        self.tick_time = self.elapsed_time - self.last_time

class GameClock(Clock):
    """
    Works as a normal clock but with the addition of framerate limiting. Passing
    a specified framerate will keep the clock running -at most- that many times
    per second.
    """
    def __init__(self, fps):
        super(GameClock, self).__init__()
        self.fps = fps

    def tick(self):
        miliseconds = self.clock.tick(self.fps)

        self.last_time = self.elapsed_time
        self.elapsed_time += miliseconds

        self.tick_time = self.elapsed_time - self.last_time

    def get_average_fps(self):
        """
        Compute and return the framerate by averaging the last 10 calls to
        self.clock.tick()
        """
        return self.clock.get_fps()
