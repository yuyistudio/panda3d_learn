# encoding: utf8

__author__ = 'Leon'

from inventory import Inventory
from inventory_system.common import consts
from variable.global_vars import G
from util import log, keyboard
from collections import namedtuple
from inventory_system.common.components import ItemEquippable, ItemPlaceable


ItemData = namedtuple('ItemData', ['item', 'bag', 'is_equipment'])


class InventoryManager(object):
    """
    将inventory_system/inventory和gui_system/inventory整合起来的，统一提供对外接口。
    即，将 数据 和 展示 结合起来。
    """
    def __init__(self):
        self._inventory_data = Inventory(G.res_mgr.get_item_config())
        Inventory.on_mouse_changed = self._on_mouse_changed
        G.gui_mgr.set_inventory_cb(self._on_item_clicked, self._on_item_hover)
        self.refresh_mouse()
        self.refresh_inventory()

    def _on_mouse_changed(self, old_item, new_item):
        if new_item:
            placeable = new_item.get_component(ItemPlaceable)
            if placeable:
                model_path, shape, scale = placeable.get_placement_config()
                G.operation.placement_mgr.enable(model_path, scale, shape=shape)
                return
        G.operation.placement_mgr.disable()


    def quick_equip(self, bag, idx):
        res = self._inventory_data.quick_equip(bag, idx)
        if res:
            self.refresh_inventory()
        return res

    def get_action_tool(self):
        return self._inventory_data.get_action_tool()

    def take_mouse_item(self):
        item = self._inventory_data.get_mouse_item()
        self._inventory_data.set_mouse_item(None)
        return item

    def get_mouse_item(self):
        return self._inventory_data.get_mouse_item()

    def on_save(self, storage):
        storage.set('inventory_data', self._inventory_data.on_save())

    def on_load(self, storage):
        data = storage.get('inventory_data')
        if data:
            self._inventory_data.on_load(data)
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
        if data.is_equipment:
            # 装备栏
            if button == 'mouse1':
                # 装备鼠标物品
                old_mouse_item = self.get_mouse_item()
                if self._inventory_data.mouse_click_at_equipment(idx):
                    current_mouse_item = self.get_mouse_item()
                    assert old_mouse_item != current_mouse_item
                    self.refresh_inventory()
                    self.refresh_mouse()
            log.debug("equipment clicked!")
            return
        else:
            # 普通物品栏
            if button == 'mouse1':
                if keyboard.is_ctrl_down():
                    # 分堆一半到鼠标
                    self._inventory_data.half_to_mouse(data.bag, idx)
                else:
                    # 直接点击物品
                    self._inventory_data.mouse_click_at_bag(data.bag, idx)
            elif button == 'mouse3':
                # 快捷操作
                if data.item:
                    data.item.on_quick_action(data.bag, idx, self.get_mouse_item())
                    if data.item.is_destroyed():
                        data.bag.remove_item_at(idx)
            self.refresh_inventory()
            self.refresh_mouse()

    def refresh_mouse(self):
        """
        将数据同步到GUI。
        :return:
        """
        item = self._inventory_data.get_mouse_item()
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
        return self._inventory_data.add_item(item)

    def create_item(self, name, count):
        return self._inventory_data.create_item(name, count)

    def create_to_inventory(self, name, count):
        """
        添加物品到背包。未完全添加时，返回剩余的物品。
        :param name:
        :param count:
        :return:
        """
        item = self._inventory_data.create_item(name, count)
        res = self._inventory_data.add_item(item)
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
        fns = [G.gui_mgr.set_item_bar_item,
               G.gui_mgr.set_bag_item,
               G.gui_mgr.set_equipments_item]
        bags = [self._inventory_data.get('item_bar'),
                self._inventory_data.get('bag'),
                self._inventory_data.get('equipment_slots')]
        for bag_idx in range(len(bags)):
            bag = bags[bag_idx]
            set_item_gui = fns[bag_idx]
            for idx, item in bag.iter_items():
                if not item:
                    set_item_gui(
                        idx,
                        None,
                        ItemData(item=None, bag=bag, is_equipment=bag_idx == 2),
                        0,
                    )
                    continue
                texture = self._get_item_texture(item)
                assert texture
                set_item_gui(
                    idx,
                    texture,
                    ItemData(item=item, bag=bag, is_equipment=bag_idx == 2),
                    item.get_count(),
                )

