import pygame, random
from ship import Ship
from bhgame import BulletHellGame
from ldpygame.sprite_events import *
from ldpygame.sprite import xy_float

class EnemyShip(Ship):
    TYPE = {
        "Arcade2":        {'frames': 5, 'fdelay': 80, 'score':  50, 'weapon': None, 'health':  50, 'size': pygame.Rect((0,0), (30,30))},
        "cakeslice2":     {'frames': 5, 'fdelay': 80, 'score': 100, 'weapon': None, 'health':  50, 'size': pygame.Rect((0,0), (64,63))},
        "Ufighter2":      {'frames': 5, 'fdelay': 80, 'score': 150, 'weapon': None, 'health': 100, 'size': pygame.Rect((0,0), (30,30))},
        "Storm2":         {'frames': 5, 'fdelay': 80, 'score': 125, 'weapon': None, 'health':  50, 'size': pygame.Rect((0,0), (30,30))},
        "Stalker2":       {'frames': 5, 'fdelay': 80, 'score':  90, 'weapon': None, 'health': 100, 'size': pygame.Rect((0,0), (30,30))},
        "Gencore2":       {'frames': 5, 'fdelay': 80, 'score':  75, 'weapon': None, 'health':  50, 'size': pygame.Rect((0,0), (30,30))},
        "GencoreMK2_2":   {'frames': 5, 'fdelay': 80, 'score': 150, 'weapon': None, 'health': 150, 'size': pygame.Rect((0,0), (30,30))},
        #"cakebossframes": {'frames': 7, 'fdelay':  0, 'score':1000, 'weapon': None, 'health':5000,  'size': pygame.Rect((0,0), (64,63))},
    }

    def __init__(self, rect, bounding_rect, groups, bullet_group, stype, score=None, health=None):
        super(EnemyShip, self).__init__(rect, bounding_rect, groups, bullet_group,
                                BulletHellGame.active_game.images.get(stype + '.png'),
                                EnemyShip.TYPE[stype]['frames'],
                                EnemyShip.TYPE[stype]['fdelay'],
                                (EnemyShip.TYPE[stype]['score'] if not score else score))
        if not health:
            health = EnemyShip.TYPE[stype]['health']
        self.health = health
        self.enable_horz_tiltmode()

    def take_damage(self, amount):
        self.health -= amount

        if self.health <= 0:
            BulletHellGame.active_game.sounds.play_sound('sfx/explode2.wav', volume=0.2)
            self.score_sprite()
            self.self_destruct()

# Ripped from our good ol' bouncingsprite
class EnemyShipBounce(EnemyShip):
    def __init__(self, rect, bounding_rect, groups, bullet_group, bounce_rect, stype, score=None, health=None):
        super(EnemyShipBounce, self).__init__(rect, bounding_rect, groups, bullet_group, stype, score=score)
        self.bounce_rect = bounce_rect
        self.add_event_responder(SpriteWillLeaveMinXEventResponder(self.bounce_min_x, self.bounce_rect))
        self.add_event_responder(SpriteWillLeaveMaxXEventResponder(self.bounce_max_x, self.bounce_rect))

    def move_sprite(self):
        val = super(EnemyShip, self).move_sprite()
        return val

    def update(self, tick_time):
        super(EnemyShipBounce, self).update(tick_time)

        if self.rect.x+self.rect.w > self.bounce_rect.right:
            self.event_manager.send_event(SpriteEvent('SpriteWillLeaveEventResponder-maxX', self, self.bounce_rect))
        elif self.rect.x < self.bounce_rect.left:
            self.event_manager.send_event(SpriteEvent('SpriteWillLeaveEventResponder-minX', self, self.bounce_rect))

        if self.rect.y+self.rect.h > self.bounce_rect.bottom:
            self.event_manager.send_event(SpriteEvent('SpriteWillLeaveEventResponder-maxY', self, self.bounce_rect))
        elif self.rect.y < self.bounce_rect.top:
            self.event_manager.send_event(SpriteEvent('SpriteWillLeaveEventResponder-minY', self, self.bounce_rect))

    def bounce_min_x(self, event):
        self.rect.x = self.bounce_rect.left
        self.velocity['x'] *= -1

    def bounce_max_x(self, event):
        self.rect.x = self.bounce_rect.right - self.rect.w
        self.velocity['x'] *= -1

    def bounce_min_y(self, event):
        self.rect.y = self.bounce_rect.top
        self.velocity['y'] *= -1

    def bounce_max_y(self, event):
        self.rect.y = self.bounce_rect.bottom - self.rect.h
        self.velocity['y'] *= -1
