#encoding: utf

from item import Item
from components import *
import consts


class Bag(object):
    def __init__(self, cells_count):
        self._items = [None] * cells_count
        self._switched_item = None

    def __str__(self):
        return '\t'.join([str(item) for item in self._items])

    def take_half(self):
        pass  # TODO

    def create_add_new_item(self, name, count=1):
        item = Item.create_by_name(name)
        stackable = item.get_stackable()
        if stackable:
            stackable.set_count(count)
        else:
            assert count == 1, 'cannot set count attributes on non-stackable item %s' % name
        return self.put_item(item)

    def get_switched_item(self):
        return self._switched_item

    def allow_item(self, item, index):
        """
        overwrite this function to prohibit certain items from being added to this bag.
        :param item:
        :return:
        """
        return True

    def get_cell_count(self):
        return len(self._items)

    def get_item_at(self, index):
        """
        get item reference
        """
        return self._items[index]

    def get_items_count(self):
        count = 0
        for i in self._items:
            if i: count += 1
        return count

    def take_item_at(self, index):
        """
        just take away the item
        """
        item = self.get_item_at(index)
        self._set_item(index, None)
        return item

    def _set_item(self, index, item):
        """
        never set item with self._items[index] = item, but use this function.
        :param index:
        :param item:
        :return:
        """
        self._switched_item = self._items[index]
        if self._switched_item:
            self._switched_item.on_taken_from_bag(self)
        if item:
            item.on_put_into_bag(self)
        self._items[index] = item

    def put_item(self, item):
        """
        put item into this bag.
        :param item:
        :return: one of the macros BAG_PUT_***
        """
        bag_res = consts.BAG_PUT_FAILED
        for i in range(len(self._items)):
            res = self.put_item_at(i, item, allow_switch=False)
            if res == consts.PUT_FORBIDDEN:
                return consts.BAG_PUT_FAILED
            if res == consts.PUT_SWITCH or \
                res == consts.PUT_INTO_EMPTY or \
                res == consts.PUT_MERGE_TOTALLY:
                return consts.BAG_PUT_TOTALLY
            if res == consts.PUT_MERGE_PARTIALLY:
                bag_res = consts.BAG_PUT_PARTIALLY
                continue
            if res == consts.PUT_MERGE_FAILED or \
                res == consts.PUT_SWITCH_FORBIDDEN:
                continue
        return bag_res

    def put_item_at(self, index, item, allow_switch=True):
        """
        put item into the specified cell.
        :param index:
        :param item:
        :return: one of the macros PUT_***
        """
        assert item, 'cannot put empty item `%s`' % item
        if not self.allow_item(item, index):
            return consts.PUT_FORBIDDEN

        ori_item = self.get_item_at(index)
        if not ori_item:
            self._set_item(index, item)
            return consts.PUT_INTO_EMPTY

        if ori_item.get_name() != item.get_name() or not ori_item.get_stackable():
            if allow_switch:
                self._set_item(index, item)
                return consts.PUT_SWITCH  # use get_switched_item() next.
            else:
                return consts.PUT_SWITCH_FORBIDDEN

        return ori_item.on_merge_with(item)

    def cleanup_by_name(self):
        items_count = len(self._items)
        self._items = filter(lambda (item): item, self._items)
        self._items.sort(key=lambda (item): item.get_name())
        self._items.extend([None] * (items_count - len(self._items)))

    def cleanup_by_category(self):
        items_count = len(self._items)
        self._items = filter(lambda (item): item, self._items)
        self._items.sort(key=lambda (item): item.get_category())
        self._items.extend([None] * (items_count - len(self._items)))

    def on_save(self):
        data = []
        for item in self._items:
            item_data =  item.on_save()
            assert item_data != None, 'item[%s].on_save() returns None' % item.get_name()
            data.append((item.get_name(), item_data))
        return data

    def on_load(self, data):
        for i in range(len(data)):
            item_data = data[i]
            item = Item.create_by_name(item_data[0])
            item.on_load(item_data[1])
            self._items[i] = item



import unittest
import logging

class BagTest(unittest.TestCase):
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

    def test_perish_merge(self):
        bag = Bag(5)
        Item.set_items_config(self.items_config)
        c1, p1, c2, p2 = 3, 0.5, 2, 0.8
        c = c1+c2

        apple = Item.create_by_name("apple", c1)
        apple.get_component(ItemPerishable).set_percentage(p1)
        self.assertEqual(bag.put_item_at(1, apple), consts.PUT_INTO_EMPTY)

        apple = Item.create_by_name("apple", c2)
        apple.get_component(ItemPerishable).set_percentage(p2)
        self.assertEqual(bag.put_item_at(1, apple), consts.PUT_MERGE_TOTALLY)

        self.assertAlmostEqual(bag.get_item_at(1).get_component(ItemPerishable).get_percentage(), p1*c1/c+p2*c2/c)
        logging.warn("final bag: %s", str(bag))

    def test_put_item_at(self):
        bag = Bag(5)
        Item.set_items_config(self.items_config)
        apple = Item.create_by_name("apple", 3)
        self.assertEqual(bag.put_item_at(1, apple), consts.PUT_INTO_EMPTY)
        self.assertEqual(bag.get_items_count(), 1)

        logging.warn("1st bag: %s", str(bag))

        apple = Item.create_by_name("apple", 3)
        self.assertEqual(bag.put_item_at(1, apple), consts.PUT_MERGE_PARTIALLY)

        logging.warn("2nd bag: %s", str(bag))

        apple = Item.create_by_name("apple", 3)
        apple.get_component(ItemPerishable).set_percentage(0.1)
        self.assertEqual(bag.put_item_at(1, apple), consts.PUT_MERGE_FAILED)

        logging.warn("3rd bag: %s", str(bag))

        apple = Item.create_by_name("apple", 3)
        self.assertEqual(bag.put_item(apple), consts.BAG_PUT_TOTALLY)

        logging.warn("4th bag: %s", str(bag))

        axe = Item.create_by_name("axe")
        self.assertEqual(bag.put_item_at(1, axe), consts.PUT_SWITCH)

        logging.warn("5th bag: %s", str(bag))

        apple = Item.create_by_name("apple", 5)
        self.assertEqual(bag.put_item(apple), consts.BAG_PUT_TOTALLY)

        logging.warn("6th bag: %s", str(bag))

        self.assertEqual(bag.take_item_at(1), axe)

        logging.warn("7th bag: %s", str(bag))

        apple = Item.create_by_name("apple", 4)
        self.assertEqual(bag.put_item(apple), consts.BAG_PUT_TOTALLY)

        logging.warn("8th bag: %s", str(bag))

        apple = Item.create_by_name("apple", 5)
        self.assertEqual(bag.put_item(apple), consts.BAG_PUT_TOTALLY)
        self.assertEqual(bag.get_item_at(0).get_count(), 5)
        self.assertEqual(bag.get_item_at(1).get_count(), 5)
        self.assertEqual(bag.get_item_at(2).get_count(), 5)
        self.assertEqual(bag.get_item_at(3).get_count(), 2)

        logging.warn("9th bag: %s", str(bag))

if __name__ == '__main__':
    unittest.main()