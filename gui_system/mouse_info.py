#encoding: utf8

from direct.gui.DirectGui import *
from variable.global_vars import G
from panda3d.core import *

__author__ = 'Leon'

class MouseGUI(object):
    def __init__(self):
        self._scale = .1
        self._mouse_gui_root = G.aspect2d.attachNewNode("mouse_gui")
        self._mouse_gui_root.setScale(self._scale)

        self._label = DirectLabel(text="item info", text_fg=(1, 1, 1, 1),
                                  text_align=TextNode.ALeft,
                                  text_bg=(0, 0, 0, 0), color=(0, 0, 0, 0), text_scale=0.7,
                                  suppressMouse=True)
        self._label.setTransparency(1)
        self._label.reparentTo(self._mouse_gui_root)
        self._label.setPos(1, 0, -1)

        self._image = DirectFrame(frameSize=(-1, 1, -1, 1), frameColor=(.6, .3, .3, 0.2),
                                  suppressMouse=True)
        self._image.setPos(1, 0, -1)
        self._image.reparentTo(self._mouse_gui_root)
        self._image.setTransparency(1)
        self.setText("DEBUG STRING")

    def setItem(self, image, count=1):
        if image:
            self._image['image'] = image
            self._image.setTransparency(1)
            self._image.show()
        else:
            self._image.hide()

    def setVisible(self, visible):
        if visible:
            self._label.show()
        else:
            self._label.hide()

    def setText(self, text):
        if not text:
            self._label.hide()
            return
        self._label.show()
        self._label['text'] = text
        self._label.setPos(0, 0, -1)

    def onUpdate(self):
        mPos = G.getMouse()
        if not mPos:
            self.setText("")
            return
        mPos = Point3(mPos.getX(), 0, mPos.getZ() - 2 * self._scale)
        self._mouse_gui_root.setPos(mPos)

def test():
    mtip = MouseGUI()
    mtip.setItem(G.loader.loadTexture("assets/images/logo.png"))
    G.schedule(mtip.onUpdate)
    G.run()

if __name__ == '__main__':
    test()