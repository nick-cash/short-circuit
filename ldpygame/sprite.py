import pygame
from math import fabs
from event_responder import EventResponderManager
from sprite_events import *

# Used internally so you can pass a simple tuple/list for velocities, and really
# anything that requires a point that you dont want to use a pygame Rect for
def xy_float(container):
    if isinstance(container, (list, tuple)) and len(container) == 2:
        return {'x': float(container[0]), 'y': float(container[1])}

    return None

class Sprite(pygame.sprite.DirtySprite):
    def __init__(self, rect, groups, image=None):
        super(Sprite, self).__init__()
        self.rect = rect
        self.dirty = 1

        self.set_layer(groups)

        if image:
            self.image = image
        else:
            self.image = pygame.Surface((self.rect.w, self.rect.h))
            self.image.fill(pygame.Color(255,255,255))

    def set_layer(self, groups, layer=0):
        if not isinstance(groups, (list, tuple)):
            groups = [groups]

        for group in groups:
            if self in group:
                group.change_layer(self, layer)
            else:
                group.add(self, layer=layer)

    def add_velocity(self, x, y):
        return False

class MobileSprite(Sprite):
    LEFT = "left"
    RIGHT = "right"
    DIRECTIONS = (LEFT,RIGHT)

    def __init__(self, rect, bounding_rect, groups, image=None):
        super(MobileSprite, self).__init__(rect, groups, image)
        self.bounding_rect = bounding_rect
        self.event_manager = EventResponderManager()
        self.velocity = xy_float((0,0))
        self.accumulated_movement = xy_float((0,0))
        self.direction = MobileSprite.LEFT
        self.last_position = None

    def add_event_responder(self, event_responder):
        self.event_manager.add_event_responder(event_responder)

    def move_sprite(self):
        self.accumulated_movement['x'] += self.velocity['x']
        self.accumulated_movement['y'] += self.velocity['y']

        if (fabs(self.accumulated_movement['x']) >= 1.0 or
            fabs(self.accumulated_movement['y']) >= 1.0):
            # Determine the number of exact pixels to move
            self.movement = pygame.Rect(int(self.accumulated_movement['x']),
                                        int(self.accumulated_movement['y']),
                                        1, 1) # Give the movement non-zero width/height
                                              # so we can use the return value in nonzero tests

            # Move this sprite
            self.last_position = self.rect
            self.rect = self.rect.move(self.movement.x, self.movement.y)
            self.accumulated_movement['x'] -= self.movement.x
            self.accumulated_movement['y'] -= self.movement.y

            return self.movement

        # No movement
        return None

    def update(self, *args):
        if self.move_sprite():
            self.dirty = 1

        if self.rect.x > self.bounding_rect.right:
            self.event_manager.send_event(SpriteEvent('SpriteDidLeaveEventResponder-maxX', self, self.bounding_rect))
        elif self.rect.x + self.rect.w < self.bounding_rect.left:
            self.event_manager.send_event(SpriteEvent('SpriteDidLeaveEventResponder-minX', self, self.bounding_rect))
        elif self.rect.x+self.rect.w > self.bounding_rect.right:
            self.event_manager.send_event(SpriteEvent('SpriteWillLeaveEventResponder-maxX', self, self.bounding_rect))
        elif self.rect.x < self.bounding_rect.left:
            self.event_manager.send_event(SpriteEvent('SpriteWillLeaveEventResponder-minX', self, self.bounding_rect))

        if self.rect.y > self.bounding_rect.bottom:
            self.event_manager.send_event(SpriteEvent('SpriteDidLeaveEventResponder-maxY', self, self.bounding_rect))
        elif self.rect.y + self.rect.h < self.bounding_rect.top:
            self.event_manager.send_event(SpriteEvent('SpriteDidLeaveEventResponder-minY', self, self.bounding_rect))
        elif self.rect.y+self.rect.h > self.bounding_rect.bottom:
            self.event_manager.send_event(SpriteEvent('SpriteWillLeaveEventResponder-maxY', self, self.bounding_rect))
        elif self.rect.y < self.bounding_rect.top:
            self.event_manager.send_event(SpriteEvent('SpriteWillLeaveEventResponder-minY', self, self.bounding_rect))

    def set_velocity(self, x, y):
        self.velocity = xy_float((x,y))
        self.update_direction()

    def add_velocity(self, x, y):
        self.velocity['x'] += x
        self.velocity['y'] += y
        self.update_direction()

        return self.direction

    def update_direction(self):
        if self.velocity['x'] < 0:
            self.direction = MobileSprite.LEFT
        elif self.velocity['x'] > 0:
            self.direction = MobileSprite.RIGHT

class BounceSprite(MobileSprite):
    def __init__(self, rect, bounding_rect, groups, image=None):
        super(BounceSprite, self).__init__(rect, bounding_rect, groups, image)
        self.add_event_responder(SpriteWillLeaveMinXEventResponder(self.bounce_min_x))
        self.add_event_responder(SpriteWillLeaveMaxXEventResponder(self.bounce_max_x))

        self.add_event_responder(SpriteWillLeaveMinYEventResponder(self.bounce_min_y))
        self.add_event_responder(SpriteWillLeaveMaxYEventResponder(self.bounce_max_y))

    def bounce_min_x(self, event):
        self.rect.x = self.bounding_rect.left
        self.velocity['x'] *= -1

    def bounce_max_x(self, event):
        self.rect.x = self.bounding_rect.right - self.rect.w
        self.velocity['x'] *= -1

    def bounce_min_y(self, event):
        self.rect.y = self.bounding_rect.top
        self.velocity['y'] *= -1

    def bounce_max_y(self, event):
        self.rect.y = self.bounding_rect.bottom - self.rect.h
        self.velocity['y'] *= -1

class AnimatedSprite(MobileSprite):
    def __init__(self, rect, bounding_rect, groups, image, num_frames, frame_delay_ms):
        super(AnimatedSprite, self).__init__(rect, bounding_rect, groups, image)

        self.num_frames = num_frames
        self.frame_delay_ms = frame_delay_ms
        self.frame_timer_ms = 0
        self.frame_num = 0
        self.frames = image

        self.set_frame(0)

    def set_frame(self, frame_num):
        self.dirty = 1
        self.frame_num = frame_num
        self.image = self.frames.subsurface(pygame.Rect(self.frame_num * self.rect.w, 0, self.rect.w, self.rect.h))

    def update(self, tick_time):
        super(AnimatedSprite, self).update(tick_time)
        self.update_frame(tick_time)

    def update_frame(self, tick_time):
        self.frame_timer_ms += tick_time

        if self.frame_timer_ms >= self.frame_delay_ms:
            self.frame_timer_ms = 0
            self.frame_num += 1

            if self.frame_num >= self.num_frames:
                self.frame_num = 0

            self.set_frame(self.frame_num)

class SpriteManager(pygame.sprite.LayeredDirty):
    """
    Keeps track of sprites in a list. When the draw() function is called, all
    sprites are drawn to the screen and it returns a list of rectangles that have
    changed that should be passed to pygame.display.update()
    """
    pass