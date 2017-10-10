#encoding: utf

from item import Item


class Bag(object):
    def __init__(self, cells_count):
        self._items = [None] * self._cells_count

    def get_cell_count(self):
        return len(self._items)

    def get_item_at(self, index):
        """
        get item reference
        """
        return self._items[index]

    def take_item_at(self, index):
        """
        just take away the item
        """
        item = self.get_item_at(index)
        self._items[index] = None
        return item

    def put_item(self, index, item):
        pass # TODO

    def given_item(self, item):
        pass # TODO

    def sort_by_name(self):
        pass # TODO

    def sort_by_category(self):
        pass # TODO

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
            item = Item.create_item_by_name(item_data[0])
            item.on_load(item_data[1])
            self._items[i] = item

class Inventory(object):
    """
    consists of several bags that belong to the hero.
    there bags are identified by names.
    this class also provide convenient method to interact with opened bags(such box or chest on the ground).
    """
    def __init__(self, items_config):
        self._bags = {}

    def add_bag(self, name, cells_count):
        bag = Bag(cells_count)
        self._bags[name] = bag
        return bag

    def get_bag(self, name):
        return self._bags.get(name)

    def on_save(self):
        data = {}
        for bag_name, bag in self._bags.iteritems():
            data[bag_name] = (bag.get_cell_count(), bag.on_save())
        return data

    def on_load(self, data):
        for bag_name, bag_data in data.iteritems():
            self.add_bag(bag_name, bag_data[0]).on_load(bag_data[1])


