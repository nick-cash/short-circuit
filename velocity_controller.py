import pygame

class VelocityController(object):
    X_AXIS_KEYS = [pygame.K_LEFT, pygame.K_a, pygame.K_RIGHT, pygame.K_d]
    Y_AXIS_KEYS = [pygame.K_UP, pygame.K_w, pygame.K_DOWN, pygame.K_s]
    POSITIVE_SIGN_KEYS = [pygame.K_RIGHT, pygame.K_d, pygame.K_DOWN, pygame.K_s]
    NEGATIVE_SIGN_KEYS = [pygame.K_LEFT, pygame.K_a, pygame.K_UP, pygame.K_w]
    SLOW_SPEED_KEYS = [pygame.K_RSHIFT, pygame.K_LSHIFT]

    def __init__(self, delegate, static_velocity):
        self.delegate = delegate
        self.static_velocity = static_velocity
        self.active_keys = []

    def toggle_key_state(self, key):
        if key in self.active_keys:
            self.active_keys.remove(key)
        else:
            self.active_keys.append(key)
        self.notify_delegate()

    def _sign_for_key(self, key):
        if key in VelocityController.POSITIVE_SIGN_KEYS:
            return 1
        elif key in VelocityController.NEGATIVE_SIGN_KEYS:
            return -1
        else:
            return 0

    def clamp(self, minimum, x, maximum):
        return max(minimum, min(x, maximum))

    def _velocity_for_keys(self, keys):
        sign = reduce(lambda sign, key: sign + self._sign_for_key(key), keys, 0)
        return self.clamp(-1, sign, 1) * self.static_velocity

    def _keys_in_scope(self, scope):
        return filter(lambda key: key in scope, self.active_keys)

    def _x_velocity(self):
        velocity_shift = 1
        if len(self._keys_in_scope(VelocityController.SLOW_SPEED_KEYS)) > 0:
            velocity_shift = 0.5

        return self._velocity_for_keys(self._keys_in_scope(VelocityController.X_AXIS_KEYS))*velocity_shift

    def _y_velocity(self):
        velocity_shift = 1
        if len(self._keys_in_scope(VelocityController.SLOW_SPEED_KEYS)) > 0:
            velocity_shift = 0.5

        return self._velocity_for_keys(self._keys_in_scope(VelocityController.Y_AXIS_KEYS))*velocity_shift

    def notify_delegate(self):
        self.delegate.velocity_did_change(self._x_velocity(), self._y_velocity())
