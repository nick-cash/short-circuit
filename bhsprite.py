import pygame, random, math, os
from ldpygame.sprite import Sprite, AnimatedSprite
from bhgame import BulletHellGame
from ldpygame.sprite_events import SpriteDidLeaveMaxYEventResponder, SpriteDidLeaveMaxXEventResponder, SpriteDidLeaveMinXEventResponder, SpriteDidLeaveMinYEventResponder

class GameSprite(AnimatedSprite):
    def __init__(self, rect, bounding_rect, groups, image,
                       num_frames=1, frame_delay_ms=1000,
                       score=0):
        super(GameSprite, self).__init__(rect, bounding_rect, groups, image, num_frames, frame_delay_ms)
        self.score = int(score)
        self.tiltmode = False
        self.tiltaxis = 'x'
        self.enable_auto_destruct()

    def take_damage(self, amount):
        return

    def self_destruct(self):
        groups = self.groups()
        for group in groups:
            group.remove(self)

    def enable_auto_destruct(self):
        self.bounding_rect.inflate_ip(150,150)
        self.add_event_responder(SpriteDidLeaveMaxYEventResponder(lambda e: self.self_destruct(), self.bounding_rect))
        self.add_event_responder(SpriteDidLeaveMaxXEventResponder(lambda e: self.self_destruct(), self.bounding_rect))
        self.add_event_responder(SpriteDidLeaveMinXEventResponder(lambda e: self.self_destruct(), self.bounding_rect))
        self.add_event_responder(SpriteDidLeaveMinYEventResponder(lambda e: self.self_destruct(), self.bounding_rect))

    def score_sprite(self):
        BulletHellGame.active_game.score += self.score

    def enable_horz_tiltmode(self, enable = True):
        """For sprites with fixed forward orientation, a simple tilt mode.
        Can modify if we add sprite rotation. Code is in update_frame. """
        self.tiltmode = enable
        if(enable):
            self.tiltaxis = 'x'
            self.frame_num = math.floor(self.num_frames/2)
            self.set_frame(self.frame_num)

    def updatetilt(self):
        self.frame_timer_ms = 0
        tilt = 0
        tiltaxis = self.tiltaxis
        if self.velocity[tiltaxis] < 0:
            tilt = -1
        elif self.velocity[tiltaxis] > 0:
            tilt = 1

        if( (self.num_frames&1) == 0):
            midframes = [(self.num_frames/2)-1, (self.num_frames/2)]
        else:
            midframes = [math.floor(self.num_frames/2)]
        if(tilt == 0 and self.frame_num < midframes[0]):
            tilt = 1
        elif(tilt == 0 and self.frame_num > midframes[-1]):
            tilt = -1
        self.frame_num += tilt
        if(self.frame_num < 0):
            self.frame_num = 0
        elif(self.frame_num) >= self.num_frames:
            self.frame_num = self.num_frames - 1

        #a special case if there are two middle frames
        if tilt == 0 and len(midframes)>1:
            if self.frame_num == midframes[0]:
                self.frame_num = midframes[1]
            else:
                self.frame_num = midframes[0]
        self.set_frame(self.frame_num)

    def update_frame(self, tick_time):
        self.frame_timer_ms += tick_time

        if self.frame_timer_ms >= self.frame_delay_ms:
            if(self.tiltmode):
                self.updatetilt()
            else:
                self.frame_timer_ms = 0
                self.frame_num += 1

                if self.frame_num >= self.num_frames:
                    self.frame_num = 0

                self.set_frame(self.frame_num)

class AttachmentSprite(GameSprite):
    def __init__(self, rect, bounding_rect, groups, image, sprite_attach,
                       num_frames=1, frame_delay_ms=1000,
                       offsetx=0, offsety=0):
        super(AttachmentSprite, self).__init__(rect, bounding_rect, groups, image, num_frames, frame_delay_ms)
        self.attach = sprite_attach
        self.rect.x = self.attach.rect.x + offsetx
        self.rect.y = self.attach.rect.y + offsety
        self.offsetx = offsetx
        self.offsety = offsety
        self.velocity['x'] = 0
        self.velocity['y'] = 0
        score = 0

    def update(self, ticktime):
        """ Update manages attachment, we can have less exact attachments later. """
        super(AttachmentSprite, self).update(ticktime)
        self.dirty = 2
        self.rect.x = self.attach.rect.x + self.offsetx
        self.rect.y = self.attach.rect.y + self.offsety

class AmmoCannonAddon(AttachmentSprite):
    def __init__(self, shipsprite, image):
        super(AmmoCannonAddon,self).__init__(pygame.Rect((0,0),(30,30)), pygame.Rect((-200,-200),(1000,1000)),
                                             shipsprite.groups()[0], image, shipsprite, offsety = -15, offsetx = -1)
        self.firedelay = 200
        self.firetimer = 0
        self.set_layer(shipsprite.groups()[0], 13)

    def update(self, ticktime):
        """ Update manages attachment, we can have less exact attachments later. """
        super(AmmoCannonAddon, self).update(ticktime)
        self.firetimer += ticktime
        if self.firetimer > self.firedelay:
            self.firetimer = 0

            b = Bullet((self.rect.x,self.rect.y-5), (30, 9), pygame.Rect((0,0), (500,700)),
                       BulletHellGame.active_game.active_screen.player_bullets,
                       BulletHellGame.active_game.images.get('topshot.png'),
                       damage=50, num_frames=1, frame_delay_ms=100)
            b.set_velocity(0, -7)

        if 'ammo' not in self.attach.powerups:
            self.self_destruct()

class LeftshotAddon(AttachmentSprite):
    def __init__(self, shipsprite, image):
        super(LeftshotAddon,self).__init__(pygame.Rect((0,0),(30,30)), pygame.Rect((-200,-200),(1000,1000)),
                                            shipsprite.groups()[0], image, shipsprite, offsety = 0, offsetx = -13)
        self.firedelay = 200
        self.firetimer = 0
        self.set_layer(shipsprite.groups()[0], 13)

    def update(self, ticktime):
        """ Update manages attachment, we can have less exact attachments later. """
        super(LeftshotAddon, self).update(ticktime)
        self.firetimer += ticktime
        if self.firetimer > self.firedelay:
            self.firetimer = 0
            b = Bullet((self.rect.x-5,self.rect.y), (9, 30), pygame.Rect((0,0), (500,700)),
                       BulletHellGame.active_game.active_screen.player_bullets,
                       BulletHellGame.active_game.images.get('leftshot.png'),
                       damage=50, num_frames=3, frame_delay_ms=100)
            b.set_velocity(-7, 0)

        if 'leftshot' not in self.attach.powerups:
            self.self_destruct()

class RightshotAddon(AttachmentSprite):
    def __init__(self, shipsprite, image):
        super(RightshotAddon,self).__init__(pygame.Rect((0,0),(30,30)), pygame.Rect((-200,-200),(1000,1000)),
                                            shipsprite.groups()[0], image, shipsprite, offsety = -1, offsetx = 13)
        self.firedelay = 200
        self.firetimer = 0
        self.set_layer(shipsprite.groups()[0], 13)

    def update(self, ticktime):
        """ Update manages attachment, we can have less exact attachments later. """
        super(RightshotAddon, self).update(ticktime)
        self.firetimer += ticktime
        if self.firetimer > self.firedelay:
            self.firetimer = 0
            b = Bullet((self.rect.x+20,self.rect.y), (9, 30), pygame.Rect((0,0), (500,700)),
                       BulletHellGame.active_game.active_screen.player_bullets,
                       BulletHellGame.active_game.images.get('rightshot.png'),
                       damage=50, num_frames=3, frame_delay_ms=100)
            b.set_velocity(7, 0)

        if 'rightshot' not in self.attach.powerups:
            self.self_destruct()

class BackshotAddon(AttachmentSprite):
    def __init__(self, shipsprite, image):
        super(BackshotAddon,self).__init__(pygame.Rect((0,0),(30,30)), pygame.Rect((-200,-200),(1000,1000)),
                                            shipsprite.groups()[0], image, shipsprite, offsety = 15, offsetx = 1)
        self.firedelay = 200
        self.firetimer = 0
        self.set_layer(shipsprite.groups()[0], 13)

    def update(self, ticktime):
        """ Update manages attachment, we can have less exact attachments later. """
        super(BackshotAddon, self).update(ticktime)
        self.firetimer += ticktime
        if self.firetimer > self.firedelay:
            self.firetimer = 0
            b = Bullet((self.rect.x,self.rect.y+20), (30, 9), pygame.Rect((0,0), (500,700)),
                       BulletHellGame.active_game.active_screen.player_bullets,
                       BulletHellGame.active_game.images.get('backshot.png'),
                       damage=50, num_frames=3, frame_delay_ms=100)
            b.set_velocity(0, 7)

        if 'backshot' not in self.attach.powerups:
            self.self_destruct()

class FlamethrowerAddon(AttachmentSprite):
    def __init__(self, shipsprite, image):
        super(FlamethrowerAddon,self).__init__(pygame.Rect((0,0),(30,30)), pygame.Rect((-200,-200),(1000,1000)),
                                            shipsprite.groups()[0], image, shipsprite, offsety = -25, offsetx = 1)
        self.firedelay = 35
        self.firetimer = 0
        self.set_layer(shipsprite.groups()[0], 13)

    def update(self, ticktime):
        """ Update manages attachment, we can have less exact attachments later. """
        super(FlamethrowerAddon, self).update(ticktime)
        self.firetimer += ticktime
        if self.firetimer > self.firedelay:
            self.firetimer = 0
            b = Bullet((self.rect.x+10,self.rect.y), (18, 26), pygame.Rect((0,0), (500,700)),
                       BulletHellGame.active_game.active_screen.player_bullets,
                       BulletHellGame.active_game.images.get('flame.png'),
                       damage=10, num_frames=2, frame_delay_ms=100)
            b.set_velocity((random.random()+0.4) * random.choice([-1,1]), -7)

        if 'flamethrower' not in self.attach.powerups:
            self.self_destruct()

class MissileAddon(AttachmentSprite):
    def __init__(self, shipsprite, image):
        super(MissileAddon,self).__init__(pygame.Rect((0,0),(30,30)), pygame.Rect((-200,-200),(1000,1000)),
                                            shipsprite.groups()[0], image, shipsprite, offsety = -25, offsetx = 1)
        self.firedelay = 600
        self.firetimer = 0
        self.set_layer(shipsprite.groups()[0], 13)

    def update(self, ticktime):
        """ Update manages attachment, we can have less exact attachments later. """
        super(MissileAddon, self).update(ticktime)
        self.firetimer += ticktime
        if self.firetimer > self.firedelay:
            self.firetimer = 0
            b = Missile((self.rect.x+10,self.rect.y), (6, 20), pygame.Rect((0,0), (500,700)),
                       BulletHellGame.active_game.active_screen.player_bullets,
                       BulletHellGame.active_game.images.get('missile.png'),
                       damage=100, num_frames=3, frame_delay_ms=250)
            b.set_velocity(-0.2, -7)

            b = Missile((self.rect.x+14,self.rect.y), (6, 20), pygame.Rect((0,0), (500,700)),
                       BulletHellGame.active_game.active_screen.player_bullets,
                       BulletHellGame.active_game.images.get('missile.png'),
                       damage=100, num_frames=3, frame_delay_ms=250)
            b.set_velocity(0.2, -7)

            BulletHellGame.active_game.sounds.play_sound('sfx/missile_launch.wav', volume=0.5)

        if 'missiles' not in self.attach.powerups:
            self.self_destruct()

class Bullet(GameSprite):
    def __init__(self, point, size, bounding_rect, groups, image, damage=50, num_frames=1, frame_delay_ms=1000):
        self.damage = damage
        self.cartesian_origin = point
        rect = pygame.Rect(point, size)
        super(Bullet, self).__init__(rect, bounding_rect, groups, image, num_frames, frame_delay_ms)
        self.set_layer(groups, 11)

class Missile(Bullet):
    def __init__(self, point, size, bounding_rect, groups, image, damage=100, num_frames=3, frame_delay_ms=250):
        super(Missile, self).__init__(point, size, bounding_rect, groups, image, damage, num_frames, frame_delay_ms)

class StandardBullet(Bullet):
    def __init__(self, center, bounding_rect, groups):
        size = (10, 10)
        image = BulletHellGame.active_game.images.get('bullet/bullet.png')
        super(StandardBullet, self).__init__(center, size, bounding_rect, groups, image, frame_delay_ms=50, num_frames=8)

class SmallBullet(Bullet):
    def __init__(self, center, bounding_rect, groups):
        size = (30, 9)
        image = BulletHellGame.active_game.images.get('smallbullet.png')
        super(SmallBullet, self).__init__(center, size, bounding_rect, groups, image, damage=10, frame_delay_ms=50, num_frames=3)

class BulletBurstBlue(GameSprite):
    def __init__(self, rect, bounding_rect, groups,
                       num_frames=1, frame_delay_ms=1000, generation = 1):
        image = BulletHellGame.active_game.images.get('bluedisc.png')
        super(BulletBurstBlue, self).__init__(rect, bounding_rect, groups, image, num_frames, frame_delay_ms)

        self.tiltmode = False
        self.velocity['x'] = 0
        self.velocity['y'] = 3
        self.timealive = 0
        self.generation = generation

    def update(self, ticktime):
        super(GameSprite, self).update(ticktime)
        self.timealive += ticktime
        if(self.timealive > 1400 and len(self.groups()) > 0 and self.generation < 2):
            for i in range(0,4):
                sprite = BulletBurstBlue(pygame.Rect((self.rect.x, self.rect.y), (16,16)), pygame.Rect((0,0), (500,700)),
                    self.groups(), generation = self.generation+1 )
                sprite.set_layer(sprite.groups()[0], 11)
                sprite.velocity['x'] = math.cos(math.radians(i*72))
                sprite.velocity['y'] = math.sin(math.radians(i*72))
            self.timealive -= 2000000
            self.self_destruct()

class Canister(GameSprite):
    TYPE = {
        'fuel': {'score': 5, 'color': pygame.Color(253, 240, 52)},
        'ammo': {'score': 15, 'color': pygame.Color(193, 36, 36)},
        'invincibility': {'score': 5, 'color': pygame.Color(203, 227, 242)},
        #'laser': {'score': 100, 'color': pygame.Color(182, 235, 201)},
        'buckshot': {'score': 15, 'color': pygame.Color(183, 183, 183)},
        'backshot': {'score': 15, 'color': pygame.Color(223, 226, 169)},
        'leftshot': {'score': 15, 'color': pygame.Color(80, 87, 213)},
        'rightshot': {'score': 15, 'color': pygame.Color(196, 96, 202)},
        'missiles': {'score': 50, 'color': pygame.Color(121, 230, 218)},
        'flamethrower': {'score': 50, 'color': pygame.Color(255, 125, 54)},
        'nuke': {'score': 500, 'color': pygame.Color(0, 158, 255)},
        #'knife': {'score': 50, 'color': pygame.Color(233, 126, 224)},
        'random': {'score': 250, 'color': None},
    }

    def __init__(self, rect, bounding_rect, groups, ctype='fuel',
                       num_frames=1, frame_delay_ms=1000):
            image = BulletHellGame.active_game.images.get('canister-%s.png' % ctype)

            if ctype == 'random':
                num_frames = 12
                frame_delay_ms = 200

            super(Canister, self).__init__(rect, bounding_rect, groups, image, num_frames, frame_delay_ms)
            self.score = Canister.TYPE[ctype]['score']
            self.ctype = ctype

# This should eventually be abstracted back to LDPygame. Note that it utilizes the active
# games score directly; no score is ever passed around
class Scoreboard(Sprite):
    def __init__(self, rect, groups, string, font, color=None):
        super(Scoreboard, self).__init__(rect, groups, image=None)
        self.string = string
        self.font = font

        if not color:
            self.color = pygame.Color(255,255,255)
        else:
            self.color = color

        # Always show scoreboard
        self.dirty = 2
        self.set_layer(groups, 100000)

        # Create our image
        self.update()

    def update(self, *args):
        score_string = self.string.format(BulletHellGame.active_game.score)
        self.image = self.font.render(score_string, True, self.color)

    def score_sprite(self):
        return

class SideBar(Scoreboard):
    def __init__(self, rect, groups, font, color=None):
        super(SideBar, self).__init__(rect, groups, "", font, color)
        self.image = BulletHellGame.active_game.images.get('sidebar.jpg')

        if not color:
            self.color = pygame.Color(255,255,255)
        else:
            self.color = color

        # Always show scoreboard
        self.dirty = 2
        self.set_layer(groups, 90000)

        # Create our image
        self.update()

    def update(self, *args):
        pass

class FuelDisplay(Scoreboard):
    def __init__(self, rect, groups, font, color=None):
        # Make sure to pass an empty string for some fucking reason, who knows, its magic i think
        super(FuelDisplay, self).__init__(rect, groups, "", font, color)

        self.image = pygame.Surface((rect.w, rect.h))
        self.image.fill(pygame.Color(0,0,0,0))

    def update(self, *args):
        if (BulletHellGame.active_game and
            BulletHellGame.active_game.active_screen and
            BulletHellGame.active_game.active_screen.ship):

            fuel = self.font.render("Fuel: ", True, self.color)

            x = int(BulletHellGame.active_game.active_screen.ship.fuel/2)

            if x <= 0:
                x = 1

            gauge = pygame.Surface((x, 15))
            gauge.fill(pygame.Color(253, 240, 52))

            self.image = pygame.Surface(((fuel.get_width()+gauge.get_width()+2), fuel.get_height()), pygame.SRCALPHA)
            self.image.fill(pygame.Color(0,0,0,0))
            self.image.blit(fuel, (0,0))
            self.image.blit(gauge, (fuel.get_width()+2, 4))
            self.rect = pygame.Rect((self.rect.x, self.rect.y), (self.image.get_width(), self.image.get_height()))

class PowerupDisplay(Scoreboard):
    def __init__(self, rect, groups, ctype):
        self.ctype = ctype
        super(PowerupDisplay, self).__init__(rect, groups, ctype, None)

    def update(self, *args):
        if (BulletHellGame.active_game and
            BulletHellGame.active_game.active_screen and
            BulletHellGame.active_game.active_screen.ship and
            self.ctype in BulletHellGame.active_game.active_screen.ship.powerups):

            x = int(BulletHellGame.active_game.active_screen.ship.powerups[self.ctype]/100)

            self.image = pygame.Surface((x,10))
            self.rect = pygame.Rect((self.rect.x, self.rect.y), (self.image.get_width(), self.image.get_height()))

            color = Canister.TYPE[self.ctype]['color']

            # only 'random' canisters will hit this
            while not color:
                color = Canister.TYPE[random.choice(Canister.TYPE.keys())]['color']

            self.image.fill(color)
        else:
            self.rect = pygame.Rect((self.rect.x, self.rect.y),(0,0))
            self.image = pygame.Surface((0,0))
            self.image.fill(pygame.Color(0,0,0,0))
