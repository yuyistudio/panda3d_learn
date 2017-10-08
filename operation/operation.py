#encoding: utf8

from panda3d.core import *
from util import trigger
import variable

class Operation(object):
    def __init__(self):
        self.picker = trigger.MousePicker(variable.show_base.triggers)
        self.look_at_target = Vec3()
        variable.show_base.taskMgr.add(self.mouse_pick_task, "mouse_pick")

    def on_mouse_hit(self, hit):
        """
        return True if mouse hit should stop
        """
        if hit.get_into_node().getTag("type").startswith("ground"):
            sp = hit.get_surface_point(variable.show_base.render)
            self.look_at_target = sp
            return True
        return False

    def on_tool_hit(self, hit):
        variable.show_base.hero.tool.onHit(hit)

    def mouse_pick_task(self, task):
        # process triggers
        self.picker.onUpdate()
        entries = variable.show_base.triggers.getEntries()
        mouse_hit_processed = False
        for hit in entries:
            from_type = hit.get_from_node().getTag("type")
            to_type = hit.get_into_node().getTag("type")
            if from_type == "mouse":
                if not mouse_hit_processed:
                    mouse_hit_processed = self.on_mouse_hit(hit)
            elif from_type.startswith('tool'):
                self.on_tool_hit(hit)
            else:
                raise RuntimeError("unexpected")
        return task.cont
