# encoding: utf8


__author__ = 'Leon'


from base_entity import BaseEntity
import base_components


class ObjectEntity(BaseEntity):
    """
    BaseEntity wrapper for ChunkManager.
    """
    def __init__(self, config):
        BaseEntity.__init__(self, config)

        # setup shortcuts
        self._transform_com = self.get_component(base_components.ObjModel)
        assert self._transform_com

    def on_destroy(self):
        BaseEntity.destroy(self)

    def on_update(self, dt):
        for com in self._updating_componets:
            com.on_update(dt)

    def need_update(self):
        return len(self._updating_componets) > 0

    def set_pos(self, pos):
        if not self._transform_com:
            return
        return self._transform_com.set_pos(pos)

    def get_pos(self):
        if not self._transform_com:
            return self.DEFAULT_POS
        return self._transform_com.get_pos()
