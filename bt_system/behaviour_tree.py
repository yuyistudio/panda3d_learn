# encoding: utf8

"""
实现了BehaviourTree
"""

import random

SUCCESS, FAIL, RUNNING, ABORT = 1, 2, 3, 4
VALID_STATUS = [SUCCESS, FAIL, RUNNING, ABORT]
STATUS_STR = ['invalid', 'success', 'fail', 'running', 'abort']
STR_TO_STATUS = {'invalid': 0, 'success': 1, 'fail': 2, 'running': 3, 'abort': 4}

import logging


def log(*args):
    return
    logging.warn(*args)


class INode(object):
    def inner_on_traverse(self):
        pass

    def inner_on_finish(self, is_abort, current_status):
        pass

    def inner_on_child_done(self, is_abort, child_status):
        pass


class ICompositeNode(INode):
    def __init__(self, children):
        self._children = children
        self._index_to_run = 0
        self._abort_child_status = SUCCESS
        self._is_loop = False

    def inner_on_finish(self, is_abort, status):
        self._index_to_run = 0
        if self.parent:
            self.parent.inner_on_child_done(is_abort, status)

    def inner_on_child_done(self, is_abort, last_child_status):
        if is_abort:
            # 孩子被打断了
            self.inner_on_finish(True, ABORT)
        else:
            # 孩子工作做完了
            assert last_child_status != RUNNING
            self._index_to_run += 1
            if self._index_to_run >= len(self._children):
                if not self._is_loop:
                    # 所有孩子都成功返回了
                    self.inner_on_finish(False, SUCCESS)
                    return
                else:
                    # 所有孩子都成功返回了，但是还需要再来一遍
                    self._index_to_run = 0

            # 孩子还没遍历完毕
            if last_child_status == self._abort_child_status:
                # 但是到达了结束状态，所以认为失败了
                self.inner_on_finish(False, last_child_status)
            else:
                # 还没到结束状态
                pass

    def get_child(self):
        assert False

    def inner_on_traverse(self):
        self.get_child().inner_on_traverse()


class UntilSuccess(ICompositeNode):
    def __init__(self, *children):
        ICompositeNode.__init__(self, children)

    def get_child(self):
        return self._children[self._index_to_run]


class UntilFailure(ICompositeNode):
    def __init__(self, *children):
        ICompositeNode.__init__(self, children)
        self._abort_child_status = FAIL

    def get_child(self):
        return self._children[self._index_to_run]


class Sequence(ICompositeNode):
    def __init__(self, *children):
        ICompositeNode.__init__(self, children)
        self._abort_child_status = ABORT

    def get_child(self):
        return self._children[self._index_to_run]


class Loop(ICompositeNode):
    def __init__(self, *children):
        ICompositeNode.__init__(self, children)
        self._abort_child_status = ABORT
        self._is_loop = True

    def get_child(self):
        return self._children[self._index_to_run]


class IActionNode(INode):
    def __init__(self, name):
        INode.__init__(self)
        self._name = name

    def __str__(self):
        return '[%s]' % self._name

    def inner_on_enter(self):
        log("[bt] entering %s", self)
        self.on_enter()

    def inner_on_finish(self, is_abort, status):
        log("[bt] %s %s", 'abort' if is_abort else 'leaving', self)
        if self.parent:
            self.parent.inner_on_child_done(is_abort, status)
        self.on_finish(is_abort, status)

    def inner_on_traverse(self):
        self.bt._set_current_action(self, False)

    def on_init(self):
        """
        重载
        :return:
        """
        pass

    def on_enter(self):
        """
        重载
        :return:
        """
        pass

    def on_action(self):
        """
        重载
        :return:
        """
        assert False  # 子类必须重载该函数

    def on_finish(self, is_abort, status):
        """
        重载
        :param is_abort:
        :param status:
        :return:
        """
        pass


class ActionFn(IActionNode):
    def __init__(self, name, fn):
        IActionNode.__init__(self, name)
        self._fn = fn

    def on_action(self):
        status = self._fn(self.bt)
        assert status in [SUCCESS, FAIL, RUNNING, ABORT], self._fn
        return status


class IDecoratorNode(INode):
    def __init__(self, child):
        self._child = child

    def inner_on_traverse(self):
        self._child.inner_on_traverse()

    def on_enter(self):
        self._child.on_enter()

    def transform_status(self, status):
        assert False

    def inner_on_child_done(self, is_abort, child_status):
        self.parent.inner_on_child_done(is_abort, self.transform_status(child_status))


class Fail(IDecoratorNode):
    def __init__(self, child):
        IDecoratorNode.__init__(self, child)

    def transform_status(self, status):
        return FAIL


class Success(IDecoratorNode):
    def __init__(self, child):
        IDecoratorNode.__init__(self, child)

    def transform_status(self, status):
        return SUCCESS


class Negate(IDecoratorNode):
    def __init__(self, child):
        IDecoratorNode.__init__(self, child)

    def transform_status(self, status):
        if status == SUCCESS:
            return FAIL
        if status == FAIL:
            return SUCCESS
        return status


class BehaviourTree(object):
    SHORT_CUT_UPDATE = 0
    FULL_UPDATE = 1
    NOT_UPDATE = 2

    def __init__(self, refresh_duration, root, default_context={}):
        self._context = default_context
        self._current_node = None
        self.dt = 0
        self._paused = False
        self._root = root
        self._last_status = None
        self._refresh_timer = 0
        self._refresh_duration = refresh_duration
        self._events = {}
        self._waiting_events = {}
        self._paused_seconds = -1
        self._paused_next_status = SUCCESS
        self._last_action = None

        self.c = 0

        # init
        if root:
            root.parent = None
            self._setup_node_relations(root)

    def _set_current_action(self, node, is_abort):
        log('[bt] %s %s => %s', 'set' if not is_abort else 'abort', self._current_node, node)
        if self._current_node == node:
            return
        if self._current_node:
            self._current_node.inner_on_finish(is_abort, self._last_status)
        if node:
            node.on_enter()
        self._current_node = node

    def _get_current(self):
        return self._current_node

    def _setup_node_relations(self, node):
        if isinstance(node, ICompositeNode):
            for child in node._children:
                child.parent = node
                self._setup_node_relations(child)
        elif isinstance(node, IDecoratorNode):
            node._child.parent = node
            self._setup_node_relations(node._child)
        else:
            node.bt = self
            node.on_init()

    def _clear_conditions(self):
        self._paused_seconds = -1
        self._refresh_timer = 0
        self._waiting_events.clear()

    def _print_action(self, action):
        if self._last_action != action:
            log('[bt] %s', action)
            self._last_action = action

    def _check_conditions(self, dt):
        """
        返回True表示不能进行后续Action.
        """
        if self._paused_seconds >= 0:
            self._paused_seconds -= dt
            if self._paused_seconds < 0:
                self._last_status = self._paused_next_status
                if self._paused_next_status != RUNNING:
                    self._set_current_action(None, False)
            else:
                self._print_action('paused for duration')
                return True
        if self._paused:
            self._print_action('paused for good')
            return True
        if self._waiting_events:
            self._print_action('waiting events')
            return True

    def get_current_action(self):
        current = self._get_current()
        return current._name if current else None

    def get(self, key):
        """
        设置BT级别的context
        :param key:
        :return:
        """
        return self._context.get(key)

    def set(self, key, value):
        """
        读取BT级别的context
        :param key:
        :param value:
        :return:
        """
        old_value = self._context.get(key)
        if old_value == value:
            return
        self._context[key] = value
        # 立即处理context变化事件
        if not old_value:
            self._set_current_action(None, True)
            self._clear_conditions()

    def wait_for_seconds(self, seconds, next_status=SUCCESS):
        """
        将当前action挂起
        :param seconds: 挂起的时间
        :param next_status: 挂起结束后action的状态
        :return:
        """
        assert not self._waiting_events  # 不支持同时等待事件和timer
        assert self._paused_seconds < 0  # 只能同时等待1个
        self._paused_seconds = seconds
        if isinstance(next_status, basestring):
            next_status = STR_TO_STATUS[next_status]
        self._paused_next_status = next_status

    def wait_for_event(self, event_name, cb=None):
        """
        Action调用这个函数来暂停执行，并等待事件发生。
        :param event_name:
        :return:
        """
        self._waiting_events[event_name] = cb

    def remove_event(self, event_name):
        """
        移除add_event添加的事件
        :param event_name:
        :return:
        """
        if event_name in self._events:
            del self._events[event_name]
            # 立即处理context变化事件
            self._set_current_action(None, True)
            self._clear_conditions()

    def pop_event(self, name):
        """
        移除并返回add_event添加的事件
        :param name:
        :return:
        """
        if name in self._events:
            ev = self._events[name]
            del self._events[name]
            return True, ev
        return False, None

    def peak_event(self, name):
        """
        返回add_event添加的事件
        :param name:
        :return:
        """
        return self._events.get(name)

    def add_event(self, event_name, event_data=1, immediately=False):
        """
        添加事件
        :param event_name: 事件名称
        :param event_data: 事件的其他参数
        :param immediately: 是否立即响应事件
        :return:
        """
        if event_name in self._waiting_events:
            cb = self._waiting_events[event_name]
            assert cb
            if cb:
                self._last_status = cb(event_name)
                assert self._last_status in VALID_STATUS
                if self._last_status == RUNNING:
                    # 还需要继续执行当前action
                    return
            # event到来导致action结束
            self._clear_conditions()
            self._set_current_action(None, False)
            return

        # 事件不被等待，暂存以便日后处理
        self._events[event_name] = event_data
        if immediately:
            self._set_current_action(None, True)
            self._clear_conditions()

    def on_update(self, dt):
        """
        更新BT
        :param dt: 距离上一次调用on_update的时间间隔
        :return: 更新类型
        """
        self.dt = dt  # Action节点通过BT.dt来访问时间。
        self._refresh_timer += dt

        if self._check_conditions(dt):
            return self.NOT_UPDATE

        update_type = self.SHORT_CUT_UPDATE
        if not self._get_current() \
                or self._refresh_timer > self._refresh_duration:
            self._refresh_timer = 0
            log('[bt] traverse')
            self._root.inner_on_traverse()
            update_type = self.FULL_UPDATE

        log('[bt] ==> %s', self._get_current())
        self._last_status = self._get_current().on_action()
        self._print_action('action')
        if self._last_status != RUNNING:
            # 当前Action已经运行完毕。
            self._set_current_action(None, False)
        return update_type

    def pause(self, paused=True):
        self._paused = paused


import unittest


class EntityTest(unittest.TestCase):
    def test_event(self):
        mm = {
            'c2': 0,
            'c3': 0,
        }
        def run2(bt):
            mm['c2'] += 1
            if mm['c2'] >= 2:
                mm['c2'] = 0
                return SUCCESS
            return RUNNING

        def run3(bt):
            mm['c3'] += 1
            if mm['c3'] >= 3:
                mm['c3'] = 0
                return SUCCESS
            return RUNNING

        def event1(bt):
            def ev_cb(event_name):
                return SUCCESS
            bt.wait_for_event('event1', ev_cb)
            return RUNNING
        bt = BehaviourTree(
            2,
            UntilFailure (
                ActionFn("test1", run2),
                ActionFn("test2", event1),
                Negate(ActionFn("test3", run3)),
                ActionFn("test4", run2),
            )
        )
        bt.on_update(.5)
        self.assertEqual(bt.get_current_action(), 'test1')
        bt.on_update(.5)
        self.assertEqual(bt.get_current_action(), None)

        bt.on_update(.5)
        self.assertEqual(bt.get_current_action(), 'test2')
        # wait for events, in test2
        for i in range(100):
            bt.on_update(.5)
            self.assertEqual(bt.get_current_action(), 'test2')

        bt.add_event('event1')
        self.assertEqual(bt.get_current_action(), None)
        bt.on_update(.5)
        self.assertEqual(bt.get_current_action(), 'test3')

        bt.add_event('event1')  # no effect
        self.assertEqual(bt.get_current_action(), 'test3')
        bt.on_update(.5)
        self.assertEqual(bt.get_current_action(), 'test3')

        bt.on_update(.5)
        self.assertEqual(bt.get_current_action(), None)

        bt.on_update(.5)
        self.assertEqual(bt.get_current_action(), 'test1')

    def test_wait(self):
        mm = {
            'c2': 0,
            'c3': 0,
        }
        def run2(bt):
            mm['c2'] += 1
            if mm['c2'] >= 2:
                mm['c2'] = 0
                return SUCCESS
            return RUNNING

        def run3(bt):
            mm['c3'] += 1
            if mm['c3'] >= 3:
                mm['c3'] = 0
                return SUCCESS
            return RUNNING

        def wait1(bt):
            bt.wait_for_seconds(1.2, SUCCESS)
            return RUNNING

        bt = BehaviourTree(
            2,
            UntilFailure (
                ActionFn("test1", run2),
                ActionFn("wait1", wait1),
                Negate(ActionFn("test2", run3)),
                ActionFn("test3", run2),
            )
        )
        bt.on_update(.5)
        self.assertEqual(bt.get_current_action(), 'test1')
        bt.on_update(.5)
        self.assertEqual(bt.get_current_action(), None)

        bt.on_update(.5)
        self.assertEqual(bt.get_current_action(), 'wait1')

        bt.on_update(.5)
        self.assertEqual(bt.get_current_action(), 'wait1')
        bt.on_update(.5)
        self.assertEqual(bt.get_current_action(), 'wait1')
        bt.on_update(.5)
        self.assertEqual(bt.get_current_action(), 'test2')

        bt.on_update(.5)
        self.assertEqual(bt.get_current_action(), 'test2')
        bt.on_update(.5)
        self.assertEqual(bt.get_current_action(), None)
        bt.on_update(.5)
        self.assertEqual(bt.get_current_action(), 'test1')

if __name__ == '__main__':
    unittest.main()