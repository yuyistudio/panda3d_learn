#encoding: utf8

from entity_system.base_entity import BaseEntity
from components import *
import consts
import components


def register_item_components():
    coms = []
    for name, com in vars(components).iteritems():
        if name.startswith("Item"):
            coms.append(com)
    BaseEntity.register_components(coms)

register_item_components()


class Item(BaseEntity):
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

    def __init__(self, name):
        BaseEntity.__init__(self, name, entity_type=ENTITY_TYPE_ITEM)

    @staticmethod
    def set_items_config(config):
        """
        For ONLY unittest purpose.
        :param config:
        :return:
        """
        BaseEntity.set_item_config(config)

    @staticmethod
    def create_by_name(name, count=1):
        config = BaseEntity._item_config.get(name, BaseEntity.CONFIG_NOT_FOUND_FLAG)
        if config == BaseEntity.CONFIG_NOT_FOUND_FLAG:
            raise RuntimeError("item not found : %s, config `%s`" % (name, BaseEntity._item_config))
        item = Item(name)
        item._post_init()
        if count > 1:
            item.get_stackable().set_count(count)
        return item

    def use_item(self, count):
        """
        :param count:
        :return: 返回剩余的count
        """
        if self._stackable:
            self._stackable.change_count(-count)
            return self._stackable.get_count()
        else:
            return 0

    def destroy(self):
        """
        让该物品消失！
        :return:
        """
        self._destroyed = True

    def get_stackable(self):
        return self._stackable

    def _post_init(self):
        self._stackable = self.get_component(ItemStackable)

    def get_count(self):
        if self._stackable:
            return self._stackable.get_count()
        return 1

    def on_quick_action(self, bag, idx, mouse_item):
        for com in self._components.itervalues():
            com.on_quick_action(bag, idx, mouse_item)

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
            if not isinstance(com1, BaseMergeableComponent):
                continue
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
        """overwrite this method"""
        pass

    def on_put_into_bag(self, bag):
        """overwrite this method"""
        pass


import unittest
class ItemTest(unittest.TestCase):
    items_config = {
        "apple": {
            "stackable": {
                "max_count": 10,
            },
            "perishable": {
                "time": 80,
            },
        },
        "axe": {},
    }
    def test_merge(self):
        BaseEntity.update_config(ItemTest.items_config)
        a1 = Item.create('apple', 3)
        a2 = Item.create("apple", 5)
        a1.get_component(ItemPerishable).set_percentage(.8)
        a2.get_component(ItemPerishable).set_percentage(.1)
        a2.on_merge_with(a1)
        corrent_value = 3. / 8 * 0.8 + 5. / 8 * 0.1
        self.assertAlmostEqual(a2.get_component(ItemPerishable).get_percentage(), corrent_value)


if __name__ == '__main__':
    unittest.main()