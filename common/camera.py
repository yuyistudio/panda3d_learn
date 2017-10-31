# encoding: utf8

__author__ = 'Leon'


from util import lerp_util, log
from panda3d.core import Vec3
from variable.global_vars import G


class CameraManager(object):
    def __init__(self):
        self.cam_lerper = lerp_util.LerpVec3(4.3210)
        self.cam_pos_lerper = lerp_util.FloatLerp(30, 15, 2000 if G.debug else 40, 6.666)
        self.target_cam_pos = 30

        self.factor1 = 1
        self.factor2 = .7
        self._pos_offset = Vec3()
        G.accept('wheel_up', self._wheel_event, [-1])
        G.accept('wheel_down', self._wheel_event, [1])

    def _wheel_event(self, value):
        self.cam_pos_lerper.change_value(value * 5)

    def look_at(self, pos):
        self.cam_lerper.set_target(pos + self._pos_offset)

    def on_update(self, dt):
        lerped_pos = self.cam_lerper.lerp(dt)
        cam_pos = self.cam_pos_lerper.lerp(dt)
        dir = '+y'
        if dir == '+y':
            sign = 1
            self._pos_offset = Vec3(0, -sign*cam_pos * self.factor1, cam_pos * self.factor2)
            G.cam.set_pos(lerped_pos)
            G.cam.look_at(lerped_pos + Vec3(0, sign*self.factor1, -self.factor2))
        if dir == '-y':
            sign = -1
            self._pos_offset = Vec3(0, -sign * cam_pos * self.factor1, cam_pos * self.factor2)
            G.cam.set_pos(lerped_pos)
            G.cam.look_at(lerped_pos + Vec3(0, sign * self.factor1, -self.factor2))
        if dir == '+x':
            sign = 1
            self._pos_offset = Vec3(-sign * cam_pos * self.factor1, 0, cam_pos * self.factor2)
            G.cam.set_pos(lerped_pos)
            G.cam.look_at(lerped_pos + Vec3(sign * self.factor1, 0, -self.factor2))
        if dir == '-x':
            sign = -1
            self._pos_offset = Vec3(-sign * cam_pos * self.factor1, 0, cam_pos * self.factor2)
            G.cam.set_pos(lerped_pos)
            G.cam.look_at(lerped_pos + Vec3(sign * self.factor1, 0, -self.factor2))

