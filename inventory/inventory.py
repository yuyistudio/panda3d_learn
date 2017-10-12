#encoding: utf8

from inventory.common.item import Item
from inventory.common.components import *
import inventory.common.consts


class Inventory(object):
    """
    Consists of several bags that are carried on by the hero.
    There bags are identified by names.
    This class also provide convenient method to interact with opened bags(such box or chest on the ground),
        but these box doesn't belong to this inventory.
    """
    def __init__(self, items_config):
        self._bags = {}

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


