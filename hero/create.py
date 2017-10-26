# encoding: utf8

from panda3d.core import *

from variable.global_vars import G
from util import keyboard
import config
from util import lerp_util
from common.animator import Animator

hero_config = {
    'filepath': "./assets/blender/hero.egg",
    'animations': {
        "walk": {
            "events":[['start', 0], ['middle', 40]],
            "rate": 3,
        },
        "tool": {
            'rate': 4.1
        },
        "pickup": {
            "events": [['pickup', 10], ['done', 20]],
            "rate": 3,
        },
        "idle": {
        }
    },
    'default': 'idle',
}

class MoveController(object):
    def __init__(self, physics_np):
        self._move_speed_lerper = lerp_util.FloatLerp(0, 0, max_value=10, lerp_factor=6.543210)
        self._last_move_direction = Vec3(0, 0, 0)
        self.physics_np = physics_np
        self.rigid_body = physics_np.node()
        self._current_speed = 0

    def _look_at(self, target_point):
        target_point.setZ(self.physics_np.getZ())
        if (target_point - self.physics_np.get_pos()).length() > 0.2:
            self.physics_np.look_at(target_point)

    def on_update(self, dt, target_point):
        self._move(dt)
        self._look_at(target_point)
        return self._current_speed

    def stop(self):
        self._move_speed_lerper.reset()

    def _move(self, dt):
        dx, dy = keyboard.get_direction()
        direction = Vec3(dx, dy, 0)
        if direction.length() > 0.01:
            self._move_speed_lerper.to_max()
            self._last_move_direction = direction.normalized()
        else:
            self._move_speed_lerper.to_min()
        new_speed = self._move_speed_lerper.lerp(dt)
        self.rigid_body.setLinearMovement(self._last_move_direction * new_speed,
                                          False)  # False -> World, True -> Local
        self._current_speed = new_speed

    def get_speed(self):
        return self._current_speed


class Hero(object):
    def __init__(self):
        self.cam_lerper = lerp_util.LerpVec3(4.3210)
        self._animator = Animator(hero_config, self)
        self.anim_np = self._animator.get_actor_np()
        self._animator.play('idle', once=False)
        self.physics_np = G.physics_world.add_player_controller(self.anim_np, bit_mask=config.BIT_MASK_HERO)
        self.controller = MoveController(self.physics_np)
        G.accept('mouse1', self.use_tool)

    def use_tool(self):
        self.controller.stop()
        self._animator.play('tool', once=True)

    def on_update(self, dt):
        self.controller.on_update(dt, G.game_mgr.operation.look_at_target)
        if self.controller.get_speed() > 0.4:
            self._animator.play('walk', once=True)
        elif self._animator.get_actor_np().getCurrentAnim() == 'walk':
            self._animator.play('idle', once=False)
        self._animator.on_update()

        hero_pos = self.physics_np.get_pos()

        # camera control
        cam_pos = 30
        factor1 = 1
        factor2 = .7
        target_pos = hero_pos + Vec3(0, -cam_pos * factor1, cam_pos * factor2)
        self.cam_lerper.set_target(target_pos)
        lerped_pos = self.cam_lerper.lerp(dt)
        G.cam.set_pos(lerped_pos)
        G.cam.look_at(lerped_pos + Vec3(0, factor1, -factor2))

        # sun light
        pos_offset = Vec3(10, -10, 10)
        look_at_offset = Vec3(0, 0, 0)
        sun_np = G.dir_light
        sun_np.set_pos(hero_pos + pos_offset)
        sun_np.look_at(hero_pos + look_at_offset)
