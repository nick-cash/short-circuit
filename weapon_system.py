import pygame, abc
from bhgame import BulletHellGame
from bhsprite import StandardBullet

class BulletTrajectory(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, bullets, temporal_origin):
        super(BulletTrajectory, self).__init__()
        self.bullets = bullets
        self.temporal_origin = temporal_origin
        self.formula = self.generate_formula(0)

    def tick_trajectory(self, temporal_offset):
        for j in range(len(self.bullets)):
            self.apply_trajectory(j, self.bullets[j], temporal_offset)

    @abc.abstractmethod
    def apply_trajectory(self, index, bullet, time_now):
        pass

    @abc.abstractmethod
    def generate_formula(time_delta):
        pass

class SprayBulletTrajectory(BulletTrajectory):
    def __init__(self, bullets, temporal_origin):
        super(SprayBulletTrajectory, self).__init__(bullets, temporal_origin)
        self.y_offset = 0

    def generate_formula(self, time_delta):
        return lambda x: (-0.50 * (x**2)) + 1

    def map_range(self, value, in_min, in_max, out_min, out_max):
        return (value - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

    def apply_trajectory(self, index, bullet, time_now):
        time_delta = time_now - self.temporal_origin
        self.y_offset += 2
        self.formula = self.generate_formula(time_delta)
        x_offset = self.map_range(index, 0, len(self.bullets) - 1, -15.0, 15.0)
        v = self.map_range(index, 0, len(self.bullets) - 1, -1.0, 1.0)
        x = bullet.cartesian_origin[0] + x_offset
        x += v * int(self.y_offset / 100 * 2.2)
        y = bullet.cartesian_origin[1] - self.y_offset - 30 - (self.formula(v) * 15)
        bullet.rect.center = (x, y)
        bullet.dirty = 1

class CornersBulletTrajectory(BulletTrajectory):
    def __init__(self, bullets, temporal_origin):
        super(CornersBulletTrajectory, self).__init__(bullets, temporal_origin)
        self.offset = 10

    def generate_formula(self, time_delta):
        return lambda x: None

    def apply_trajectory(self, index, bullet, time_now):
        self.offset += 0.85
        x = bullet.cartesian_origin[0]
        y = bullet.cartesian_origin[1]

        if index is 0:
            x -= self.offset
        elif index is 1:
            y -= self.offset
        elif index is 2:
            x += self.offset
        elif index is 3:
            y += self.offset
        bullet.rect.center = (x, y)
        bullet.dirty = 1

class Weapon(object):
    def __init__(self, cooldown, trajectory, bullet_count, bullet_type):
        super(Weapon, self).__init__()
        self.cooldown = cooldown
        self.trajectory = trajectory
        self.bullet_count = bullet_count
        self.bullet_type = bullet_type
        self.sprite_group = None

    def set_sprite_group(self, group):
        """Make sure to call this before we ever try to make bullets"""
        self.sprite_group = group

    def spawn_trajectory(self, point, temporal_origin):
        bullets = []
        g = BulletHellGame.active_game

        for j in range(self.bullet_count):
            bullets.append(self.bullet_type(point, pygame.Rect((0, 0), g.size), self.sprite_group))
        return self.trajectory(bullets, temporal_origin)
