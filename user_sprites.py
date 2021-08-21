import random
from ship import Ship
from velocity_controller import VelocityController
from ldpygame.event_responder import KeyUpResponder, KeyDownResponder
from bhgame import BulletHellGame
from bhsprite import *
from weapon_system import *

class UserShip(Ship):
    def __init__(self, rect, bounding_rect, groups, bullet_group, image=None, num_frames=1, frame_delay_ms=1000):
        super(UserShip, self).__init__(rect, bounding_rect, groups, bullet_group, image, num_frames, frame_delay_ms)
        self.powerups = {'fuel': 10000}
        self.fuel = 200
        self.active_weapon = None

    def fire_active_weapon(self, tick_time):
        if super(UserShip, self).fire_active_weapon(tick_time):
            BulletHellGame.active_game.sounds.play_sound('shotgun1.wav', os.path.join('sounds', 'sfx'), 0.1)

    def update(self, tick_time):
        super(UserShip, self).update(tick_time)
        for powerup in self.powerups.keys():
            self.powerups[powerup] -= tick_time

            if self.powerups[powerup] <= 0:
                if powerup == 'fuel':
                    self.fuel -= 10
                    # To keep the fuel gauge happy
                    if self.fuel < 0:
                        self.fuel = 0
                    self.powerups[powerup] = 10000
                else:
                    self.powerups.pop(powerup)
                    BulletHellGame.active_game.active_screen.remove_display(powerup)

                    if powerup == 'random':
                        while powerup == 'random':
                            powerup = random.choice(Canister.TYPE.keys())
                        self.add_powerup(powerup)
                        BulletHellGame.active_game.sounds.play_sound('sfx/powerup6.wav', volume=0.7)
                    elif powerup == 'buckshot':
                        self.active_weapon = None
                    elif powerup == 'invincibility':
                        self.frames = BulletHellGame.active_game.images.get('ship.png')
                        self.update_frame(self.frame_num)
                    elif powerup == 'nuke':
                        BulletHellGame.active_game.active_screen.detonate()

    def add_powerup(self, powerup):
        if len(self.groups()) > 0:
            if powerup == 'ammo' and 'ammo' not in self.powerups:
                AmmoCannonAddon(self, BulletHellGame.active_game.images.get('cannon_addon.png'))
            elif powerup == 'leftshot' and 'leftshot' not in self.powerups:
                LeftshotAddon(self, BulletHellGame.active_game.images.get('cannon_addon_left.png'))
            elif powerup == 'rightshot' and 'rightshot' not in self.powerups:
                RightshotAddon(self, BulletHellGame.active_game.images.get('cannon_addon_right.png'))
            elif powerup == 'backshot' and 'backshot' not in self.powerups:
                BackshotAddon(self, BulletHellGame.active_game.images.get('cannon_addon_down.png'))
            elif powerup == 'flamethrower' and 'flamethrower' not in self.powerups:
                FlamethrowerAddon(self, BulletHellGame.active_game.images.get('flamethrower_addon.png'))
            elif powerup == 'missiles' and 'missiles' not in self.powerups:
                MissileAddon(self, BulletHellGame.active_game.images.get('flamethrower_addon.png'))
            elif powerup == 'buckshot' and 'buckshot' not in self.powerups:
                self.active_weapon = Weapon(500, SprayBulletTrajectory, 5, StandardBullet)
                self.active_weapon.set_sprite_group(self.bullet_group)
            elif powerup == 'invincibility' and 'invincibility' not in self.powerups:
                self.frames = BulletHellGame.active_game.images.get('ship-invincible.png')
                self.update_frame(self.frame_num)

        self.powerups[powerup] = 10000 # 10 seconds in ms

    def apply_key_func(self, key):
        return lambda event: self.velocity_controller.toggle_key_state(key)

    def add_event_responders(self, manager):
        self.velocity_controller = VelocityController(self, 8)

        add_responder = lambda key, kind: manager.add_event_responder(kind((key), None, -1, self.apply_key_func(key)))
        keys = [pygame.K_LEFT, pygame.K_a, pygame.K_RIGHT, pygame.K_d, pygame.K_UP, pygame.K_w, pygame.K_DOWN,
            pygame.K_s, pygame.K_RSHIFT, pygame.K_LSHIFT]
        for key in keys:
            add_responder(key, KeyDownResponder)
            add_responder(key, KeyUpResponder)

        manager.add_event_responder(KeyDownResponder((pygame.K_SPACE), None, -1, self.toggle_weapons_hot))

    def velocity_did_change(self, x, y):
        self.set_velocity(x, y)
