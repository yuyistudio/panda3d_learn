#encoding: utf8

from direct.gui.DirectGui import *
from direct.gui import DirectGuiGlobals as DGG
from variable.global_vars import G
from panda3d.core import *

__author__ = 'Leon'

class MouseGUI(object):
    def __init__(self):
        self._scale = .1
        self._text_scale = .9
        self._mouse_gui_root = G.aspect2d.attachNewNode("mouse_gui")
        self._mouse_gui_root.setScale(self._scale)

        self._image = DirectFrame(frameSize=(-.01, .01, -.01, .01), frameColor=(.6, .3, .3, 1))
        self._image.setPos(0, 0, -0.02)
        self._image.reparentTo(self._mouse_gui_root)
        self._image.setTransparency(1)

        self._label = DirectLabel(text="", text_fg=(1, 1, 1, 1),
                                  text_align=TextNode.A_center,
                                  text_bg=(0, 0, 0, 0), color=(0, 0, 0, 0), text_scale=self._text_scale,
                                  suppressMouse=True,
                                  frameSize=(0.01, 0.01, 0.01, 0.01),
                                  sortOrder=10000,
                                  text_font=G.res_mgr.get_font('default'),
                                  )
        self._label.setTransparency(1)
        self._label.reparentTo(self._mouse_gui_root)
        self._label.setPos(0, 0, -0.02)

        self._object_info = None
        self._item_info = None
        self._mouse_item_info = None

    def setItem(self, image, count=1):
        if image:
            self._image['image'] = image
            self._image.setTransparency(1)
            self._image.show()
        else:
            self._image.hide()

    def setVisible(self, visible):
        if visible:
            self._image.show()
            self._label.show()
        else:
            self._image.hide()
            self._label.hide()

    def set_mouse_item_info(self, text):
        self._mouse_item_info = text
        self._setup_text()

    def set_object_info(self, text):
        self._object_info = text
        self._setup_text()

    def set_item_text(self, text):
        self._item_info = text
        self._setup_text()

    def _setup_text(self):
        text = ''
        offset = 0
        if self._object_info:
            offset = 0.2
            text = self._object_info
        if self._item_info:
            offset = 1
            text += '\n' + self._item_info
        if self._mouse_item_info:
            offset = 1 - self._text_scale
            text += '\n' + self._mouse_item_info
        if not text:
            self._label.hide()
            return
        self._label.show()
        self._label['text'] = text
        self._label.setPos(0, 0, offset + text.count('\n') * self._text_scale)

    def onUpdate(self):
        mPos = G.getMouse()
        if not mPos:
            self.set_item_text("")
            self.set_object_info("")
            self.set_mouse_item_info("")
            return
        # mPos = Point3(mPos.getX(), 0, mPos.getZ() - 2 * self._scale)
        self._mouse_gui_root.setPos(mPos)

def test():
    mtip = MouseGUI()
    mtip.setItem(G.loader.loadTexture("assets/images/logo.png"))
    G.schedule(mtip.onUpdate)
    G.run()

if __name__ == '__main__':
    test()