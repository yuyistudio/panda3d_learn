#encoding: utf

from item import Item
from components import *
import consts


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


