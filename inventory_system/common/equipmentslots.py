#encoding: utf8

from item import Item
from components import *
import consts
import copy
from util import log
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
        equip_item = self._bag.take_item_at(idx)
        if equip_item:
            equippable = equip_item.get_component(ItemEquippable)
            equippable.on_unequipped(self._index2name[idx])
        return equip_item

    def put_equipment_with_check(self, index, equip_item):
        """
        返回是否成功。成功时可能要处理switched item！
        :param index:
        :param equip_item:
        :return:
        """
        old_equipment = self._bag.get_item_at(index)
        log.debug("bag %s", self._bag._items)
        slot_type = self._index2name[index]
        equippable = equip_item.get_component(ItemEquippable)
        if not equippable:
            return False
        target_slots = equippable.get_slots()
        if slot_type in target_slots:
            self._put_equip_at(index, equip_item)
            log.debug("!!! %s, bag %s", old_equipment, self._bag._items)
            if old_equipment:
                old_equipment.get_component(ItemEquippable).on_unequipped(slot_type)
            equippable.on_equipped(slot_type)
            return True
        return False

    def _put_equip_at(self, index, item):
        """
        不进行装备类型检查。
        :param index:
        :param item: cannot be None
        :return: macro PUT_*
        """
        return self._bag.put_item_at(index, item)

    def _equip(self, equip_item):
        """
        装备物品到匹配的一栏。可能会返回装备后的物品。
        :param equip_item:
        :return:
        """
        equippable = equip_item.get_component(ItemEquippable)
        if not equippable:
            return consts.BAG_PUT_FAILED
        target_slots = equippable.get_slots()
        if not target_slots:
            return consts.BAG_PUT_FAILED
        for target_slot in target_slots:  # priority.
            idx = self._name2index.get(target_slot, -1)
            if idx < 0:
                log.error('unexpected equipment slot `%s`', target_slot)
                continue
            res = self._bag.put_item_at(idx, equip_item)
            if res == consts.PUT_INTO_EMPTY:
                return consts.BAG_PUT_TOTALLY, target_slot
            elif res == consts.PUT_SWITCH:  # get old weapon with get_switched_equipment()
                return consts.BAG_PUT_TOTALLY, target_slot
            elif res == consts.PUT_FORBIDDEN:
                return consts.BAG_PUT_FAILED, None
            else:
                raise RuntimeError("unexpected put-item result %s", res)
        return consts.BAG_PUT_FAILED, None

    def quick_equip(self, bag, index):
        equip = bag.get_item_at(index)
        assert equip, (bag, index)
        res, slot_type = self._equip(equip)
        if res == consts.BAG_PUT_TOTALLY:
            # 成功了
            bag.remove_item_at(index)

            switched_equip = self.get_switched_equipment()
            if switched_equip:
                switched_equip.get_component(ItemEquippable).on_unequipped(slot_type)
                bag.put_item_at(index, switched_equip)

            equip.get_component(ItemEquippable).on_equipped(slot_type)
            return True
        assert not self.get_switched_equipment()
        return False

    def iter_items(self):
        for idx, item in self._bag.iter_items():
            yield idx, item

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
        equipments._equip(sword)
        equipments._equip(hat)
        self.assertEqual(equipments.get_equipment("head"), hat)
        self.assertEqual(equipments.get_equipment("hand"), sword)
        equipments._equip(helmet)
        self.assertEqual(equipments.get_equipment("head"), helmet)
        self.assertEqual(equipments.get_switched_equipment(), hat)


if __name__ == '__main__':
    unittest.main()