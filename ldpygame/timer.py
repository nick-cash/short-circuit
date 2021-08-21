import pygame

class Timer(object):
    event_id = pygame.USEREVENT

    def __init__(self, milliseconds):
        self.milliseconds = milliseconds

        self.event_id = Timer.event_id
        Timer.event_id += 1

    def start(self):
        """
        Begin adding events to the queue. You should register an event
        responder for self.event_id to process them.
        """
        pygame.time.set_timer(self.event_id, self.milliseconds)

    def stop(self):
        """
        Stop adding events to the queue. The event_id of this timer will never
        be reused.
        """
        pygame.time.set_timer(self.event_id, 0)

class TimerManager(object):
    """
    A wrapper for Timer() objects. Can be inherited or instantiated.
    """
    def __init__(self):
        self.timers = {}

    def add(self, milliseconds):
        """ Create a new timer and keep track of it. """
        timer = Timer(milliseconds)
        self.timers[timer.event_id] = timer
        return timer

    def start(event_id):
        self.timers[event_id].start()

    def stop(event_id):
        self.timers[event_id].stop()
