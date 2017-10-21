#encoding: utf8

__author__ = 'Leon'

import sys
sys.path.insert(0, 'D:\\Leon\\gamedev\\pandas3d\\learn')
from grid_layout import *
from mouse_info import MouseGUI
from variable.global_vars import G
from panda3d.core import Texture
from gui_system import GUIManager


def test():
    gm = GUIManager()

    G.run()


if __name__ == '__main__':
    test()
