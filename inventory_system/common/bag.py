#encoding: utf

from item import Item
from components import *
import consts
import copy


class Bag(object):
    """
    None means empty item.
    """
    def __init__(self, cells_count):
        self._items = [None] * cells_count
        self._switched_item = None

    def __str__(self):
        return '\t'.join([str(item) for item in self._items])

    def transform_to_bag(self, index, dest_bag):
        if not dest_bag:
            return consts.BAG_PUT_FAILED
        item = self.get_item_at(index)
        if not item:
            return consts.BAG_PUT_FAILED
        res = dest_bag.add_item(item)
        if res == consts.BAG_PUT_TOTALLY:
            self.take_item_at(index)
        return res

    def transform_all_to_bag(self, dest_bag):
        """
        :param dest_bag:
        :return: macro BAG_PUT_**
        """
        for i in range(len(self._items)):
            self.transform_to_bag(i, dest_bag)

    def take_half(self, index, max_count=99999):
        """
        return item with half count.
            eg. 5 apples, return 2 apples.
                1 apple, return 1 apple.
                None item, return None.
        :param index:
        :return:
        """
        item = self.get_item_at(index)
        if not item:
            return None
        stackable = item.get_stackable()
        if stackable:
            total_count = stackable.get_count()
            if total_count == 1:
                self._set_item(index, None)
                return self.get_switched_item()
            half_count = int(total_count / 2)
            if half_count > max_count:
                half_count = max_count
            stackable.change_count(-half_count)
            new_item = copy.deepcopy(item)
            new_item.get_stackable().set_count(half_count)
            return new_item
        else:
            self._set_item(index, None)
            return item

    def create_add_new_item(self, name, count=1):
        """
        Create an item, and try my best to put it into the bag.
        The remained part that cannot be put into the bag, will be ignored.
        It's mainly for debug purpose.
        :param name:
        :param count:
        :return: return macro BAG_PUT_**
        """
        item = Item.create_by_name(name)
        stackable = item.get_stackable()
        if stackable:
            stackable.set_count(count)
        else:
            assert count == 1, 'cannot set count attributes on non-stackable item %s' % name
        return self.add_item(item)

    def get_switched_item(self):
        """
        meant to be used by code outside this class.
        used to get last item, and clean the record.
        :return:
        """
        res = self._switched_item
        # logging.warn('get switched item: %s' % res)
        self._switched_item = None
        return res

    def set_switched_item(self, item):
        # logging.warn('set switched item: %s' % item)
        assert not self._switched_item, "take care of the switched item please"
        self._switched_item = item

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

    def get_slot_count(self):
        return len(self._items)

    def iter_items(self):
        for idx in range(len(self._items)):
            yield idx, self._items[idx]

    def get_items_count(self):
        count = 0
        for i in self._items:
            if i: count += 1
        return count

    def take_item_at(self, index):
        """
        Take away the item.
        There's no delete() for the bag, just use this function instead.
        """
        self._set_item(index, None)
        return self.get_switched_item()

    def _set_item(self, index, item):
        """
        Never set item with self._items[index] = item, but use this function.
        This function will set the original item at this index as switched-item,
            and you should use get_switched_item() to get this item.
        :param index:
        :param item:
        :return:
        """
        switched_item = self._items[index]
        if switched_item:
            switched_item.on_taken_from_bag(self)
            self.set_switched_item(switched_item)
        if item:
            item.on_put_into_bag(self)
        self._items[index] = item

    def add_item(self, item):
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
        :param item: cannot be None.
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

    def on_update(self, dt):
        for i in range(len(self._items)):
            item = self._items[i]
            if item and item.on_update(dt):
                self._set_item(i, None)

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

    def cleanup_merge_by_name(self):
        # TODO sort by name firstly, then merge items with the same name, and finally sort again.
        raise RuntimeError("not implemented yet!")

    def on_save(self):
        data = []
        for item in self._items:
            if not item:
                data.append(None)
                continue
            item_data = item.on_save()
            assert item_data != None, 'item[%s].on_save() returns None' % item.get_name()
            data.append((item.get_name(), item_data))
        return data

    def on_load(self, data):
        self._items = [None] * len(data)
        for i in range(len(data)):
            item_data = data[i]
            if not item_data:
                continue
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

    def test_sibling_bag(self):
        Item.set_items_config(self.items_config)
        bag = Bag(5)
        apple = Item.create_by_name("apple", 3)
        bag.add_item(apple)
        axe = Item.create_by_name("axe")
        bag.add_item(axe)

        bag2 = Bag(5)
        bag2.create_add_new_item("axe")
        bag2.create_add_new_item("apple")

        self.assertEqual(bag.get_item_at(0), apple)
        self.assertEqual(bag.get_item_at(1), axe)

        bag.transform_all_to_bag(bag2)

        self.assertEqual(bag2.get_item_at(1).get_count(), 4)
        self.assertEqual(bag2.get_item_at(1).get_name(), "apple")
        self.assertEqual(bag2.get_item_at(2), axe)

    def test_save_load(self):
        Item.set_items_config(self.items_config)
        bag = Bag(5)
        bag.create_add_new_item("apple", 3)
        apple = Item.create_by_name("apple", 4)
        apple.get_component(ItemPerishable).set_percentage(0.88)
        bag.put_item_at(1, apple)
        bag.create_add_new_item("apple", 4)
        data = bag.on_save()

        bag = Bag(5)
        bag.on_load(data)
        self.assertEqual(bag.get_item_at(0).get_count(), 5)
        self.assertEqual(bag.get_item_at(1).get_count(), 5)
        self.assertEqual(bag.get_item_at(2).get_count(), 1)
        self.assertAlmostEqual(bag.get_item_at(1).get_component(ItemPerishable).get_percentage(), 0.904)

    def test_cleanup(self):
        Item.set_items_config(self.items_config)
        bag = Bag(5)
        bag.create_add_new_item("apple", 4)
        bag.create_add_new_item("apple", 3)
        bag.create_add_new_item("apple", 4)
        self.assertEqual(bag.get_item_at(0).get_count(), 5)
        self.assertEqual(bag.get_item_at(1).get_count(), 5)
        self.assertEqual(bag.get_item_at(2).get_count(), 1)
        bag.create_add_new_item("axe")
        self.assertEqual(bag.put_item_at(4, Item.create_by_name("apple", 3)), consts.PUT_INTO_EMPTY)
        bag.take_item_at(0)
        bag.cleanup_by_name()

    def test_take_half(self):
        Item.set_items_config(self.items_config)
        bag = Bag(5)
        apple = Item.create_by_name("apple", 5)
        apple.get_component(ItemPerishable).set_percentage(0.88)
        self.assertEqual(bag.put_item_at(1, apple), consts.PUT_INTO_EMPTY)
        half_item = bag.take_half(1)
        self.assertEqual(half_item.get_count(), 2)
        half_item.get_component(ItemPerishable).set_percentage(0.77)
        self.assertEqual(bag.get_item_at(1).get_count(), 3)
        self.assertAlmostEqual(bag.get_item_at(1).get_component(ItemPerishable).get_percentage(), 0.88)

    def test_perish_merge(self):
        # TEST1
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


        # TEST 2
        bag = Bag(5)
        Item.set_items_config(self.items_config)

        c1, p1, c2, p2 = 3, 0.5, 3, 0.8
        c = c1 + 2

        apple = Item.create_by_name("apple", c1)
        apple.get_component(ItemPerishable).set_percentage(p1)
        self.assertEqual(bag.put_item_at(1, apple), consts.PUT_INTO_EMPTY)

        apple = Item.create_by_name("apple", c2)
        apple.get_component(ItemPerishable).set_percentage(p2)
        self.assertEqual(bag.put_item_at(1, apple), consts.PUT_MERGE_PARTIALLY)

        self.assertAlmostEqual(bag.get_item_at(1).get_component(ItemPerishable).get_percentage(),
                               p1 * c1 / c + p2 * 2 / c)

    def test_put_item_at(self):
        bag = Bag(5)
        Item.set_items_config(self.items_config)
        apple = Item.create_by_name("apple", 3)
        self.assertEqual(bag.put_item_at(1, apple), consts.PUT_INTO_EMPTY)
        self.assertEqual(bag.get_items_count(), 1)

        apple = Item.create_by_name("apple", 3)
        self.assertEqual(bag.put_item_at(1, apple), consts.PUT_MERGE_PARTIALLY)

        apple = Item.create_by_name("apple", 3)
        apple.get_component(ItemPerishable).set_percentage(0.1)
        self.assertEqual(bag.put_item_at(1, apple), consts.PUT_MERGE_FAILED)

        apple = Item.create_by_name("apple", 3)
        self.assertEqual(bag.add_item(apple), consts.BAG_PUT_TOTALLY)

        axe = Item.create_by_name("axe")
        self.assertEqual(bag.put_item_at(1, axe), consts.PUT_SWITCH)
        bag.get_switched_item()  # must call this after a switch action.

        apple = Item.create_by_name("apple", 5)
        self.assertEqual(bag.add_item(apple), consts.BAG_PUT_TOTALLY)

        self.assertEqual(bag.take_item_at(1), axe)

        apple = Item.create_by_name("apple", 4)
        self.assertEqual(bag.add_item(apple), consts.BAG_PUT_TOTALLY)

        apple = Item.create_by_name("apple", 5)
        self.assertEqual(bag.add_item(apple), consts.BAG_PUT_TOTALLY)
        self.assertEqual(bag.get_item_at(0).get_count(), 5)
        self.assertEqual(bag.get_item_at(1).get_count(), 5)
        self.assertEqual(bag.get_item_at(2).get_count(), 5)
        self.assertEqual(bag.get_item_at(3).get_count(), 2)

    def test_on_update(self):
        bag = Bag(5)
        Item.set_items_config(self.items_config)
        apple = Item.create_by_name("apple", 3)
        apple.get_component(ItemPerishable).set_value(3)
        self.assertEqual(bag.put_item_at(1, apple), consts.PUT_INTO_EMPTY)
        self.assertEqual(bag.get_item_at(1), apple)
        bag.on_update(2)
        self.assertEqual(bag.get_item_at(1), apple)
        bag.on_update(2)
        self.assertEqual(bag.get_item_at(1), None)

if __name__ == '__main__':
    unittest.main()