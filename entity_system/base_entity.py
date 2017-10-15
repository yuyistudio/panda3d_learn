#encoding: utf8


name2component_class = {}


def get_component_name(com_type):
    return com_type.name


class BaseEntity(object):
    _config = None
    CONFIG_NOT_FOUND_FLAG = -1

    def __str__(self):
        return self.get_name()

    def __init__(self, name, category=None):
        self._name = name
        self._category = category or name
        self._components = {}

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
            {
                "stackable": {"max_count": 10},
                "perishable": {"time": 80},
                "edible": {"food": 10},
            }
        :return:
        """
        BaseEntity._config = config

    def on_update(self, dt):
        return any([c.on_update(dt) for c in self._components.itervalues()])

    @staticmethod
    def create_by_name(name):
        config = BaseEntity._config.get(name, BaseEntity.CONFIG_NOT_FOUND_FLAG)
        if config == BaseEntity.CONFIG_NOT_FOUND_FLAG:
            raise RuntimeError("entity not found : %s, config `%s`" % (name, BaseEntity._config))
        entity = BaseEntity(name)
        for com_name, com_config in config.iteritems():
            entity.add_component(com_name, com_config)
        return entity

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
        self._components[key] = component_class(component_config)

    def get_component(self, component_type):
        return self._components.get(component_type)

    def on_save(self):
        data = {}
        for com_type, com in self._components.iteritems():
            key = get_component_name(com_type)
            value = com.on_save()
            assert value != None, "unexpected, com[%s].on_save() returns None" % key
            data[key] = value
        return data

    def on_load(self, data):
        for com_name, com_data in data.iteritems():
            com_type = name2component_class.get(com_name)
            assert com_type, "unidentified component %s" % com_name
            self.get_component(com_type).on_load(com_data)


import unittest


class EntityTest(unittest.TestCase):
    def test_entity(self):
        pass


if __name__ == '__main__':
    unittest.main()