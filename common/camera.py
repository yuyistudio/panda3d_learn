# encoding: utf8

__author__ = 'Leon'


from util import lerp_util
from panda3d.core import Vec3
from variable.global_vars import G


class CameraManager(object):
    def __init__(self):
        self.cam_lerper = lerp_util.LerpVec3(4.3210)
        self.cam_pos = 40
        self.factor1 = 1
        self.factor2 = .7
        self._pos_offset = Vec3(0, -self.cam_pos * self.factor1, self.cam_pos * self.factor2)

        G.accept('wheel_up', self._wheel_event, [-1])
        G.accept('wheel_down', self._wheel_event, [1])

    def _wheel_event(self, value):
        self.cam_pos += value * 5
        self._pos_offset = Vec3(0, -self.cam_pos * self.factor1, self.cam_pos * self.factor2)

    def look_at(self, pos):
        self.cam_lerper.set_target(pos + self._pos_offset)

    def on_update(self, dt):
        lerped_pos = self.cam_lerper.lerp(dt)
        G.cam.set_pos(lerped_pos)
        G.cam.look_at(lerped_pos + Vec3(0, self.factor1, -self.factor2))
