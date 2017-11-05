#encoding: utf8

from panda3d.core import *
from util import trigger, log, freq
from variable.global_vars import G
from util import keyboard
from entity_system.base_components import ObjHeroController


class GroundEntity(object):
    """
    模拟对object的操作。
    """
    def __init__(self):
        self._pos = None

    def set_pos(self, pos):
        self._pos = pos

    def get_pos(self):
        return self._pos

    def allow_action(self, tool, key_type, mouse_entity):
        if mouse_entity:
            if key_type == 'left':
                return {'action_type': 'throw_item_at', 'anim_name': 'pickup', 'event_name': 'pickup'}
            else:
                return {'action_type': 'trow_item_now', 'anim_name': 'pickup', 'event_name': 'pickup'}
        return False

    def get_radius(self):
        return 0

    def do_action(self, tool, key_type, mouse_entity):
        if mouse_entity:
            if key_type == 'left':
                G.game_mgr.put_mouse_item_on_ground(self._pos)
            else:
                log.debug("throw item now!")


class Operation(object):
    """
    Operation为游戏游玩时的玩家输入。不包括主菜单。
    OP_xxx 表示一个接受玩家输入的操作
    """
    def __init__(self, op_target):
        self._ground_entity = GroundEntity()
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
            self._on_hold_done,
        )
        self._right_key = keyboard.KeyStatus(
            'mouse3',
            self.OP_right_mouse_click, None, None
        )

        self._enabled = False
        self._hold_to_move = False
        G.taskMgr.add(self.mouse_pick_task, "mouse_pick")
        G.accept('space', self.OP_craft)

    def _on_hold_done(self):
        self._hold_to_move = False

    def set_enabled(self, enabled):
        if enabled:
            # 为啥要加个延时呢？因为DirectGUI的点击事件触发了之后，让operation enable了。
            # 这个事件还会再触发operation的点击。
            # DirectGUI比较挫，无法知道鼠标是不是正在GUI上。暂时通过这种trick的方式解决问题吧。
            def defered(task):
                self._enabled = enabled
                return task.done
            G.taskMgr.doMethodLater(.33, defered, 'enable_operation')
        else:
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
                if entity and not entity.is_destroyed():
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
        if G.gui_mgr.is_mouse_on_gui():
            return
        self._left_key.on_update(dt)
        self._right_key.on_update(dt)

        # 鼠标显示
        if self._hit_obj_ref:
            ent = self._hit_obj_ref()
            if ent:
                G.gui_mgr.get_mouse_gui().set_object_info(ent.get_name())
        else:
            G.gui_mgr.get_mouse_gui().set_object_info("")

    def _do_work_to_entity(self, entity, key):
        if not self._enabled:
            return False
        log.debug("do work to entity!")
        from inventory_system.common.components import ItemTool

        fake_tool = ItemTool({
            "action_types": {
                "pick": {"duration": 10},
                "cut": {"duration": 1},
            },
            "distance": 1
        })
        mouse_item = G.game_mgr.get_mouse_item()
        action_info = entity.allow_action(fake_tool, key, mouse_item)
        if not action_info:
            log.debug('action not allowed for entity: %s', entity)
            return False
        assert 'action_type' in action_info and 'anim_name' in action_info

        # 远程武器应当将tool的distance设置得比较大。
        # 这样所有的action都可以抽象为 行走+动作 了。
        gap = self.target_ref().get_radius() + entity.get_radius() + fake_tool.get_distance()
        self.controller.set_context('move_min_dist', gap)
        self.controller.set_context('target_pos', entity.get_pos())
        extra_info = {
            'target_entity': entity,
            'key'          : key,
            'ctrl'         : False,
            'min_dist'     : gap,
        }
        extra_info.update(action_info)
        self.controller.set_context('buffered_work', extra_info)
        return True

    def OP_right_mouse_click(self):
        self.OP_on_mouse_clicked('right')

    def OP_left_mouse_click(self):
        self.OP_on_mouse_clicked('left')

    def OP_on_mouse_clicked(self, key):
        if not self._enabled:
            return
        if G.gui_mgr.is_mouse_on_gui():
            return
        if not self._click_on_object(key):
            self._move_to_mouse(key)

    def OP_left_mouse_hold(self):
        if not self._enabled:
            return
        if G.gui_mgr.is_mouse_on_gui():
            return

        if not self._hold_to_move:
            if self._click_on_object('left'):
                return
        self._hold_to_move = True
        self._move_to_mouse('left')

    def _move_to_mouse(self, key):
        if key == 'left':
            self.controller.set_context('buffered_work', None)
            self.controller.set_context('move_min_dist', 0)
            self.controller.set_context('target_pos', self.mouse_pos_on_ground)

    def _click_on_object(self, key):
        """
        :return: True成功进行的动作
        """
        if self._hit_obj_ref:
            obj = self._hit_obj_ref()
        else:
            self._ground_entity.set_pos(self.mouse_pos_on_ground)
            obj = self._ground_entity
        if self._do_work_to_entity(obj, key):
            return True
        return False

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
