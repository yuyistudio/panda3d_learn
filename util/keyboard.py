# encoding: utf8

from panda3d.core import *
from variable.global_vars import G
from util import log


forward_button = KeyboardButton.ascii_key('w')
backward_button = KeyboardButton.ascii_key('s')
left_button = KeyboardButton.ascii_key('a')
right_button = KeyboardButton.ascii_key('d')


def get_direction():
    dx, dy = 0, 0
    is_button_down = G.mouseWatcherNode.is_button_down
    if is_button_down(left_button):
        dx = -1
    elif is_button_down(right_button):
        dx = 1

    if is_button_down(forward_button):
        dy = 1
    elif is_button_down(backward_button):
        dy = -1
    return dx, dy


def is_shift_down():
    return G.mouseWatcherNode.is_button_down(KeyboardButton.shift())


def is_ctrl_down():
    return G.mouseWatcherNode.is_button_down(KeyboardButton.control())


class KeyStatus(object):
    def __init__(self, key, on_click_cb, on_hold_cb, on_hold_done, click_max_duration=0.12):
        self._click_max_duration = click_max_duration
        self._is_down = False
        self._key_timer = 0
        self._on_click = on_click_cb
        self._on_hold_done = on_hold_done
        self._on_hold = on_hold_cb
        self._key = key
        G.accept(key, self._mouse_click_event, ['down'])
        G.accept('%s-up' % key, self._mouse_click_event, ['up'])

    def on_update(self, dt):
        if self._is_down:
            self._key_timer += dt
            if self._key_timer > self._click_max_duration:
                if self._on_hold:
                    self._on_hold()

    def _mouse_click_event(self, status):
        if self._key == 'space':
            log.debug("space event: %s", status)
        if status == 'up':
            if self._key_timer <= self._click_max_duration:
                # click事件
                if self._on_click:
                    self._on_click()
            else:
                # hold事件结束
                if self._on_hold_done:
                    self._on_hold_done()
        self._key_timer = 0
        self._is_down = status == 'down'
