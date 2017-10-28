# encoding: utf8

__author__ = 'Leon'


from behaviour_tree import *
from panda3d.core import Vec3
from entity_system import base_components as coms


Priority = UntilFailure
Pick = UntilSuccess
Decision = ActionFn


class BaseAction(IActionNode):
    def __init__(self, name):
        IActionNode.__init__(self, name)
        self.bt = BehaviourTree(0, None)  # Just for grammatical hints.
        self._entity = None
        self._animator = None
        self._controller = None

    def on_init(self):
        self._entity = self.bt.get('entity')
        assert self._entity, self.bt._context
        self._animator = self._entity.get_component(coms.ObjAnimator)
        self._controller = self._entity.get_component(coms.ObjTransformController)
        assert self._animator and self._controller


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
    def __init__(self, name):
        IActionNode.__init__(self, name)
        self._last_pos = None
        self._linger_timer = 0

    def on_enter(self):
        self._linger_timer = 0
        self._last_pos = Vec3()

    def on_action(self):
        target_pos = self.bt.get('target_pos')
        if not target_pos:
            return FAIL
        self._controller.look_at(target_pos)
        current_pos = self._entity.get_pos()

        # 处理被阻挡的情况
        dist_from_last = (current_pos - self._last_pos).length()
        self._last_pos = current_pos
        if dist_from_last < 0.02:
            self._linger_timer += self.bt.dt
            if self._linger_timer > .5:
                self._linger_timer = 0
                return FAIL
        else:
            self._linger_timer = 0

        # 走动
        dir_vec3 = target_pos - current_pos
        if dir_vec3.length() > 1:
            dir_vec3 = dir_vec3.normalized()
            self._controller.move_towards(dir_vec3[0], dir_vec3[1], self.bt.dt)
            return RUNNING
        else:
            return SUCCESS

    def on_finish(self, is_abort, status):
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
