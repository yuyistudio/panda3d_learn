#encoding: utf

from item import Item
from components import *
import consts
import copy
import bag


class EquipmentSlots(object):
    """
    None means empty item.
    """
    def __init__(self, slots):
        """
        :param slots:  eg. ["left_hand", "right_hand", "head"]
        :return:
        """
        self._bag = bag.Bag(len(slots))
        self._name2index = {}
        self._index2name = slots
        for i in range(len(slots)):
            self._name2index[slots[i]] = i

    def __str__(self):
        slots = []
        for i in range(len(self._bag._items)):
            slots.append('[%s:%s]' % (self._index2name[i], self._bag.get_item_at(i)))
        return '\t'.join(slots)

    def on_save(self):
        return self._bag.on_save()

    def on_load(self, data):
        self._bag.on_load(data)

    def get_switched_equipment(self):
        return self._bag.get_switched_item()

    def get_equipment(self, name):
        idx = self._name2index.get(name, -1)
        if idx < 0:
            return None
        return self._bag.get_item_at(idx)

    def take_equipment(self, name):
        idx = self._name2index.get(name, -1)
        if idx < 0:
            return None
        return self._bag.take_item_at(idx)

    def take_equipment_at(self, idx):
        return self._bag.take_item_at(idx)

    def put_equip_at(self, index, item):
        """
        :param index:
        :param item: cannot be None
        :return: macro PUT_*
        """
        return self._bag.put_item_at(index, item)

    def equip(self, equip_item):
        equippable = equip_item.get_component(ItemEquippable)
        if not equippable:
            return consts.BAG_PUT_FAILED
        target_slots = equippable.get_slots()
        if not target_slots:
            return consts.BAG_PUT_FAILED
        for target_slot in target_slots:  # priority.
            idx = self._name2index.get(target_slot, -1)
            if idx < 0:
                continue
            res = self._bag.put_item_at(idx, equip_item)
            if res == consts.PUT_INTO_EMPTY:
                return consts.BAG_PUT_TOTALLY
            elif res == consts.PUT_SWITCH:  # get old weapon with get_switched_equipment()
                return consts.BAG_PUT_TOTALLY
            elif res == consts.PUT_FORBIDDEN:
                return consts.BAG_PUT_FAILED
            else:
                raise RuntimeError("unexpected put-item result %s", res)


import unittest
import logging

class ET(unittest.TestCase):
    items_config = {
        "sword": {
            "equippable": {"slots": ["hand", "head"]},
            "duration": {"duration": 2},
        },
        "hat": {
            "equippable": {"slots": ["head"]},
            "duration": {"duration": 1},
        },
        "helmet": {
            "equippable": {"slots": ["head"]},
            "duration": {"duration": 10},
        },

    }

    def test_duration(self):
        Item.set_items_config(self.items_config)
        sword = Item.create_by_name("sword")
        sword.get_component(ItemDuration).change(-1)
        self.assertEqual(sword.get_component(ItemDuration).is_broken(), False)
        sword.get_component(ItemDuration).change(-1)
        self.assertEqual(sword.get_component(ItemDuration).is_broken(), True)

    def test_equip(self):
        Item.set_items_config(self.items_config)
        equipments = EquipmentSlots(['hand', 'feet', 'head'])
        sword = Item.create_by_name("sword")
        hat = Item.create_by_name("hat")
        helmet = Item.create_by_name("helmet")
        equipments.equip(sword)
        equipments.equip(hat)
        self.assertEqual(equipments.get_equipment("head"), hat)
        self.assertEqual(equipments.get_equipment("hand"), sword)
        equipments.equip(helmet)
        self.assertEqual(equipments.get_equipment("head"), helmet)
        self.assertEqual(equipments.get_switched_equipment(), hat)


if __name__ == '__main__':
    unittest.main()