import pygame

from velocity_controller import VelocityController
from bhgame import BulletHellGame
from bhsprite import GameSprite
from weapon_system import *

class Ship(GameSprite):
    def __init__(self, rect, bounding_rect, groups, bullet_group, image=None, num_frames=1, frame_delay_ms=1000, score=100):
        super(Ship, self).__init__(rect, bounding_rect, groups, image, num_frames, frame_delay_ms, score)
        self.set_layer(groups, 10)
        self.weapons_hot = True
        self.weapon_cooldown_remaining = 0
        self.bullet_group = bullet_group
        self.active_weapon = None

    def fire_active_weapon(self, tick_time):
        if not self.weapons_hot or self.active_weapon is None:
            return

        if self.weapon_cooldown_remaining <= 0:
            trajectory = self.active_weapon.spawn_trajectory(self.rect.center, pygame.time.get_ticks())
            BulletHellGame.active_game.active_screen.trajectories.append(trajectory)
            self.weapon_cooldown_remaining = self.active_weapon.cooldown
            return True
        else:
            self.weapon_cooldown_remaining -= tick_time
            return False

    def update(self, tick_time):
        super(Ship, self).update(tick_time)
        self.fire_active_weapon(tick_time)

    def toggle_weapons_hot(self, event):
        self.weapons_hot = not self.weapons_hot
