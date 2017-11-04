__author__ = 'Leon'

from grid_layout import *


class Inventory(object):
    def __init__(self):
        self._bag = InventoryLayout(
            "assets/images/gui/cell.png",
            "assets/images/gui/bag_bk.png",
            5, 2,
            self._click_cb, self._hover_cb,
            ALIGNMENT_RIGHT)
        self._item_bar = InventoryLayout(
            "assets/images/gui/cell.png",
            "assets/images/gui/item_bar.png",
            1, 13,
            self._click_cb, self._hover_cb,
            ALIGNMENT_BOTTOM)
        scale = 0.7
        self._user_hover_cb = None
        self._user_click_cb = None
        self._bag.setPos(-0.01, 0)
        self._bag.setScale(scale)
        self._item_bar.setPos(0, 0.01)
        self._item_bar.setScale(scale)

    def set_bag_item(self, idx, image_path, user_data, count=0):
        self._bag.set_item(idx, image_path, user_data, count)

    def set_item_bar_item(self, idx, image_path, user_data, count=0):
        self._item_bar.set_item(idx, image_path, user_data, count)

    def set_user_cb(self, hover_cb, click_cb):
        self._user_click_cb = click_cb
        self._user_hover_cb = hover_cb

    def _hover_cb(self, data, idx, is_hover):
        if self._user_hover_cb:
            self._user_hover_cb(data, idx, is_hover)

    def _click_cb(self, data, idx, button):
        if self._user_click_cb:
            self._user_click_cb(data, idx, button)

