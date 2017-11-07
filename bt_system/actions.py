# encoding: utf8

__author__ = 'Leon'


from behaviour_tree import *
from panda3d.core import Vec3
from entity_system import base_components as coms
from util import log
from entity_system.base_components import *

Priority = UntilSuccess
Decision = ActionFn

from inventory_system.common.components import ItemTool


class BaseAction(IActionNode):
    def __init__(self, name):
        IActionNode.__init__(self, name)
        self.bt = BehaviourTree(0, None)  # Just for grammatical hints.
        self.__entity_weak_ref__ = None
        self._animator = None
        self._controller = None

    def on_init(self):
        entity_ref = self.bt.get('entity')
        ent = entity_ref()
        self.__entity_weak_ref__ = entity_ref  # 只保留弱引用，避免循环引用
        assert ent, 'should set entity in context at first, context: %s' % self.bt._context
        self._animator = ent.get_component(coms.ObjAnimator)
        self._controller = ent.get_component(coms.ObjTransformController)
        assert self._animator and self._controller

    def get_entity(self):
        return self.__entity_weak_ref__()


class ActionAnim(BaseAction):
    def __init__(self, name, anim_name, events):
        """
        :param name:
        :param anim_name:
        :param events:
            {
                "pickup": "running",
                "done": "success",
            }
        :return:
        """
        BaseAction.__init__(self, name)
        self._anim_name = anim_name
        self._events = {}
        for anim_event_name, anim_event_status in events.iteritems():
            event_key = 'anim.%s.%s' % (self._anim_name, anim_event_name)
            event_value = STR_TO_STATUS[anim_event_status]
            self._events[event_key] = event_value

    def on_enter(self):
        pass

    def _anim_cb(self, event_name):
        status = self._events.get(event_name)
        if status:
            return status
        return RUNNING

    def on_action(self):
        self._animator.play(self._anim_name, once=True)
        for event_name in self._events.keys():
            self.bt.wait_for_event(event_name, self._anim_cb)
        return RUNNING

    def on_finish(self, is_abort, status):
        pass


class ActionMove(BaseAction):
    def __init__(self, name, stop_when_blocked=True):
        IActionNode.__init__(self, name)
        self._last_pos = None
        self._linger_timer = 0
        self._auto_stop = stop_when_blocked

    def on_enter(self):
        self._linger_timer = 0
        self._last_pos = Vec3()

    def on_action(self):
        current_pos = self.get_entity().get_pos()
        target_dir = self.bt.get('target_dir')
        if target_dir:
            self.bt.set('target_pos', None)
        else:
            target_pos = self.bt.get('target_pos')

        if not target_dir and not target_pos:
            return FAIL

        # 处理被阻挡的情况
        if self._auto_stop:
            dist_from_last = (current_pos - self._last_pos).length()
            self._last_pos = current_pos
            if dist_from_last < 0.02:
                self._linger_timer += self.bt.dt
                if self._linger_timer > .5:
                    self._linger_timer = 0
                    return FAIL
            else:
                self._linger_timer = 0

        # 向某个方向移动
        if target_dir:
            self._controller.look_at(current_pos + target_dir)
            dir_vec3 = target_dir.normalized()
            self._controller.move_towards(dir_vec3[0], dir_vec3[1], self.bt.dt)
            return RUNNING

        # 向某个点移动
        if not target_pos:
            return FAIL
        dir_vec3 = target_pos - current_pos
        dir_vec3.setZ(0)
        if dir_vec3.length() > max(.5, (self.bt.get('move_min_dist') or .5)):
            self._controller.look_at(target_pos)
            dir_vec3 = dir_vec3.normalized()
            self._controller.move_towards(dir_vec3[0], dir_vec3[1], self.bt.dt)
            return RUNNING
        else:
            return SUCCESS

    def on_finish(self, is_abort, status):
        self.bt.set('target_dir', None)
        self.bt.set('target_pos', None)
        self._controller.stop()


class ActionRandomTargetPos(BaseAction):
    def __init__(self, name, pos_range):
        BaseAction.__init__(self, name)
        self._range = pos_range

    def on_action(self):
        target_pos = Vec3(
            random.random() * self._range,
            random.random() * self._range,
            random.random() * self._range,
        )
        self.bt.set('target_pos', target_pos)
        return SUCCESS


class ActionIdle(BaseAction):
    def __init__(self, name, seconds, after_status):
        BaseAction.__init__(self, name)
        self._seconds = seconds
        self._after_status = after_status

    def on_action(self):
        self.bt.wait_for_seconds(self._seconds, self._after_status)
        return RUNNING


class ActionDebugFatal(BaseAction):
    def __init__(self, name):
        BaseAction.__init__(self, name)

    def on_action(self):
        assert False, 'unepxected action: %s' % self._name


class ActionHeroWanderDecision(BaseAction):
    def __init__(self, name, wander_range=10):
        BaseAction.__init__(self, name)
        self._wander_range = wander_range

    def on_action(self):
        pos = self.get_entity().get_pos()
        random_pos = Vec3(
            (random.random() - 0.5) * 2 * self._wander_range,
            (random.random() - 0.5) * 2 * self._wander_range,
            (random.random() - 0.5) * 2 * self._wander_range,
        )
        target_pos = pos + random_pos
        self.bt.set('target_pos', target_pos)
        return SUCCESS


class ActionHeroWork(BaseAction):
    def __init__(self, name, wander_range=10):
        BaseAction.__init__(self, name)
        self._wander_range = wander_range
        self._buffered_work = None

    def on_action(self):
        buffered_work = self.bt.get('buffered_work')
        if buffered_work:
            self.do_work(buffered_work)
            return RUNNING
        return FAIL

    def do_work(self, buffered_work):
        self._buffered_work = buffered_work
        target_entity = buffered_work['target_entity']
        key = buffered_work.get('key', 'left')
        is_ctrl = buffered_work.get('ctrl', False)

        # check是否太远不能工作. 远程action将min_dist设置得足够远即可。
        diff_vec3 = self.get_entity().get_pos() - target_entity.get_pos()
        diff_vec3.set_z(0)
        dist = diff_vec3.length()
        if dist > buffered_work.get('min_dist', 2):
            log.debug('%s > %s', dist, buffered_work.get('min_dist', 2))
            return FAIL

        # 开始工作
        if target_entity:
            self._controller.look_at(target_entity.get_pos())
        anim = buffered_work.get('anim_name', 'tool')
        self._animator.play(anim, once=True)
        event_name = buffered_work.get('event_name', 'done')
        self.bt.wait_for_event('anim.%s.%s' % (anim, event_name), self._anim_cb)
        return RUNNING

    def _anim_cb(self, event_name):
        buffered_work = self.bt.get('buffered_work')
        if buffered_work and buffered_work == self._buffered_work:
            log.debug('work done: %s', buffered_work.get('anim_name', 'craft'))

            entity = buffered_work['target_entity']
            tool = G.operation.get_action_tool()
            if tool != buffered_work.get('tool'):
                # 执行动作时，不能中途换工具的哦~
                return FAIL
            if entity.do_action(buffered_work, tool, buffered_work['key'], G.game_mgr.get_mouse_item()):
                tool.on_use(buffered_work['action_type'])
                return SUCCESS
            else:
                return FAIL
        else:
            log.debug('work not found')
            return FAIL

    def on_finish(self, is_abort, status):
        self._buffered_work = None
        self.bt.set('buffered_work', None)


