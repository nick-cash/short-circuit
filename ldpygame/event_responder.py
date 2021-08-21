# Seemed good, so I took this from Allyn's nspygame :D
import pygame
from timer import Timer

# This should go in some sort of window/screen abstraction
class EventResponderManager(object):
    def __init__(self):
        self.event_responders = []
        self.repeating_event_responders = []

    # should probably subclass and customize this method
    def should_process_responders(self, event):
        return True

    def tick(self, time):
        for d in self.repeating_event_responders:
            d['remaining'] -= time
            if d['remaining'] <= 0:
                d['remaining'] = d['responder'].repeats_every
                d['responder'].callback(None)

    def should_cancel_repeating_responder(self, repeat_dict, event):
        r = repeat_dict['responder']
        c = r.anti_responder()
        if not c:
            return False
        return c.responds_to_event(event)

    def add_repeating_responder(self, responder):
        matches = filter(lambda d: d['responder'] == responder, self.repeating_event_responders)
        if len(matches) == 0:
            self.repeating_event_responders.append({'responder': responder, 'remaining': responder.repeats_every })

    def process_responders(self, event):
        repeats = filter(lambda d: self.should_cancel_repeating_responder(d, event), self.repeating_event_responders)

        for repeat in repeats:
            self.repeating_event_responders.remove(repeat)

        if self.should_process_responders(event):
            responders = filter(lambda responder: responder.responds_to_event(event), self.event_responders)

            for responder in responders:
                if responder.does_repeat():
                    self.add_repeating_responder(responder)
                counter = responder.anti_responder()
                responder.callback(event)

    def send_event(self, event):
        self.process_responders(event)

    def add_event_responder(self, responder):
        self.event_responders.append(responder)

class EventResponder(object):
    RepeatsNever = -1
    CallbackIgnore = 'CallbackIgnore'

    def __init__(self, repeats_every, callback, type=None):
        self.callback = callback
        self.repeats_every = repeats_every
        self.type = type
        if not self.is_fake_responder():
            assert callable(callback), "callback must be callable"

    def responds_to_event(self, event):
        return event.type == self.type

    def is_fake_responder(self):
        return self.callback == EventResponder.CallbackIgnore

    def does_repeat(self):
        return self.repeats_every > EventResponder.RepeatsNever and not self.is_fake_responder()

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return self.type == other.type

    def anti_responder(self):
        return None

class QuitResponder(EventResponder):
    def __init__(self, callback):
        super(QuitResponder, self).__init__(EventResponder.RepeatsNever, callback, type=pygame.QUIT)

class TimerResponder(EventResponder):
    def __init__(self, callback, timer):
        super(TimerResponder, self).__init__(EventResponder.RepeatsNever, callback, type=timer.event_id)

# calls callback with the event when the mouse moves
class MouseMotionResponder(EventResponder):
    def __init__(self, callback):
        super(MouseMotionResponder, self).__init__(EventResponder.RepeatsNever, callback, type=pygame.MOUSEMOTION)

class MouseButtonEventResponder(EventResponder):
    def __init__(self, callback):
        EventResponder.__init__(self, EventResponder.RepeatsNever, callback)
        self.button = 1

    def responds_to_event(self, event):
        return EventResponder.responds_to_event(self, event) and self.button == event.button

# calls callback with the event when button is clicked
class MouseButtonDownResponder(MouseButtonEventResponder):
    def __init__(self, callback):
        MouseButtonEventResponder.__init__(self, callback)
        self.type = pygame.MOUSEBUTTONDOWN
        self.button = 1

# calls callback with the event when button is released
class MouseButtonUpResponder(MouseButtonEventResponder):
    def __init__(self, callback):
        MouseButtonEventResponder.__init__(self, callback)
        self.type = pygame.MOUSEBUTTONUP
        self.button = 1

class KeyEventResponder(EventResponder):
    def __init__(self, keys, mods, repeats_every, callback):
        EventResponder.__init__(self, repeats_every, callback)
        self.keys = keys
        self.mods = mods
        self.callback = callback

    def responds_to_event(self, event):
        return EventResponder.responds_to_event(self, event) and self.keys == event.key

    def __eq__(self, other):
        return super(KeyEventResponder, self).__eq__(other) and self.keys == other.keys and self.mods == other.mods

# actives when all keys are active on view. currently that view must be the window, because its hard
# keys is a list of keys. but for now it will only support one
# mods is a list of mods #http://www.pygame.org/docs/ref/key.html
class KeyDownResponder(KeyEventResponder):
    def __init__(self, keys, mods, repeats_every, callback):
        KeyEventResponder.__init__(self, keys, mods, repeats_every, callback)
        self.type = pygame.KEYDOWN

    def responds_to_event(self, event):
        return KeyEventResponder.responds_to_event(self, event) and self.keys == event.key

    def anti_responder(self):
        return KeyUpResponder(self.keys, self.mods, EventResponder.RepeatsNever, EventResponder.CallbackIgnore)

class KeyUpResponder(KeyEventResponder):
    def __init__(self, keys, mods, repeats_every, callback):
        KeyEventResponder.__init__(self, keys, mods, repeats_every, callback)
        self.type = pygame.KEYUP

    def responds_to_event(self, event):
        return KeyEventResponder.responds_to_event(self, event) and self.keys == event.key

    def anti_responder(self):
        return KeyDownResponder(self.keys, self.mods, EventResponder.RepeatsNever, EventResponder.CallbackIgnore)

