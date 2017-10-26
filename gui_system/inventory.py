__author__ = 'Leon'

from grid_layout import *


class Inventory(object):
    def __init__(self):
        self._bag = InventoryLayout("assets/images/gui/cell.png", "assets/images/gui/bag_bk.png", 5, 2, self._click_cb, self._hover_cb, ALIGNMENT_RIGHT)
        self._bag.setPos(-0.01, 0)
        self._bag.setScale(0.5)
        self._item_bar = InventoryLayout("assets/images/gui/cell.png", "assets/images/gui/item_bar.png", 1, 13, self._click_cb, self._hover_cb, ALIGNMENT_BOTTOM)
        self._item_bar.setPos(0, 0.01)
        self._item_bar.setScale(0.5)

    def _hover_cb(self, data, idx, is_hover):
        pass

    def _click_cb(self, data, idx, button):
        return
        if button == 'mouse1':
            button = 'left _mouse'
            mg.setItem(data)
        elif button == 'mouse3':
            button = 'right mose'
        print 'click %d-th item with key `%s`' % (idx, button)

