#encoding: utf8


import base_components
from variable.global_vars import G
from util import log
from base_component import *
from config import *

name2component_class = {}


def get_component_name(com_type):
    return com_type.name

class BaseEntity(object):
    _object_config = None
    _item_config = None
    CONFIG_NOT_FOUND_FLAG = -1
    DEFAULT_POS = Vec3(0, 0, 0)

    def __str__(self):
        return "[Entity:%s]" % self.get_name()

    def __init__(self, name, overwrite_config=dict(), entity_type=ENTITY_TYPE_OBJECT, placement_data=None):
        assert isinstance(name, basestring)
        self._name = name
        self._entity_type = entity_type
        self.placement_data = placement_data  # 各种com在on_start的时候，获取该数据。

        default_config = self._get_config().get(self._name, BaseEntity.CONFIG_NOT_FOUND_FLAG)
        if default_config == BaseEntity.CONFIG_NOT_FOUND_FLAG:
            raise RuntimeError("entity not found : %s" % self._name)
        self._category = default_config.get('category') or self._name

        self._destroyed = False
        self._components = {}
        self._updating_componets = []

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

    def get_placement_data(self):
        """
        在object和item转换的时候，交换数据。
        例如object转Item时，调用 Object.get_placement_data，数据给新生成的 item 来使用。
        :return:
        """
        data = {}
        for com in self._components.itervalues():
            com_data = com.get_placement_data()
            if com_data:
                data[com.name] = com_data
        return data

    def _get_config(self):
        return self._item_config if self._entity_type == ENTITY_TYPE_ITEM else self._object_config

    def is_destroyed(self):
        return self._destroyed

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
    def set_object_config(config):
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
        BaseEntity._object_config = config
        for k, v in config.iteritems():
            v['name'] = k

    @staticmethod
    def set_item_config(config):
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
        BaseEntity._item_config = config
        for k, v in config.iteritems():
            v['name'] = k

    def set_enabled(self, enabled):
        for c in self._components.itervalues():
            c.set_enabled(enabled)

    def on_update(self, dt):
        return any([c.on_update(dt) for c in self._components.itervalues()])

    def get_components_of_type(self, target_type):
        return [com for com_type, com in self._components.iteritems() if isinstance(com, target_type)]

    def get_category(self):
        return self._category

    def get_name(self):
        return self._name

    def add_component(self, component_name, component_config):
        """
        :param component_name:
        :param component_config:
        :return: ComInstance添加成功，None因为entity_type不匹配添加失败.
        """
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
            assert key, key
            assert not isinstance(value, type(None)), "unexpected, com[%s].on_save() returns `%s`" % (key, value)
            if value != NO_STORAGE_FLAG:
                data[key] = value
        return {
            'name': self.get_name(),
            'components': data,
        }

    def on_load(self, data):
        for com_name, com_data in data['components'].iteritems():
            com_type = name2component_class.get(com_name)
            assert com_type, "unidentified component `%s`" % com_name
            self.get_component(com_type).on_load(com_data)

    def need_update(self):
        return len(self._updating_componets) > 0


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