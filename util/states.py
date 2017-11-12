# encoding: utf8
__author__ = 'Leon'

"""
控制游戏状态
on_enter
on_update
on_pushed
on_poped
on_leave
"""

from util import log


class BaseState(object):
    """
    基类，用来被继承并实现需要的回调函数。
    """
    def __init__(self, name):
        self._state_name = name

    def __str__(self):
        return "[STATE:%s]" % self._state_name

    def get_name(self):
        return self._state_name

    def on_enter(self, last_name):
        pass

    def on_leave(self, next_name):
        pass

    def on_pushed(self, next_name):
        pass

    def on_popped(self, last_name):
        pass

    def on_update(self, dt):
        pass


class StatesManager(object):
    def __init__(self, first_state_name):
        self.states = {}
        self.state_stack = [first_state_name]
        self._init_done = False

    def _current(self):
        current_state = self.state_stack[-1]
        state = self.states.get(current_state)
        assert state, "state not found for name `%s`" % current_state
        return state

    def add_state(self, state):
        name = state.get_name()
        if name in self.states:
            raise RuntimeError("duplicated state `%s`", name)
        self.states[name] = state

    def push(self, name):
        log.process('state pushed: %s', self.state_stack[-1])
        assert name != self.state_stack[-1]
        self._current().on_pushed(name)
        last_name = self.state_stack[-1]
        self.state_stack.append(name)
        self._current().on_enter(last_name)

    def pop(self):
        assert self.state_stack
        log.process('state popped: %s', self.state_stack[-1])
        self._current().on_leave(self.state_stack[-2])
        last_name = self.state_stack[-1]
        self.state_stack.pop()
        self._current().on_popped(last_name)

    def switch_to(self, name):
        log.process('state switched to: %s', name)
        assert self.state_stack[-1] != name
        self._current().on_leave(name)
        last_name = self.state_stack[-1]
        self.state_stack[-1] = name
        self._current().on_enter(last_name)

    def get_state_by_name(self, name):
        return self.states.get(name)

    def get_current_name(self):
        return self.state_stack[-1]

    def on_update(self, dt):
        if not self._init_done:
            self._init_done = True
            self._current().on_enter("INITIAL_STATE")
        self._current().on_update(dt)


import unittest


class StatesTest(unittest.TestCase):
    def test_states(self):
        sm = StatesManager("_main_menu")
        sm.add_state(BaseState("_main_menu"))
        sm.add_state(BaseState("storage_select"))
        sm.add_state(BaseState("game.game"))
        sm.add_state(BaseState("game.pause"))
        sm.add_state(BaseState("game.map"))
        sm.add_state(BaseState("game.menu"))

        self.assertEqual(sm.get_current_name(), "_main_menu")
        sm.push("storage_select")
        self.assertEqual(sm.get_current_name(), "storage_select")
        sm.switch_to("game.game")
        self.assertEqual(sm.get_current_name(), "game.game")
        sm.push("game.pause")
        self.assertEqual(sm.get_current_name(), "game.pause")
        sm.pop()
        self.assertEqual(sm.get_current_name(), "game.game")
        sm.pop()
        self.assertEqual(sm.get_current_name(), "_main_menu")


if __name__ == '__main__':
    unittest.main()