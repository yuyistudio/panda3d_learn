# encoding: utf8

__author__ = 'Leon'

from inventory import Inventory
from variable.global_vars import G
from util import log
from collections import namedtuple


ItemData = namedtuple('ItemData', ['item', 'bag'])


class InventoryGUI(object):
    """
    将inventory_system/inventory和gui_system/inventory整合起来的，统一提供对外接口。
    即，将 数据 和 展示 结合起来。
    """
    def __init__(self):
        self._inventory = Inventory(G.res_mgr.get_item_config())
        G.gui_mgr.set_inventory_cb(self._on_item_clicked, self._on_item_hover)

    def _on_item_hover(self, data, idx, is_hover):
        if not data:
            return
        item = data.item
        if is_hover:
            log.debug("item[%s] hovered!", item.get_name())
        else:
            log.debug("item[%s] unhovered!", item.get_name())

    def _on_item_clicked(self, data, idx, button):
        if not data:
            log.debug('cell clicked!')
            return
        item = data.item
        log.debug('item[%s/%s] clicked!', item.get_name(), data.bag)
        item = data.bag.take_item_at(idx)
        data.bag.put_item_at(idx+1, item)
        self.refresh()

    def create_to_inventory(self, name, count, idx=0):
        item = self._inventory.create_item(name, count)
        self._inventory.add_item(item)

    def refresh(self):
        """
        将数据同步到GUI。
        :return:
        """
        fns = [G.gui_mgr.set_item_bar_item, G.gui_mgr.set_bag_item]
        bags = [self._inventory.get('item_bar'), self._inventory.get('bag')]
        for bag_idx in range(len(bags)):
            bag = bags[bag_idx]
            set_item_gui = fns[bag_idx]
            for idx, item in bag.iter_items():
                if not item:
                    set_item_gui(
                        idx,
                        None,
                        None,
                        0,
                    )
                    continue
                item_config = G.res_mgr.get_item_config_by_name(item.get_name())
                assert item_config
                texture = G.res_mgr.get_item_texture(item_config['texture'])
                assert texture
                set_item_gui(
                    idx,
                    texture,
                    ItemData(item=item, bag=bag),
                    item.get_count(),
                )


