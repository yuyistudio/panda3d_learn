# encoding: utf8

__author__ = 'Leon'

from inventory import Inventory
from inventory_system.common import consts
from variable.global_vars import G
from util import log, keyboard
from collections import namedtuple


ItemData = namedtuple('ItemData', ['item', 'bag'])


class InventoryManager(object):
    """
    将inventory_system/inventory和gui_system/inventory整合起来的，统一提供对外接口。
    即，将 数据 和 展示 结合起来。
    """
    def __init__(self):
        self._inventory = Inventory(G.res_mgr.get_item_config())
        G.gui_mgr.set_inventory_cb(self._on_item_clicked, self._on_item_hover)
        self.refresh_mouse()
        self.refresh_inventory()

    def on_save(self, storage):
        storage.set('inventory_data', self._inventory.on_save())

    def on_load(self, storage):
        data = storage.get('inventory_data')
        if data:
            self._inventory.on_load(data)
            self.refresh_mouse()
            self.refresh_inventory()

    def _on_item_hover(self, data, idx, is_hover):
        assert data, (data, idx, is_hover)
        item = data.item
        if not item:
            return
        mouse = G.gui_mgr.get_mouse_gui()
        if is_hover:
            mouse.set_item_text("item %s" % item.get_name())
        else:
            mouse.set_item_text('')

    def _on_item_clicked(self, data, idx, button):
        assert data, (data, idx, button)
        if button == 'mouse1':
            if keyboard.is_ctrl_down():
                self._inventory.half_to_mouse(data.bag, idx)
            else:
                self._inventory.mouse_click_at_bag(data.bag, idx)
            self.refresh_inventory()
            self.refresh_mouse()

    def refresh_mouse(self):
        item = self._inventory.get_mouse_item()
        mouse = G.gui_mgr.get_mouse_gui()
        if not item:
            mouse.setVisible(False)
            mouse.set_mouse_item_info('')
            return
        texture = self._get_item_texture(item)
        mouse.setItem(texture, item.get_count())
        mouse.set_mouse_item_info("%d" % item.get_count())
        mouse.setVisible(True)

    def add_item(self, item):
        return self._inventory.add_item(item)

    def create_item(self, name, count):
        return self._inventory.create_item(name, count)

    def create_to_inventory(self, name, count):
        """
        添加物品到背包。未完全添加时，返回剩余的物品。
        :param name:
        :param count:
        :return:
        """
        item = self._inventory.create_item(name, count)
        res = self._inventory.add_item(item)
        if res == consts.BAG_PUT_TOTALLY:
            return None
        else:
            return item

    def _get_item_texture(self, item):
        item_config = G.res_mgr.get_item_config_by_name(item.get_name())
        assert item_config
        tex = G.res_mgr.get_item_texture(item_config['texture'])
        if not tex:
            log.error("texture %s not found", item_config['texture'])
        return tex

    def refresh_inventory(self):
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
                        ItemData(item=None, bag=bag),
                        0,
                    )
                    continue
                texture = self._get_item_texture(item)
                assert texture
                set_item_gui(
                    idx,
                    texture,
                    ItemData(item=item, bag=bag),
                    item.get_count(),
                )

