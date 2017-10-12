#encoding: utf8

from common.item import Item
from common.bag import Bag
from common.equipmentslots import EquipmentSlots
from common import consts

EQUIP_SLOT_HEAD = "head"
EQUIP_SLOT_LEFT_HAND = "left_hand"
EQUIP_SLOT_RIGHT_HAND = "right_hand"
EQUIP_SLOT_BODY = "body"
EQUIP_SLOT_FEET = "feet"


class Inventory(object):
    """
    Consists of several bags that are carried on by the hero.
    There bags are identified by names.
    This class also provide convenient method to interact with opened bags(such box or chest on the ground),
        but these box doesn't belong to this inventory.

    All actions with inventory, should perform with Inventory.instance.
    """
    instance = None
    def __init__(self, items_config):
        assert not Inventory.instance, "duplicated inventory"
        Inventory.instance = self

        # init global resources
        Item.set_items_config(items_config)

        # initial state
        self._bag_enabled = False

        # create bags
        self._item_bar = Bag(17)
        self._equipment_slots = EquipmentSlots([EQUIP_SLOT_BODY, EQUIP_SLOT_LEFT_HAND, EQUIP_SLOT_RIGHT_HAND, EQUIP_SLOT_BODY, EQUIP_SLOT_FEET])
        self._bag = Bag(10)
        self._bags = {
            "item_bar": self._item_bar,
            "equipment_slots": self._equipment_slots,
            "bag": self._bag,
        }

    def __str__(self):
        lst = []
        for k, v in self._bags.iteritems():
            lst.append("%s\t%s" % (k, v))
        return '\n'.join(lst)

    def get(self, name):
        """
        Get a specific bag.
        :param name:
        :return:
        """
        bag = self._bags.get(name)
        assert bag, "bag not found: %s" % name
        return bag

    def add_item(self, item):
        """
        Give an item to inventory, add it to the item-bar or add it to the bag.
        :param item:
        :return: one macro of BAG_PUT_**
        """
        res = self._item_bar.add_item(item)
        if res == consts.BAG_PUT_TOTALLY:
            return consts.BAG_PUT_TOTALLY
        if not self._bag_enabled:
            return res
        return self._bag.add_item(item)

    def create_item(self, name, count=1):
        return Item.create_by_name(name, count)

    def on_save(self):
        data = {
            "item_bar": self._item_bar.on_save(),
            "equipment_slots": self._equipment_slots.on_save(),
            "bag": self._bag.on_save(),
            "bag_enabled": self._bag_enabled,
        }
        return data

    def on_load(self, data):
        self._item_bar.on_load(data['item_bar'])
        self._equipment_slots.on_load(data['equipment_slots'])
        self._bag.on_load(data['bag'])
        self._bag_enabled = data['_bag_enabled']

    def open_box(self, box):
        assert not self._opened_box, "cannot open two boxes at the same time"
        self._opened_box = box

    def close_box(self):
        self._opened_box = None

    def _transform(self, src_bag, index, dest_bag):
        # TODO transform clicked to another bag.
        pass


import unittest
import logging
class InventoryTest(unittest.TestCase):
    items_config = {
        "apple": {
            "stackable": {
                "max_count": 5,
            },
            "perishable": {
                "time": 80,
            },
        },
        "axe": {},
    }
    def test_storage(self):
        inv = Inventory(self.items_config)
        inv.add_item(inv.create_item("apple", 4))
        logging.warn(inv)


if __name__ == '__main__':
    unittest.main()
