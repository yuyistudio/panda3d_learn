# encoding: utf8


__author__ = 'Leon'
from panda3d.core import Vec3


class FloatLerp(object):
    def __init__(self, init_value, min_value, max_value, lerp_factor):
        self.value = init_value
        self.min_value = min_value
        self.max_value = max_value
        self.lerp_factor = lerp_factor
        self.target_value = init_value

    def change_target(self, target_value):
        self.target_value = max(self.min_value, min(self.max_value, self.target_value + target_value))

    def change_value(self, change_value):
        self.value += change_value
        self.target_value = max(self.min_value, min(self.max_value, self.target_value + change_value))

    def set_target(self, target_value):
        self.target_value = max(self.min_value, min(self.max_value, target_value))

    def to_max(self):
        self.target_value = self.max_value

    def to_min(self):
        self.target_value = self.min_value

    def get_percentage(self):
        return (self.value - self.min_value) / (self.max_value - self.min_value)

    def reset(self):
        self.value = self.min_value
        self.target_value = self.min_value

    def lerp(self, dt):
        self.value = self.value + (self.target_value - self.value) * self.lerp_factor * dt
        return self.value


class LerpVec3(object):
    def __init__(self, lerp_factor):
        self.pos = None
        self.target_pos = None
        self.lerp_factor = lerp_factor
        self._initialized = False

    def set_target(self, target):
        if not self._initialized:
            self._initialized = True
            self.pos = target
        self.target_pos = target

    def lerp(self, dt):
        if not self._initialized:
            return Vec3(0, 0, 0)
        factor = dt * self.lerp_factor
        x = self.pos.getX() + (self.target_pos.getX() - self.pos.getX()) * factor
        y = self.pos.getY() + (self.target_pos.getY() - self.pos.getY()) * factor
        z = self.pos.getZ() + (self.target_pos.getZ() - self.pos.getZ()) * factor
        self.pos = Vec3(x, y, z)
        return self.pos