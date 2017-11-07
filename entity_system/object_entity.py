# encoding: utf8


__author__ = 'Leon'


from base_entity import BaseEntity
from variable.global_vars import G
from util import log
from base_component import *
from config import *


class ObjectEntity(BaseEntity):
    DEFAULT_POS = Vec3(0, 0, 0)

    def __str__(self):
        return "[ObjectEntity:%s]" % self.get_name()

    def __init__(self, name, overwrite_config=dict()):
        default_config = BaseEntity._object_config.get(name, BaseEntity.CONFIG_NOT_FOUND_FLAG)
        self._transform_com = None
        self._radius = overwrite_config.get('radius', default_config.get('radius', 1))
        BaseEntity.__init__(self, name, overwrite_config, ENTITY_TYPE_OBJECT)

    def is_static(self):
        return True

    def allow_action(self, tool, key_type, mouse_entity):
        """
        详见 docs/user_action.md
        :param tool:
        :param key_type:
        :param mouse_entity:
        :return:
        """
        for com in self._components.itervalues():
            action_type = com.allow_action(tool, key_type, mouse_entity)
            if action_type:
                return action_type
        return False

    def do_action(self, action_info, tool, key_type, mouse_entity):
        for com in self._components.itervalues():
            if com.do_action(action_info, tool, key_type, mouse_entity):
                return True
        return False

    def get_static_models(self):
        models = []
        for com in self._components.itervalues():
            models.extend(com.get_static_models())
        return models

    def set_radius(self, new_radius):
        self._radius = new_radius

    def get_radius(self):
        return self._radius

    def destroy(self, consider_chunk_mgr=True):
        """
        因为GC有延时，所以需要显式destroy物体。
        destroy不会立即生效，以免当前帧出错。应当保证被destroy的物体不会再产生交互。
        :on_removing_chunk: False表示只删除当前entity，此时需要通知chunk_manager进行一些操作。
            True时直接清理自身就可以了
        :return:
        """
        assert not self._destroyed
        self._destroyed = True

        # TODO 实现一种更优雅的方式去destroy物体，比如先保存到一个队列中，过一会儿再删除
        def delayed_destroy(task):
            if consider_chunk_mgr:
                G.game_mgr.chunk_mgr.remove_entity(self)
            for com in self._components.itervalues():
                com.destroy()
            return task.done
        G.taskMgr.doMethodLater(0.01, delayed_destroy, name='destroy')

    def set_transform(self, transform):
        self._transform_com = transform

    def set_pos(self, pos):
        if not self._transform_com:
            return
        return self._transform_com.set_pos(pos)

    def get_pos(self):
        if not self._transform_com:
            return self.DEFAULT_POS
        return self._transform_com.get_pos()


