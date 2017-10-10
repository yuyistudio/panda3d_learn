#encoding: utf8

from panda3d.core import *
from util import trigger
import variable

class Operation(object):
    def __init__(self):
        self.picker = trigger.MousePicker(variable.show_base.triggers)
        self.look_at_target = Vec3()
        variable.show_base.taskMgr.add(self.mouse_pick_task, "mouse_pick")

    def on_tool_hit(self, hit):
        variable.show_base.hero.tool.onHit(hit)

    def on_hit_something(self, hit):
        pass

    def mouse_pick_task(self, task):
        # process triggers
        self.picker.onUpdate()
        hits = variable.show_base.physics_world.mouseHit()
        for hit in hits:
            physical_node = hit.getNode()
            hit_point = hit.getHitPos()
            # hit_normal = hit.getHitNormal()
            hit_type = physical_node.getTag("type")
            if hit_type == "ground":
                self.look_at_target = hit_point
            else:
                self.on_hit_something(hit)
        return task.cont
