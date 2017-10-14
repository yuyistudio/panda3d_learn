#encoding: utf8

from variable.global_vars import G
from direct.gui.DirectGui import *
from panda3d.core import *

ALIGNMENT_BOTTOM = 0
ALIGNMENT_LEFT = 1
ALIGNMENT_RIGHT = 2
ALIGNMENT_ENTER = 3


class GridLayout(object):
    def __init__(self, rows, cols, click_callback=None, hover_callback=None, alignment=ALIGNMENT_ENTER, cell_width=0.2, cell_height=0.2, margin=0.015, padding_horizontal=0.05, padding_vertical=0.1):
        self._rows = rows
        self._cols = cols
        self._cell_width = cell_width
        self._cell_height = cell_height
        self._margin = margin
        self._padding_h = padding_horizontal
        self._padding_v = padding_vertical

        self._click_cb = click_callback
        self._hover_cb = hover_callback

        total_width = self._padding_h * 2 + (cell_width + margin) * (self._cols - 1) + cell_width
        total_height = self._padding_v * 2 + (cell_height + margin) * (self._rows - 1) + cell_height
        print total_width/total_height*400

        self._scale = 1
        self._offset = Point3(0)
        self.normal_color = (1, 1, 1, 1)
        self.hover_color = (1, 0.95, 0.95, 1)
        self.normal_scale = cell_width / 2
        self.hover_scale = self.normal_scale * 1.3

        self._container = DirectFrame(
            image=G.loader.loadTexture("../images/gui/bag_cell.png"),
            image_scale=(total_width/2.,0,total_height/2.),
            frameColor=(0, 0, 0, 0),
            frameSize=(-total_width/2, total_width/2, -total_height/2, total_height/2),
        )
        self._container.setTransparency(1)
        self._idx = 0
        if alignment == ALIGNMENT_BOTTOM:
            self._base_pos = Point3(0, 0, total_height / 2)
            self._container.reparentTo(G.a2dBottomCenter)
        elif alignment == ALIGNMENT_LEFT:
            self._base_pos = Point3(total_width / 2, 0, 0)
            self._container.reparentTo(G.a2dLeftCenter)
        elif alignment == ALIGNMENT_RIGHT:
            self._base_pos = Point3(-total_width / 2, 0, 0)
            self._container.reparentTo(G.a2dRightCenter)
        else:
            self._base_pos = Point3(0,0,0)
            self._container.reparentTo(G.aspect2d)

        self._container.setPos(self._base_pos)

    def setNormalColor(self, c):
        self.normal_color = c

    def setScale(self, s):
        self._scale = s
        self._container.setScale(s)
        pos = self._base_pos * self._scale + self._offset
        self._container.setPos(pos)

    def setPos(self, x, y):
        self._offset = Point3(x, 0, y)
        pos = self._base_pos * self._scale + self._offset
        self._container.setPos(pos)

    def addButton(self, image_path):
        assert self._idx <= (self._rows * self._cols)

        item = DirectButton(image=image_path, relief=4,
                            borderWidth=(0.01, 0.01), frameColor=(0, 0, 0, 0.3))
        item.setTransparency(1)

        count_label = DirectLabel(text="99", frameColor=(0,0,0,1), text_align=TextNode.ABoxedLeft,
                                  text_scale=0.1, text_fg=(.9,.9,.9,1))
        count_label.reparentTo(item)

        item['state'] = DGG.NORMAL
        item.bind(DGG.WITHOUT, self._on_cell_hover, [item, False])
        item.bind(DGG.WITHIN, self._on_cell_hover, [item, True])
        item.bind(DGG.B1PRESS, self._on_cell_clicked, [item, self._idx])
        item.bind(DGG.B2PRESS, self._on_cell_clicked, [item, self._idx])
        item.bind(DGG.B3PRESS, self._on_cell_clicked, [item, self._idx])

        col = self._idx % self._cols
        row = self._idx / self._cols
        self._idx += 1

        frame = self._container['frameSize']
        bx = frame[0] + self._padding_h + col * (self._margin + self._cell_width) + self._cell_width / 2
        by = frame[3] - (self._padding_v + row * (self._margin + self._cell_height) + self._cell_height / 2)
        item["frameSize"] = (-self._cell_width/2, self._cell_width/2, -self._cell_height/2, self._cell_height/2)
        item.setPos(bx, 0, by)
        item.reparentTo(self._container)

        self._on_cell_hover(item, False, None)

    def _on_cell_hover(self, item, status, event_info):
        if self._hover_cb:
            self._hover_cb(item, status)
        if status:
            item['image_color'] = self.hover_color
            item['image_scale'] = self.hover_scale
        else:
            item['image_scale'] = self.normal_scale
            item['image_color'] = self.normal_color

    def _on_cell_clicked(self, item, idx, event_info):
        """
        :param item:
        :param idx:
        :param event_info: PGMouseWatcherParameter
        :return:
        """
        if not self._click_cb:
            return
        button = None
        if event_info.hasButton():
            button = event_info.getButton()
        self._click_cb(item, idx, button)

def test():
    def cb(item, idx, button):
        if button == 'mouse1':
            button = 'left mouse'
        elif button == 'mouse3':
            button = 'right mose'
        print 'click %d-th item with key `%s`' % (idx, button)
    gl = GridLayout(5, 2, cb, alignment=ALIGNMENT_RIGHT)
    images = 'apple axe orange iron silver sapling cooking_pit cobweb'.split()
    for image_path in images:
        used_texture = G.loader.loadTexture("../images/items/%s.png" % image_path)
        gl.addButton(used_texture)
    gl.setPos(-0.01, 0)
    gl.setScale(0.5)
    G.run()


if __name__ == '__main__':
    test()
