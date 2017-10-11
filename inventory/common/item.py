#encoding: utf8

import components
from components import *
import consts

name2component_class = {}


def get_component_name(com_type):
    return com_type.__name__[4:].lower()


def register_components(ignore_conflict=False):
    component_names = set()
    for name, component in vars(components).iteritems():
        if not ignore_conflict and name in component_names:
            raise RuntimeError("duplicated component: %s" % name)
        if name.startswith("Item"):
            name2component_class[get_component_name(component)] = component

register_components()


class Item(object):
    _items_config = None
    __CONFIG_NOT_FOUND_FLAG = -1
    @staticmethod
    def set_items_config(items_config):
        """
        :param items_config: mapping from item_name => config
            {
                "stackable": {"max_count": 10},
                "perishable": {"time": 80},
                "edible": {"food": 10},
            }
        :return:
        """
        Item._items_config = items_config

    @staticmethod
    def get_item(self, name, count):
        item = Item.create_by_name("apple")
        item.get_stackable().set_count(count)
        return item

    @staticmethod
    def create_by_name(name, count=1):
        config = Item._items_config.get(name, Item.__CONFIG_NOT_FOUND_FLAG)
        if config == Item.__CONFIG_NOT_FOUND_FLAG:
            raise RuntimeError("item not found : %s, config `%s`" % (name, Item._items_config))
        item = Item(name)
        for com_name, com_config in config.iteritems():
            item.add_component(com_name, com_config)
        item._post_init()
        if count > 1:
            item.get_stackable().set_count(count)
        return item

    def __str__(self):
        stackable = self.get_stackable()
        if stackable:
            res = '%s[%d]' % (self.get_name(), stackable.get_count())
        else:
            res = '%s(1)' % self.get_name()
        perishable = self.get_component(ItemPerishable)
        if perishable:
            res += '(%s)' % perishable.get_percentage()
        else:
            res += '(1.0)'
        return res

    def __init__(self, name, category=None):
        self._name = name
        self._category = category
        self._components = {}

    def get_stackable(self):
        return self._stackable

    def _post_init(self):
        self._stackable = self.get_component(ItemStackable)

    def get_count(self):
        if self._stackable:
            return self._stackable.get_count()
        return 1

    def get_category(self):
        return self._category

    def get_name(self):
        return self._name

    def add_component(self, component_name, component_config):
        component_class = name2component_class[component_name]
        key = component_class
        if key in self._components:
            raise RuntimeError("duplicated component: %s" % key)
        self._components[key] = component_class(component_config)

    def get_component(self, component_type):
        return self._components.get(component_type)

    def on_merge_with(self, item1):
        """
        merge item to self.
        if totally merged, item won't be removed automatically, but its Stackable.get_count() will be zero.
        :param item1:
            must has component Stackable.
            must has the same name with self.
        :return: one of the macros PUT_***
        """
        item2 = self  # merge 1 to 2
        assert item1.get_name() == item2.get_name(), "try to merge different items (%s,%s)" % (item1.get_name(), item2.get_name())
        stack1 = item1.get_component(ItemStackable)
        stack2 = item2.get_component(ItemStackable)
        assert stack1 and stack2, "failed to get Stackable component for merging, (%s,%s)" % (item1.get_name(), item2.get_name())
        remained_count = stack2.get_max_count() - stack2.get_count()
        if remained_count == 0:
            return consts.PUT_MERGE_FAILED
        merge_count = min(stack1.get_count(), remained_count)
        count2 = stack2.get_count()
        stack1.change_count(-merge_count)
        stack2.change_count(merge_count)

        total_count = float(stack2.get_count())
        factor1 = merge_count / total_count
        factor2 = count2 / total_count

        for component_type, com1 in item1._components.iteritems():
            merge_value1 = com1.get_merge_value()
            if merge_value1:
                com2 = item2.get_component(component_type)
                assert(com2)  # since they have the same name
                merge_value2 = com2.get_merge_value()
                # print component_type.__name__, merge_value1, factor1, merge_value2, factor2
                com2.set_merge_value(merge_value1 * factor1 + merge_value2 * factor2)
        if stack1.get_count() == 0:
            return consts.PUT_MERGE_TOTALLY
        else:
            return consts.PUT_MERGE_PARTIALLY

    def on_taken_from_bag(self, bag):
        pass

    def on_put_into_bag(self, bag):
        pass

    def on_save(self):
        data = {}
        for com_type, com in self._components.iteritems():
            key = get_component_name(com_type)
            value = com.on_save()
            assert value != None, "com[%s].on_save() returns None" % key
            data[key] = value
        return data

    def on_load(self, data):
        for com_name, com_data in data.iteritems():
            com_type = name2component_class.get(com_name)
            assert com_type, "unidentified component %s" % com_name
            self.get_component(com_type).on_load(com_data)
        self._post_init()


import unittest
class ItemTest(unittest.TestCase):
    def test_merge(self):
        a1 = Item("apple")
        a2 = Item("apple")
        a1.add_component(ItemStackable(5))
        a1.get_component(ItemStackable).change_count(-2)
        a1.add_component(ItemPerishable(0.8))
        a2.add_component(ItemStackable(10))
        a2.get_component(ItemStackable).change_count(-5)
        a2.add_component(ItemPerishable(0.1))
        a2.on_merge_with(a1)
        corrent_value = 3. / 8 * 0.8 + 5. / 8 * 0.1
        self.assertAlmostEqual(a2.get_component(ItemPerishable).get_merge_value(), corrent_value)


if __name__ == '__main__':
    unittest.main()