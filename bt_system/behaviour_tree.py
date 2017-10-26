# encoding: utf8

"""
实现了BehaviourTree
"""

import random

SUCCESS, FAIL, RUNNING, ABORT = 1, 2, 3, 4
VALID_STATUS = [SUCCESS, FAIL, RUNNING, ABORT]
STATUS_STR = ['invalid', 'success', 'fail', 'running', 'abort']

import logging

def log(*args):
    logging.warn(*args)

class INode(object):
    def on_enter(self):
        """
        # Action借点
        on_enter()
        traverse()
        on_finish(abort=False)

        # Composite借点
        traverse()
        get_child()
        handle_child_status(status)
        on_child_done(is_abort, last_child_status)

        :return:
        """
        pass

    def traverse(self):
        pass

    def on_finish(self, is_abort, current_status):
        pass

    def on_child_done(self, is_abort, child_status):
        pass


class ICompositeNode(INode):
    def __init__(self, children):
        self._children = children
        self._index_to_run = 0
        self._abort_child_status = SUCCESS

    def on_finish(self, is_abort, status):
        self._index_to_run = 0
        if self.parent:
            self.parent.on_child_done(is_abort, status)

    def on_child_done(self, is_abort, last_child_status):
        if is_abort:
            # 孩子被打断了
            self.on_finish(True, ABORT)
        else:
            # 孩子工作做完了
            assert last_child_status != RUNNING
            self._index_to_run += 1
            if self._index_to_run >= len(self._children):
                # 所有孩子都成功返回了
                self.on_finish(False, SUCCESS)
            else:
                # 孩子还没遍历完毕
                if last_child_status == self._abort_child_status:
                    # 但是到达了结束状态
                    self.on_finish(False, SUCCESS)
                else:
                    # 还没到结束状态
                    pass

    def get_child(self):
        assert False

    def traverse(self):
        self.get_child().traverse()


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


class IActionNode(INode):
    def __init__(self):
        INode.__init__(self)

    def on_enter(self):
        log("[bt] entering %s", self)

    def on_finish(self, is_abort, status):
        log("[bt] %s %s", 'abort' if is_abort else 'leaving', self)
        if self.parent:
            self.parent.on_child_done(is_abort, status)

    def on_action(self):
        """
        overwrite this method.
        :return:
        """
        assert False

    def traverse(self):
        self.bt.set_current(self, False)


class ActionFn(IActionNode):
    def __init__(self, name, fn):
        IActionNode.__init__(self)
        self._name = name
        self._fn = fn

    def __str__(self):
        return '[%s]' % self._name

    def on_action(self):
        status = self._fn(self.bt)
        assert status in [SUCCESS, FAIL, RUNNING, ABORT], self._fn
        return status


class IDecoratorNode(INode):
    def __init__(self, child):
        self._child = child

    def traverse(self):
        self._child.traverse()

    def on_enter(self):
        self._child.on_enter()

    def transform_status(self, status):
        assert False

    def on_child_done(self, is_abort, child_status):
        self.parent.on_child_done(is_abort, self.transform_status(child_status))


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

    def __init__(self, refresh_duration, root):
        self._current_node = None
        self.dt = 0
        self._paused = False
        self._root = root
        self._context = {}
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
        root.parent = None
        self._setup_node_relations(root)

    def set_current(self, node, is_abort):
        log('[bt] %s %s => %s', 'set' if not is_abort else 'abort', self._current_node, node)
        if self._current_node == node:
            return
        if self._current_node:
            self._current_node.on_finish(is_abort, self._last_status)
        if node:
            node.on_enter()
        self._current_node = node

    def get_current(self):
        return self._current_node

    def get(self, key):
        return self._context.get(key)

    def set(self, key, value):
        self._context[key] = value

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

    def wait_for_seconds(self, seconds, next_status=SUCCESS):
        assert not self._waiting_events  # 不支持同时等待事件和timer
        assert self._paused_seconds < 0  # 只能同时等待1个
        self._paused_seconds = seconds
        self._paused_next_status = next_status

    def wait_for_event(self, event_name, cb=None):
        """
        Action调用这个函数来暂停执行，并等待事件发生。
        :param event_name:
        :return:
        """
        self._waiting_events[event_name] = cb

    def remove_event(self, event_name):
        del self._events[event_name]

    def clear_conditions(self):
        self._paused_seconds = -1
        self._refresh_timer = 0
        self._waiting_events.clear()

    def pop_event(self, name):
        ev = self._events.get(name)
        if ev:
            del self._events[name]
        return ev

    def peak_event(self, name):
        return self._events.get(name)

    def add_event(self, event_name, event_data=1, immediately=False):
        """
        让BT响应事件。记录下来让Node来自己获取。
        :param event_data:
        :param immediately: 是否立即相应事件
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
            self.clear_conditions()
            self.set_current(None, False)
            return

        # 事件不被等待，暂存以便日后处理
        self._events[event_name] = event_data
        if immediately:
            self.set_current(None, True)
            self.clear_conditions()

    def print_action(self, action):
        if self._last_action != action:
            log('[bt] %s', action)
            self._last_action = action

    def check_conditions(self, dt):
        """
        返回True表示不能进行后续Action.
        """
        if self._paused_seconds >= 0:
            self._paused_seconds -= dt
            if self._paused_seconds < 0:
                self._last_status = self._paused_next_status
                if self._paused_next_status != RUNNING:
                    self.set_current(None, False)
            else:
                self.print_action('paused for duration')
                return True
        if self._paused:
            self.print_action('paused for good')
            return True
        if self._waiting_events:
            self.print_action('waiting events')
            return True

    def on_update(self, dt):
        """
        :param dt:
        :return: update type
        """
        self.dt = dt  # Action节点通过BT.dt来访问时间。
        self._refresh_timer += dt

        if self.check_conditions(dt):
            return self.NOT_UPDATE

        if not self.get_current() \
                or self._refresh_timer > self._refresh_duration:
            self._refresh_timer = 0
            log('[bt] traverse')
            self._root.traverse()

        self._last_status = self.get_current().on_action()
        self.print_action('action')
        if self._last_status != RUNNING:
            # 当前Action已经运行完毕。
            self.set_current(None, False)
        return self.FULL_UPDATE

    def pause(self, paused=True):
        self._paused = paused


def test_event():
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
    bt.on_update(.5)
    # test1 done

    bt.on_update(.5)
    # wait for events, in test2
    for i in range(100):
        bt.on_update(.5)

    bt.add_event('event1')
    bt.on_update(.5)
    # running test3

    bt.add_event('event1')  # no effect
    bt.on_update(.5)
    # still running test3

    bt.on_update(.5)
    # leaving test3

    bt.on_update(.5)
    # running test1, because test3 is negated.


def test_wait():
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
    bt.on_update(.5)
    # test1 done

    bt.on_update(.5)
    # action, enter waiting status

    bt.on_update(.5)
    # action, waiting for .5 seconds
    bt.on_update(.5)
    # action, waiting for 1.0 seconds
    bt.on_update(.5)
    # action, waiting done, success, and enter test2

    bt.on_update(.5)
    # action of test2
    bt.on_update(.5)
    # action of test2
    bt.on_update(.5)
    # action of test2 done, entering test1

if __name__ == '__main__':
    test_wait()