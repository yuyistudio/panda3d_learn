#encoding: utf8

from panda3d.core import *
from variable.global_vars import G
import config
from entity_system.base_components import ObjAnimator


class HeroEquipmentModels(object):
    """
    处理主角装备模型
    """
    # 定义主角支持的slot
    SLOT_TO_BONE = {
        "right_hand": "weapon.r",
    }

    def __init__(self, hero):
        self.hero = hero
        self.name2tool = {}
        self.tool_names = 'sword axe'.split()
        for tool_name in self.tool_names:
            tool_np = G.loader.loadModel("assets/blender/%s" % tool_name)
            self.name2tool[tool_name] = tool_np
        self.current_tool_name = "axe"

    def change_model(self, slot, tool_name):
        """
        :param slot:
        :param tool_name:
        :return: True表示换装备成功。
        """
        current_tool = self.get_current_model()
        current_tool.detachNode()
        if not tool_name:
            return True
        tool = self.name2tool.get(tool_name)
        assert(tool)
        actor = self.hero.get_component(ObjAnimator).get_actor_np()
        assert actor
        weapon_slot = actor.exposeJoint(None, "modelRoot", self.SLOT_TO_BONE[slot])
        tool.reparentTo(weapon_slot)
        self.current_tool_name = tool_name
        return True

    def get_current_model(self):
        current_tool = self.name2tool.get(self.current_tool_name)
        return current_tool

