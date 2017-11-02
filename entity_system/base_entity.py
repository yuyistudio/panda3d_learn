#encoding: utf8


import base_components
from panda3d.core import Vec3
from base_component import NO_STORAGE_FLAG
from common import user_action
from variable.global_vars import G
from util import log

name2component_class = {}


def get_component_name(com_type):
    return com_type.name


class BaseEntity(object):
    _config = None
    CONFIG_NOT_FOUND_FLAG = -1
    DEFAULT_POS = Vec3(0, 0, 0)

    def __str__(self):
        return "[Entity:%s]" % self.get_name()

    def __init__(self, name, overwrite_config=dict()):
        assert isinstance(name, basestring)
        self._name = name
        default_config = BaseEntity._config.get(self._name, BaseEntity.CONFIG_NOT_FOUND_FLAG)
        if default_config == BaseEntity.CONFIG_NOT_FOUND_FLAG:
            raise RuntimeError("entity not found : %s" % self._name)
        self._category = default_config.get('category') or self._name

        self._destroyed = False
        self._components = {}
        self._updating_componets = []
        self._transform_com = None
        self._radius = overwrite_config.get('radius', default_config.get('radius', 1))
        self._key_handlers = {}  # action对应的组件。例如 left_click 对应到 edible。目的是保证一个action只有一个com进行响应。

        overwrite_com_conf = overwrite_config.get('components', {})
        for com_name, com_config in default_config['components'].iteritems():
            # construct component with default data.
            com = self.add_component(com_name, com_config)
            # load overwrite data.
            com_overwrite = overwrite_com_conf.get(com_name)
            if com_overwrite:
                com.on_load(com_overwrite)

        # call on_start() on each component after all components are ready.
        for com in self._components.itervalues():
            if com.is_update_overwrite():
                self._updating_componets.append(com)
            com.on_start()

    def register_key_handler(self, key_type, component):
        assert key_type not in self._key_handlers
        self._key_handlers[key_type] = component

    def is_static(self):
        return True

    def allow_action(self, tool, key_type, mouse_entity):
        for com in self._components.itervalues():
            action_type = com.allow_action(tool, key_type, mouse_entity)
            if action_type:
                log.debug("allowed %s, com %s", action_type, com)
                return action_type
        return False

    def do_action(self, tool, key_type, mouse_entity):
        for com in self._components.itervalues():
            if com.do_action(tool, key_type, mouse_entity):
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

    def is_destroyed(self):
        return self._destroyed

    def destroy(self, on_removing_chunk=False):
        """
        因为GC有延时，所以需要显式destroy物体。
        destroy不会立即生效，以免当前帧出错。应当保证被destroy的物体不会再产生交互。
        :return:
        """
        assert not self._destroyed
        self._destroyed = True

        # TODO 实现一种更优雅的方式去destroy物体，比如先保存到一个队列中，过一会儿再删除
        def delayed_destroy(task):
            if not on_removing_chunk:
                G.game_mgr.chunk_mgr.remove_entity(self)
            for com in self._components.itervalues():
                com.destroy()
            return task.done
        G.taskMgr.doMethodLater(0.01, delayed_destroy, name='destroy')

    @staticmethod
    def register_components(components, ignore_conflict=False):
        """
        :param components: [ComType1, ComType2, ...]
            ComType must contain static properti `name` as its identifier.
        :param ignore_conflict: confict detection of component identifiers.
        :return: None
        """
        component_keys = set(name2component_class.keys())
        for component_type in components:
            key = get_component_name(component_type)
            if not ignore_conflict and key in component_keys:
                raise RuntimeError("duplicated component: %s, %s" % (key, component_type))
            name2component_class[key] = component_type

    @staticmethod
    def set_config(config):
        """
        :param config: mapping from entity_name => config
            components:
            {
                "stackable": {"max_count": 10},
                "perishable": {"time": 80},
                "edible": {"food": 10},
            }
        :return:
        """
        BaseEntity._config = config
        for k, v in config.iteritems():
            v['name'] = k

    def set_enabled(self, enabled):
        for c in self._components.itervalues():
            c.set_enabled(enabled)

    def on_update(self, dt):
        return any([c.on_update(dt) for c in self._components.itervalues()])

    def get_components_of_type(self, target_type):
        return [com for com_type, com in self._components.iteritems() if isinstance(com, target_type)]

    def get_inspectable_components(self):
        return [com for com in self._components.itervalues() if com.support_inspect()]

    def get_category(self):
        return self._category

    def get_name(self):
        return self._name

    def add_component(self, component_name, component_config):
        component_class = name2component_class.get(component_name)
        if not component_class:
            raise RuntimeError("invalid component name: %s" % component_name)
        key = component_class
        if key in self._components:
            raise RuntimeError("duplicated component: %s" % key)

        com = component_class(component_config)
        import weakref
        com._entity_weak_ref = weakref.ref(self)

        self._components[key] = com
        return com

    def get_component(self, component_type):
        if self._destroyed:
            return None
        return self._components.get(component_type)

    def get_component_names(self):
        if self._destroyed:
            return None
        return '|'.join([str(v) for v in self._components.keys()])

    def on_save(self):
        data = {}
        for com_type, com in self._components.iteritems():
            key = get_component_name(com_type)
            value = com.on_save()
            assert not isinstance(value, type(None)), "unexpected, com[%s].on_save() returns `%s`" % (key, value)
            if value != NO_STORAGE_FLAG:
                data[key] = value
        return {
            'name': self.get_name(),
            'components': data,
        }

    def on_load(self, data):
        for com_name, com_data in data.iteritems():
            com_type = name2component_class.get(com_name)
            assert com_type, "unidentified component %s" % com_name
            self.get_component(com_type).on_load(com_data)

    def set_transform(self, transform):
        self._transform_com = transform

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


def register_object_components():
    coms = []
    for name, com in vars(base_components).iteritems():
        if name.startswith("Obj"):
            coms.append(com)
    BaseEntity.register_components(coms)

register_object_components()


import unittest


class EntityTest(unittest.TestCase):
    def test_entity(self):
        pass


if __name__ == '__main__':
    unittest.main()