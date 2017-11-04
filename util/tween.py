# encoding: utf8

"""
实现Tween功能
"""

__author__ = 'Leon'


import ease_functions as EaseType


class LoopType(object):
    PingPong = 1
    Once = 2
    Loop = 3


class TweenManager(object):
    def __init__(self):
        self.in_update_loop = False
        self.tweens = []
        self.remove_list = []  # 目的是为了在循环遍历tween的时候，不修改 self.tweens
        self.add_list = []  # 目的是为了在循环遍历tween的时候，不修改 self.tweens

    def add_tween(self, tween):
        self.add_list.append(tween)

    def remove_tween(self, tween):
        self.remove_list.append(tween)

    def on_update(self, dt):
        self.in_update_loop = True
        for tween in self.tweens:
            tween.on_update(dt)

        self.in_update_loop = False
        new_tween_list = []
        for tween in self.tweens:
            if tween.is_complete or tween in self.remove_list:
                continue
            new_tween_list.append(tween)
        for tween in self.add_list:
            new_tween_list.append(tween)
        self.tweens = new_tween_list
        self.remove_list = []
        self.add_list = []


class Tween(object):
    def __init__(self, mgr=None, duration=2, from_value=0, to_value=1,
                 tween_after=None, loop_type=LoopType.Loop, ease_type=EaseType.linear,
                 on_update=None, on_complete=None, on_start=None):
        self.mgr = mgr
        self.ease_fn = ease_type
        self.duration = duration
        self.loop_type = loop_type
        self.on_update_cb = on_update
        self.on_complete_cb = on_complete
        self.on_start_cb = on_start
        self.from_value = from_value
        self.to_value = to_value
        self.tween_after = tween_after
        self.tween_after_time_gap = 0

        self.is_complete = False
        self.timer = 0  # 内部计时器

    def get_remained_seconds(self):
        return self.duration - self.timer

    def get_elapsed_seconds(self):
        return self.timer

    def get_percentage(self):
        return self.timer / self.duration

    def _get_ease_value(self):
        v = self.ease_fn(self.get_percentage())
        return self.from_value + (self.to_value - self.from_value) * v

    def cancel(self):
        self.is_complete = True

    def start(self):
        self.mgr.add_tween(self)
        if self.tween_after and self.loop_type != LoopType.Once:
            assert False, "tween-after won't take effect when loop type is not none"
        if self.on_start_cb:
            self.on_start_cb()

    def on_update_without_cb(self, dt):
        self.timer += dt
        if self.timer > self.duration:
            self.is_complete = True
            self.on_complete()
            if self.mgr:
                self.mgr.remove_tween(self)

    def on_update_with_cb(self, dt):
        self.timer += dt
        if self.timer > self.duration:
            self.timer = self.duration
            if not self.is_complete:
                self.is_complete = True
                if self.on_update_cb:
                    self.on_update_cb(self._get_ease_value())
            self.on_complete()
        else:
            self.on_update_cb(self._get_ease_value())

    def on_update(self, dt):
        if self.on_update_cb:
            self.on_update_with_cb(dt)
        else:
            self.on_update_without_cb(dt)

    def on_complete(self):
        self.is_complete = True
        if self.on_complete_cb:
            self.on_complete_cb()
        if self.mgr:
            self.mgr.remove_tween(self)
        if self.loop_type == LoopType.PingPong:
            tmp = self.to_value
            self.to_value = self.from_value
            self.from_value = tmp
        elif self.loop_type == LoopType.Once:
            if self.tween_after and self.mgr:
                self.mgr.add_tween(self.tween_after)
        if self.loop_type != LoopType.Once:
            self.is_complete = False
            self.timer = 0
            if self.on_start_cb:
                self.on_start_cb()


def test():
    def on_up(value):
        print 'up', value
    def on_com():
        print 'complete'
    tm = TweenManager()
    t = Tween(tm, on_complete=on_com, on_update=on_up, duration=2, ease_type=EaseType.easeInOutBounce)
    t.start()
    for i in range(100):
        tm.on_update(0.05)


if __name__ == '__main__':
    test()