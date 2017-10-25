#encoding: utf8


import base_components
from panda3d.core import Vec3


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
        self._name = name
        default_config = BaseEntity._config.get(self._name, BaseEntity.CONFIG_NOT_FOUND_FLAG)
        if default_config == BaseEntity.CONFIG_NOT_FOUND_FLAG:
            raise RuntimeError("entity not found : %s" % self._name)
        self._category = default_config.get('category') or self._name

        self._components = {}
        self._updating_componets = []
        self._transform_com = None

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

    def destroy(self):
        """
        因为GC有延时，所以需要显式destroy物体。
        :return:
        """
        for com in self._components.itervalues():
            com.destroy()

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
        return self._components.get(component_type)

    def on_save(self):
        data = {}
        for com_type, com in self._components.iteritems():
            key = get_component_name(com_type)
            value = com.on_save()
            assert value != None, "unexpected, com[%s].on_save() returns None" % key
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

    def on_destroy(self):
        BaseEntity.destroy(self)

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