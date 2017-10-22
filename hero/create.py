# encoding: utf8

from panda3d.core import *
from variable.global_vars import G
from util import keyboard
from script_anim import hero_animation
from .tool import TOOL_SUBPART, TOOL_ANIM_NAME, HeroTool
import config
from util import lerp_util


class Hero(object):
    def __init__(self):
        self.hero_lerper = lerp_util.FloatLerp(0, 0, max_value=10, lerp_factor=3.3)
        self.cam_lerper = lerp_util.LerpVec3(Vec3(0, 0, 0), 6.3)
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

        # self.physics_np = G.physics_world.addBoxCollider(self.model_np, mass=1, bit_mask=config.BIT_MASK_HERO)
        self.physics_np = G.physics_world.add_player_controller(self.anim_np, bit_mask=config.BIT_MASK_HERO)
        self.physics_np.setTag("type", "hero")
        self.rigid_body = self.physics_np.node()

        G.accept("b", self.getBored)
        G.accept("n", self.getNotBored)
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
        self.lookAt(G.game_mgr.operation.look_at_target)
        self._movementControl(dt)
        self.tool.onUpdate(dt)

        # camera control
        cam_pos = 30
        factor1 = 1
        factor2 = 2
        target_pos = G.game_mgr.hero.getNP().get_pos() + Vec3(0, -cam_pos * factor1, cam_pos * factor2)
        self.cam_lerper.set_target(target_pos)
        lerped_pos = self.cam_lerper.lerp(dt)
        G.cam.set_pos(lerped_pos)
        G.cam.look_at(lerped_pos + Vec3(0, factor1, -factor2))

        # setup animation weights
        speed_ratio = self.hero_lerper.get_percentage()
        self.anim_np.setControlEffect("walk", min(1, speed_ratio))
        self.anim_np.setControlEffect("idle", min(1, 1 - speed_ratio))

    def lookAt(self, target_point):
        np = self.physics_np
        tp = target_point
        tp.setZ(np.getZ())
        if (tp - np.get_pos()).length() > 0.2:
            np.look_at(tp)

    def _movementControl(self, dt):
        dx, dy = keyboard.get_direction()
        direction = Vec3(dx, dy, 0)
        if direction.length() > 0.01:
            self.hero_lerper.to_max()
        else:
            self.hero_lerper.to_min()
        direction = direction.normalized()
        new_speed = self.hero_lerper.lerp(dt)
        self.rigid_body.setLinearMovement(direction * new_speed, False)  # False -> World, True -> Local

