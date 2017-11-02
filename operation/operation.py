#encoding: utf8

from panda3d.core import *
from util import trigger, log, freq
from variable.global_vars import G
from util import keyboard
from entity_system.base_components import ObjHeroController


class Operation(object):
    """
    Operation为游戏游玩时的玩家输入。不包括主菜单。
    OP_xxx 表示一个接受玩家输入的操作
    """
    def __init__(self, op_target):
        self.target_ref = None
        self.controller = None
        self.set_target(op_target)
        self.picker = trigger.MousePicker(G.triggers)
        self.mouse_pos_on_ground = Vec3()
        self._hit_obj_ref = None
        self._hit_point = None
        self._left_key = keyboard.KeyStatus(
            'mouse1',
            self.OP_left_mouse_click, self.OP_left_mouse_hold,
        )
        self._enabled = False
        G.taskMgr.add(self.mouse_pick_task, "mouse_pick")
        G.accept('space', self.OP_craft)

    def set_enabled(self, enabled):
        self._enabled = enabled

    def on_tool_hit(self, hit):
        self.target_ref().tool.onHit(hit)

    def mouse_pick_task(self, task):
        if not self._enabled:
            return task.cont

        self._hit_point = None
        self._hit_obj_ref = None
        # process triggers
        self.picker.onUpdate()
        hits = G.physics_world.mouseHit()
        hit_info = []
        for hit in hits:
            physical_node = hit.getNode()
            hit_point = hit.getHitPos()
            # hit_normal = hit.getHitNormal()
            hit_type = physical_node.get_python_tag("type")
            if hit_type == "ground":
                self.mouse_pos_on_ground = hit_point
            elif hit_type == 'object':
                entity = physical_node.get_python_tag('entity')()
                if not entity.is_destroyed():
                    dist = (hit_point - G.cam.get_pos()).length()
                    hit_info.append((dist, physical_node, hit_point))
            elif hit_type == 'hero':
                pass
            else:
                pass  # assert False, 'hit type:%s, physics node: %s' % (hit_type, physical_node)

        # 从近到远排个序，最近的那个算被点到了
        if hit_info:
            hit_info.sort(key=lambda v: v[0])
            self._hit_obj_ref = hit_info[0][1].get_python_tag('entity')
            self._hit_point = hit_info[0][2]

        return task.cont

    def set_target(self, new_target):
        import weakref
        if new_target:
            self.target_ref = weakref.ref(new_target)
            self.controller = new_target.get_component(ObjHeroController)

    def get_center_pos(self):
        if self.target_ref():
            return self.target_ref().get_pos()
        return Vec3()

    def on_update(self, dt):
        if not self._enabled:
            return

        self.OP_keyboard_move()
        self._left_key.on_update(dt)

    def _do_work_to_entity(self, entity, is_left_mouse):

        if not self._enabled:
            return
        from inventory_system.common.components import ItemTool

        fake_tool = ItemTool({
            "action_types": {
                "pick": {"duration": 10},
                "cut": {"duration": 1},
            },
            "distance": 1
        })
        key = 'left' if is_left_mouse else 'right'
        action_type = entity.allow_action(fake_tool, key, None)
        if not action_type:
            log.debug('action not allowed for entity: %s', entity)
            return

        # 远程武器应当将tool的distance设置得比较大。
        # 这样所有的action都可以抽象为 行走+动作 了。
        gap = self.target_ref().get_radius() + entity.get_radius() + fake_tool.get_distance()
        self.controller.set_context('move_min_dist', gap)
        self.controller.set_context('target_pos', entity.get_pos())
        self.controller.set_context('buffered_work', {
            'action_type': action_type,
            'target_entity': entity,
            'key': key,
            'ctrl': False,
            'min_dist': gap,
        })
        return

    def OP_left_mouse_click(self):
        if not self._enabled:
            return
        log.debug("is click")
        self.OP_left_mouse_hold()

    def OP_left_mouse_hold(self):
        if not self._enabled:
            return

        if self._hit_obj_ref:
            obj = self._hit_obj_ref()
            if obj:
                self._do_work_to_entity(obj, True)
                return
        self.controller.set_context('buffered_work', None)
        self.controller.set_context('move_min_dist', 0)
        self.controller.set_context('target_pos', self.mouse_pos_on_ground)

    def OP_craft(self):
        if not self._enabled:
            return

        self.controller.set_context('buffered_work', None)
        self.controller.emit_event('craft')

    def OP_keyboard_move(self):
        if not self._enabled:
            return

        dx, dy = keyboard.get_direction()
        if dx == 0 and dy == 0:
            self.controller.set_context('target_dir', None)
            return
        self.controller.set_context('buffered_work', None)
        move_dir = Vec3(dx, dy, 0)
        self.controller.set_context('target_dir', move_dir)
