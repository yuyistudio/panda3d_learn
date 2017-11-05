#encoding: utf8

from common.item import Item
from common.bag import Bag
from common.equipmentslots import EquipmentSlots
from common import consts
from components import *

EQUIP_SLOT_HEAD = "head"
EQUIP_SLOT_LEFT_HAND = "left_hand"
EQUIP_SLOT_RIGHT_HAND = "right_hand"
EQUIP_SLOT_BODY = "body"
EQUIP_SLOT_FEET = "feet"
EQUIP_SLOT_BAG = "bag"


class Inventory(object):
    """
    Consists of several bags that are carried on by the hero.
    There bags are identified by names.
    This class also provide convenient method to interact with opened bags(such box or chest on the ground),
        but these box doesn't belong to this _inventory_data.

    All actions with _inventory_data, should perform with Inventory.instance.
    """
    instance = None
    _mouse_item = None

    def __init__(self, items_config):
        """
        :param items_config:
        :return:
        """
        Inventory.instance = self

        # init_global_vars global resources
        Item.set_items_config(items_config)

        # initial state
        self._bag_enabled = True

        # create bags
        self._item_bar = Bag(13)
        self._equipment_slots = EquipmentSlots(
            [EQUIP_SLOT_HEAD,
             EQUIP_SLOT_LEFT_HAND, EQUIP_SLOT_RIGHT_HAND,
             EQUIP_SLOT_BODY,
             EQUIP_SLOT_FEET,
             EQUIP_SLOT_BAG])
        self._bag = Bag(10)
        self._bags = {
            "item_bar": self._item_bar,
            "equipment_slots": self._equipment_slots,
            "bag": self._bag,
        }

    def get_action_tool(self):
        return self._equipment_slots.get_equipment("right_hand")

    def __str__(self):
        lst = ["_mouse\t%s" % Inventory._mouse_item]
        for k, v in self._bags.iteritems():
            lst.append("%s\t%s" % (k, v))
        return '\n'.join(lst)

    def get_equipment_slots(self):
        """
        :return: instance of EquipmentSlots()
        """
        return self._equipment_slots

    def get_bag(self):
        """
        :return: instance of Bag()
        """
        if self._bag_enabled:
            return self._bag
        return None

    def get_item_bar(self):
        """
        :return: instance of Bag()
        """
        return self._item_bar

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
        Give an item to _inventory_data, add it to the item-bar or add it to the bag.
        :param item:
        :return: one macro of BAG_PUT_**
        """
        res = self._item_bar.add_item(item)
        if res == consts.BAG_PUT_TOTALLY:
            return consts.BAG_PUT_TOTALLY
        if not self._bag_enabled:
            return res
        return self._bag.add_item(item)

    @staticmethod
    def create_item(name, count=1):
        return Item.create_by_name(name, count)

    def on_save(self):
        data = {
            "item_bar": self._item_bar.on_save(),
            "equipment_slots": self._equipment_slots.on_save(),
            "bag": self._bag.on_save(),
            "bag_enabled": self._bag_enabled,
        }
        if Inventory._mouse_item:
            data["mouse_item"] = (Inventory._mouse_item.get_name(), Inventory._mouse_item.on_save())
        else:
            data["mouse_item"] = None
        return data

    def on_load(self, data):
        self._item_bar.on_load(data['item_bar'])
        self._equipment_slots.on_load(data['equipment_slots'])
        self._bag.on_load(data['bag'])
        self._bag_enabled = data['bag_enabled']
        mouse_item_data = data['mouse_item']
        if mouse_item_data:
            Inventory._mouse_item = Inventory.create_item(mouse_item_data[0])
            Inventory._mouse_item.on_load(mouse_item_data[1])

    def open_box(self, box):
        assert not self._opened_box, "cannot open two boxes at the same time"
        self._opened_box = box

    def close_box(self):
        self._opened_box = None

    def take_all_from_box(self):
        assert self._opened_box
        self._opened_box.transform_all_to_bag(self._item_bar)
        if self._bag_enabled:
            self._opened_box.transform_all_to_bag(self._bag)

    @staticmethod
    def get_mouse_item():
        return Inventory._mouse_item

    @staticmethod
    def set_mouse_item(item):
        Inventory._mouse_item = item

    def mouse_click_at_equipment(self, index):
        if Inventory._mouse_item:
            if self._equipment_slots.put_equipment_with_check(index, Inventory._mouse_item):
                Inventory.set_mouse_item(self._equipment_slots.get_switched_equipment())
                return True
            else:
                return False
        else:
            equipment = self._equipment_slots.take_equipment_at(index)
            if equipment:
                Inventory.set_mouse_item(equipment)
                return True
            return False

    def quick_equip(self, bag, index):
        return self._equipment_slots.quick_equip(bag, index)

    @staticmethod
    def mouse_click_at_bag(bag, index):
        """
        Put _mouse item into item-bar or backpack.
        :param bag:
        :param index:
        :return:
        """
        assert bag
        if Inventory._mouse_item:
            res = bag.put_item_at(index, Inventory._mouse_item)
            if res == consts.PUT_FORBIDDEN\
                    or res == consts.PUT_MERGE_FAILED\
                    or res == consts.PUT_SWITCH_FORBIDDEN:
                return
            elif res == consts.PUT_INTO_EMPTY\
                    or res == consts.PUT_MERGE_TOTALLY:
                Inventory._mouse_item = None
            elif res == consts.PUT_SWITCH:
                Inventory._mouse_item = bag.get_switched_item()
            elif res == consts.PUT_MERGE_PARTIALLY:
                pass
        else:
            # No mosue item.
            Inventory._mouse_item = bag.take_item_at(index)

    @staticmethod
    def half_to_mouse(bag, index):
        """
        Take half of the item clicked.
        :return: True if there's changes, else False.
        """
        assert bag
        clicked_item = bag.get_item_at(index)
        if not clicked_item:
            return False
        if not Inventory._mouse_item:
            Inventory._mouse_item = bag.take_half(index)
            return True
        if not Inventory._mouse_item.get_stackable() or Inventory._mouse_item.get_name() != clicked_item.get_name():
            return False
        remained = Inventory._mouse_item.get_stackable().get_remained_capacity()
        half_item = bag.take_half(index, remained)
        if not half_item:
            return False
        res = Inventory._mouse_item.on_merge_with(half_item)
        assert res == consts.PUT_MERGE_TOTALLY
        return True


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
        "axe": {
            "equippable": {
                "slots": ["right_hand"],
            },
            "duration": {},
        },
    }

    def test_storage(self):
        inv = Inventory(self.items_config)
        inv.add_item(inv.create_item("apple", 4))
        axe = Inventory.create_item("axe")
        inv.get_equipment_slots()._equip(axe)
        data = inv.on_save()

        Inventory.instance = None
        inv = Inventory(self.items_config)
        inv.on_load(data)
        self.assertNotEqual(inv.get_equipment_slots().get_equipment("right_hand"), None)
        self.assertEqual(inv.get_item_bar().get_item_at(0).get_name(), "apple")

    def test_mouse_item(self):
        inv = Inventory(self.items_config)
        inv.add_item(inv.create_item("apple", 4))
        axe = Inventory.create_item("axe")
        inv.add_item(axe)
        self.assertEqual(inv.get_item_bar().get_item_at(1), axe)
        inv.mouse_click_at_bag(inv.get_item_bar(), 0)
        self.assertEqual(inv.get_mouse_item().get_name(), "apple")
        inv.mouse_click_at_bag(inv.get_item_bar(), 1)
        self.assertEqual(inv.get_mouse_item().get_name(), "axe")
        inv.mouse_click_at_bag(inv.get_item_bar(), 1)
        self.assertEqual(inv.get_mouse_item().get_name(), "apple")
        inv.mouse_click_at_bag(inv.get_item_bar(), 2)
        self.assertEqual(inv.get_mouse_item(), None)
        inv.half_to_mouse(inv.get_item_bar(), 2)
        self.assertEqual(inv.get_mouse_item().get_name(), "apple")
        self.assertEqual(inv.get_mouse_item().get_count(), 2)
        remained = inv.get_item_bar().get_item_at(2)
        self.assertEqual(remained.get_name(), "apple")
        self.assertEqual(remained.get_count(), 2)


if __name__ == '__main__':
    unittest.main()
