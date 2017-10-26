__author__ = 'Leon'
#encoding: utf8

__author__ = 'Leon'

import sys
sys.path.insert(0, 'D:\\Leon\\gamedev\\pandas3d\\learn')
from grid_layout import *
from mouse_info import MouseGUI
from variable.global_vars import G
from panda3d.core import Texture


class CenterMenu(object):
    def __init__(self, texts, click_cb, events=None,
                 item_width=.6, item_height=.2):

        m = MenuLayout("assets/images/gui/menu_item.png", "assets/images/gui/menu_bk.png",
                       len(texts), 1,
                       alignment=ALIGNMENT_CENTER,
                       cell_width=item_width,
                       cell_height=item_height,
                       click_callback=click_cb,
                       extra_image=False)
        m.setScale(.5)
        for i in range(len(texts)):
            m.setItem(i, texts[i], events[i] if events else None)
        self._layout = m

    def set_visible(self, visible):
        self._layout.setVisible(visible)

if __name__ == '__main__':
    test()
