#encoding: utf8

from panda3d.core import *
import variable
from util import trigger

TOOL_ANIM_NAME = "tool"
TOOL_SUBPART = "tool_subpart"

class HitRecorder(object):
    def __init__(self):
        self.ready = False
        self.hit_names = set()

    def already_hit(self, name):
        if not self.ready:
            return True
        l1 = len(self.hit_names)
        self.hit_names.add(name)
        return len(self.hit_names) == l1

    def reset(self):
        self.ready = True
        self.hit_names.clear()


class HeroTool(object):
    def __init__(self, hero):
        self.hero = hero
        variable.show_base.accept("mouse1", self.useTool)
        variable.show_base.accept("c", self.changeTool)

        self.tool_index = 0

        self.tool_weight = 0
        self.target_tool_weight = 0
        self.tool_weight_lerp = 10

        self.hit_recorder = HitRecorder()

        tools = {}
        for tool_name in 'sword axe'.split():
            tool = variable.show_base.loader.loadModel("blender/%s" % tool_name)
            variable.show_base.triggers.addCollider(trigger.addCollisionSegment(tool, variable.BIT_MASK_TOOL, "tool_" + tool_name,from_enabled=True))
            tools[tool_name] = tool
        self.tools = tools
        self.changeTool()

    def changeTool(self):
        current_tool = self.tools.values()[self.tool_index]
        current_tool.detachNode()

        self.tool_index += 1
        if self.tool_index >= len(self.tools):
            self.tool_index = 0
        tool = self.tools.values()[self.tool_index]

        print "change to:", self.tool_index, tool
        weapon_slot = self.hero.hero_np.exposeJoint(None, "modelRoot", "weapon.r")
        tool.reparentTo(weapon_slot)

    def useTool(self):
        self.hit_recorder.reset()
        if self.target_tool_weight > 0.1:
            return
        self.hero.hero_np.play(TOOL_ANIM_NAME, partName=TOOL_SUBPART)
        self.target_tool_weight = 10

    def onHit(self, hit_entry):
        np = hit_entry.get_into_node_path().getParent()
        if self.target_tool_weight < 1 or self.hit_recorder.already_hit(np.getName()):
            return
        print 'hit:',np.getName()

    def onUpdate(self, dt):
        self._toolAnimation(dt)

    def _toolAnimation(self, dt):
        # tool animation control
        self.tool_weight = self.tool_weight + (self.target_tool_weight - self.tool_weight) * dt * self.tool_weight_lerp
        self.hero.hero_np.setControlEffect(TOOL_ANIM_NAME, self.tool_weight, partName=TOOL_SUBPART)
        if not self.hero.hero_np.getCurrentAnim(partName=TOOL_SUBPART):
            self.target_tool_weight = 0
