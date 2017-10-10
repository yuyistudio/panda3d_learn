#encoding: utf8

from panda3d.core import *
import variable

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

class ToolInfo(object):
    def __init__(self, tool_np, ghost_np):
        self.tool_np = tool_np
        self.ghost_np = ghost_np

class HeroTool(object):
    def __init__(self, hero):
        self.hero = hero
        variable.show_base.accept("mouse1", self.useTool)
        variable.show_base.accept("c", lambda: self.changeTool("sword"))
        variable.show_base.accept("v", lambda: self.changeTool("axe"))


        self.tool_weight = 0
        self.target_tool_weight = 0
        self.tool_weight_lerp = 10

        self.hit_recorder = HitRecorder()

        self.name2tool = {}
        self.tool_names = 'sword axe'.split()
        for tool_name in self.tool_names:
            tool_np = variable.show_base.loader.loadModel("blender/%s" % tool_name)
            ghost_np = variable.show_base.physics_world.addBoxTrigger(tool_np, variable.BIT_MASK_TOOL)
            self.name2tool[tool_name] = ToolInfo(tool_np, ghost_np)
            variable.show_base.physics_world.world.removeGhost(ghost_np.node())
        self.current_tool_name = "axe"
        self.changeTool("axe")

    def changeTool(self, tool_name):
        current_tool = self.getCurrentTool()
        variable.show_base.physics_world.world.removeGhost(current_tool.ghost_np.node())
        current_tool.tool_np.detachNode()
        tool = self.name2tool.get(tool_name)
        assert(tool)
        variable.show_base.physics_world.world.attachGhost(tool.ghost_np.node())
        weapon_slot = self.hero.anim_np.exposeJoint(None, "modelRoot", "weapon.r")
        tool.tool_np.reparentTo(weapon_slot)
        self.current_tool_name = tool_name

    def useTool(self):
        self.hit_recorder.reset()
        if self.target_tool_weight > 0.1:
            return
        self.hero.anim_np.play(TOOL_ANIM_NAME, partName=TOOL_SUBPART)
        self.target_tool_weight = 10

    def getCurrentTool(self):
        current_tool = self.name2tool.get(self.current_tool_name)
        return current_tool

    def _checkHit(self):
        if self.target_tool_weight < 1:
            return
        ghost = self.getCurrentTool().ghost_np.node()  # get_trigger_np().get_ghost_node()
        for node in ghost.getOverlappingNodes():
            physical_np = node.getPythonTag("instance")
            if not physical_np:
                continue
            name = physical_np.getName()
            if self.hit_recorder.already_hit(name):  # tool aren't being used OR has been used already
                return
            print 'node:', physical_np
            node.setLinearVelocity((physical_np.getPos() - self.hero.physics_np.getPos()).normalized() * 5)
            print 'hit:', name

    def onUpdate(self, dt):
        self._toolAnimation(dt)
        self._checkHit()


    def _toolAnimation(self, dt):
        # tool animation control
        self.tool_weight = self.tool_weight + (self.target_tool_weight - self.tool_weight) * dt * self.tool_weight_lerp
        self.hero.anim_np.setControlEffect(TOOL_ANIM_NAME, self.tool_weight, partName=TOOL_SUBPART)
        if not self.hero.anim_np.getCurrentAnim(partName=TOOL_SUBPART):
            self.target_tool_weight = 0
