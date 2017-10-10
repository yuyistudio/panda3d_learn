import physics
import primitive

from panda3d.ai import *
from panda3d.core import *
from direct.showbase.ShowBase import ShowBase
import logging
from direct.task import Task
from direct.interval.IntervalGlobal import Sequence
import light
import variable
from util import draw, keyboard
from script_anim import hero_animation
from .tool import TOOL_SUBPART, TOOL_ANIM_NAME, HeroTool

class Hero(object):
    def __init__(self):
        self.max_hero_speed = 18
        self.target_hero_speed = 0
        self.speed_lerp_factor = 3
        self._setup()
        self.tool = HeroTool(self)

    def _setup(self):
        self.anim_np = hero_animation.load_hero()
        self.anim_np.set_pos(Vec3(5, 5, 0))
        self.anim_np.enableBlend()
        self.anim_np.loop("walk")
        self.anim_np.setSubpartsComplete(False)
        self.anim_np.makeSubpart(TOOL_SUBPART, ["arm.r", 'weapon.r'])

        self.anim_np.setPlayRate(5, "walk")
        self.anim_np.setPlayRate(2, "idle")
        self.anim_np.setPlayRate(6, TOOL_ANIM_NAME, partName=TOOL_SUBPART)
        self.anim_np.setControlEffect("walk", 1)
        self.anim_np.setControlEffect("idle", 0.)
        self.anim_np.setControlEffect(TOOL_ANIM_NAME, 0)

        self.anim_np.loop("walk")
        self.anim_np.loop("idle")

        self.physics_np = variable.show_base.physics_world.addBoxCollider(self.anim_np, mass=1, bit_mask=variable.BIT_MASK_HERO)
        self.rigid_body = self.physics_np.node()
        self.physics_np.setTag("type", "hero")

        variable.show_base.accept("b", self.getBored)
        variable.show_base.accept("n", self.getNotBored)
        self.boring_anim = "boring"
        self.anim_np.setPlayRate(1.1, self.boring_anim)

    def getBored(self):
        self.anim_np.loop(self.boring_anim)
        self.anim_np.setControlEffect(self.boring_anim, 100)

    def getNotBored(self):
        self.anim_np.stop(self.boring_anim)
        self.anim_np.setControlEffect(self.boring_anim, 0)

    def getNP(self):
        return self.physics_np

    def onUpdate(self, dt):
        self._movementControl(dt)
        self.tool.onUpdate(dt)

    def lookAt(self, target_point):
        tp = target_point
        tp.setZ(self.physics_np.getZ())
        if (tp - self.physics_np.get_pos()).length() > 0.2:
            self.physics_np.look_at(tp)

    def _movementControl(self, dt):
        dx, dy = keyboard.get_direction()
        direction = Vec3(dx, dy, 0)
        if direction.length() > 0.01:
            self.target_hero_speed = self.max_hero_speed
        else:
            self.target_hero_speed = 0

        speed_vector = self.rigid_body.getLinearVelocity()
        current_z = speed_vector.get_z()
        speed_vector.set_z(0)
        current_speed = speed_vector.length()
        new_speed = current_speed + (self.target_hero_speed - current_speed) * dt * self.speed_lerp_factor
        new_v = direction.normalized() * new_speed
        new_v.setZ(current_z)
        self.rigid_body.setLinearVelocity(new_v)

        # setup animation weights
        speed_ratio = new_speed / self.max_hero_speed
        self.anim_np.setControlEffect("walk", min(1, speed_ratio))
        self.anim_np.setControlEffect("idle", min(1, 1 - speed_ratio))
