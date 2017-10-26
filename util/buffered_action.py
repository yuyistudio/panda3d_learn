# encoding: utf8


class BufferedAction(object):
    def on_update(self, dt):
        pass


class BActionAnim(BufferedAction):
    def __init__(self, target_entity, cb):
        self._target_entity = target_entity
        self._cb_fn = cb

    def on_update(self, dt):
        pass


class BActionFollow(BufferedAction):
    def __init__(self, target_entity, cb):
        self._target_entity = target_entity
        self._cb_fn = cb


class BActionClick(BufferedAction):
    def __init__(self, target_entity, cb):
        self._target_entity = target_entity
        self._cb_fn = cb



