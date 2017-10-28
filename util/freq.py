# encoding: utf8

__author__ = 'Leon'


class FrequencyControl(object):
    """
    频控模块
    """
    def __init__(self, duration):
        self._duration = duration
        self._timer = 0

    def is_ok(self, dt):
        self._timer += dt
        if self._timer > self._duration:
            self._timer = 0
            return True
        return False

