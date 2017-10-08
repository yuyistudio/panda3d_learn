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
from util import draw, keyboard, trigger
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
        self.hero_np = hero_animation.load_hero()
        variable.show_base.triggers.addCollider(trigger.addCollisionBox(self.hero_np, variable.BIT_MASK_HERO, 'hero', to_enabled=True))
        self.hero_np.set_pos(Vec3(5, 5, 0))
        self.hero_np.enableBlend()
        self.hero_np.loop("walk")
        self.hero_np.setSubpartsComplete(False)
        self.hero_np.makeSubpart(TOOL_SUBPART, ["arm.r", 'weapon.r'])
        self.hero_np.enableBlend()

        self.hero_np.setPlayRate(5, "walk")
        self.hero_np.setPlayRate(2, "idle")
        self.hero_np.setPlayRate(6, TOOL_ANIM_NAME, partName=TOOL_SUBPART)
        self.hero_np.setControlEffect("walk", 1)
        self.hero_np.setControlEffect("idle", 0.)
        self.hero_np.setControlEffect(TOOL_ANIM_NAME, 0)

        self.hero_np.loop("walk")
        self.hero_np.loop("idle")

        self.hero_body = variable.show_base.physics_world.addBoxCollider(self.hero_np, density=300, is_static=False, auto_transform=True, auto_disable=False)
        self.hero_np.setTag("type", "hero")

        variable.show_base.accept("b", self.getBored)
        variable.show_base.accept("n", self.getNotBored)
        self.boring_anim = "boring"
        self.hero_np.setPlayRate(1.1, self.boring_anim)

    def getBored(self):
        self.hero_np.loop(self.boring_anim)
        self.hero_np.setControlEffect(self.boring_anim, 100)

    def getNotBored(self):
        self.hero_np.stop(self.boring_anim)
        self.hero_np.setControlEffect(self.boring_anim, 0)

    def getNP(self):
        return self.hero_np

    def onUpdate(self, dt):
        self._movementControl(dt)
        self.tool.onUpdate(dt)

    def lookAt(self, target_point):
        if (target_point - self.hero_np.get_pos()).length() > 0.1:
            target_point.set_z(self.hero_np.get_pos().get_z())
            self.hero_np.look_at(target_point)
        self.hero_body.set_quaternion(self.hero_np.getQuat())

    def _movementControl(self, dt):
        dx, dy = keyboard.get_direction()
        direction = Vec3(dx, dy, 0)
        if direction.length() > 0.01:
            self.target_hero_speed = self.max_hero_speed
        else:
            self.target_hero_speed = 0

        speed_vector = self.hero_body.get_linear_vel()
        current_z = speed_vector.get_z()
        speed_vector.set_z(0)
        current_speed = speed_vector.length()
        new_speed = current_speed + (self.target_hero_speed - current_speed) * dt * self.speed_lerp_factor
        new_v = direction.normalized() * new_speed
        new_v.setZ(current_z)
        self.hero_body.set_linear_vel(new_v)

        # setup animation weights
        speed_ratio = new_speed / self.max_hero_speed
        self.hero_np.setControlEffect("walk", min(1, speed_ratio))
        self.hero_np.setControlEffect("idle", min(1, 1-speed_ratio))
