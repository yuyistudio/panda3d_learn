#encoding: utf8

import logging
import sys
sys.path.insert(0, 'D:\\Leon\\gamedev\\pandas3d\\learn')
from variable.global_vars import G
from direct.gui.DirectGui import *
from panda3d.core import *

ALIGNMENT_BOTTOM = 0
ALIGNMENT_LEFT = 1
ALIGNMENT_RIGHT = 2
ALIGNMENT_CENTER = 3
ALIGNMENT_BOTTOM_RIGHT = 4


class GridLayout(object):
    def __init__(self, cell_bk_image, bk_image, rows=2, cols=2,
                 click_callback=None, hover_callback=None,
                 alignment=ALIGNMENT_CENTER,
                 cell_width=0.2, cell_height=0.2,
                 margin=0.015, padding_horizontal=0.05, padding_vertical=0.1, extra_image=True):
        self._font = G.res_mgr.get_font('default')
        self._digital_font = G.res_mgr.get_font('digital')
        self._rows = rows
        self._cols = cols
        self._user_data = [None] * (self._rows * self._cols)
        self._cell_width = cell_width
        self._cell_height = cell_height
        self._margin = margin
        self._padding_h = padding_horizontal
        self._padding_v = padding_vertical
        self._extra_image = extra_image

        self._click_cb = click_callback
        self._hover_cb = hover_callback

        total_width = self._padding_h * 2 + (cell_width + margin) * (self._cols - 1) + cell_width
        total_height = self._padding_v * 2 + (cell_height + margin) * (self._rows - 1) + cell_height
        # print "total size:", total_width, total_height

        self._scale = 1
        self._cell_normal_scale = 1
        self._cell_hover_scale = 1.05
        self._offset = Point3(0)
        self._normal_color = (.9, .9, .9, 1)
        self._hover_color = (1, 0.95, 0.95, 1)

        self._cell_h_scale = cell_height / 2
        self._cell_w_scale = cell_width / 2
        self._cell_scale = (self._cell_w_scale, 1, self._cell_h_scale)

        self._container = DirectFrame(
            image=G.loader.loadTexture(bk_image),
            image_scale=(total_width/2.,0,total_height/2.),
            image_color=(0, 0, 0, 0),
            frameColor=(1, 0, 0, 0),
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
        elif alignment == ALIGNMENT_BOTTOM_RIGHT:
            self._base_pos = Point3(-total_width / 2, 0, total_height / 2)
            self._container.reparent_to(G.a2dBottomRight)
        else:
            self._base_pos = Point3(0,0,0)
            self._container.reparentTo(G.aspect2d)

        self._cell_texture = G.loader.loadTexture(cell_bk_image)
        self._cell_texture.set_magfilter(Texture.FT_nearest)
        self._cell_texture.set_minfilter(Texture.FT_nearest)
        self._container.setPos(self._base_pos)
        self._cells = []
        self._cell_images = []
        for i in range(rows * cols):
            self._addCell()
            self._idx += 1

    def setVisible(self, visible=True):
        if visible:
            self._container.show()
        else:
            self._container.hide()

    def setNormalColor(self, c):
        self._normal_color = c

    def setScale(self, s):
        self._scale = s
        self._container.setScale(s)
        pos = self._base_pos * self._scale + self._offset
        self._container.setPos(pos)

    def setPos(self, x, y):
        self._offset = Point3(x, 0, y)
        pos = self._base_pos * self._scale + self._offset
        self._container.setPos(pos)

    def _addCell(self):
        assert self._idx <= (self._rows * self._cols)
        col = self._idx % self._cols
        row = self._idx / self._cols

        # container apperance
        cell = DirectButton(image=self._cell_texture, relief=4, image_scale=self._cell_scale,
                            borderWidth=(0.01, 0.01), frameColor=(1, 0, 0, 0.0),
                            sortOrder=1,
                            )
        cell.setTransparency(1)

        # position & size
        frame = self._container['frameSize']
        bx = frame[0] + self._padding_h + col * (self._margin + self._cell_width) + self._cell_width / 2
        by = frame[3] - (self._padding_v + row * (self._margin + self._cell_height) + self._cell_height / 2)
        cell["frameSize"] = (-self._cell_width/2, self._cell_width/2, -self._cell_height/2, self._cell_height/2)
        cell.setPos(bx, 0, by)
        cell.reparentTo(self._container)

        # _main_menu_events
        cell['state'] = DGG.NORMAL
        cell.bind(DGG.WITHOUT, self._on_cell_hover, [self._idx, False])
        cell.bind(DGG.WITHIN, self._on_cell_hover, [self._idx, True])
        cell.bind(DGG.B1PRESS, self._on_cell_clicked, [self._idx])
        cell.bind(DGG.B2PRESS, self._on_cell_clicked, [self._idx])
        cell.bind(DGG.B3PRESS, self._on_cell_clicked, [self._idx])

        # image
        img = None
        if self._extra_image:
            img = DirectFrame(relief=4, scale=self._cell_h_scale, image_scale=self._cell_scale, frameColor=(0,0,0,0))
            img.reparentTo(cell)
            img.setTransparency(1)
            img.bind(DGG.B1PRESS, self._on_cell_clicked, [self._idx])
            img.bind(DGG.B2PRESS, self._on_cell_clicked, [self._idx])
            img.bind(DGG.B3PRESS, self._on_cell_clicked, [self._idx])

        # initialization
        self._cells.append(cell)
        self._cell_images.append(img)
        self._inner_cell_hover(self._idx, False, None)
        return cell, img

    def _on_cell_hover(self, idx, status, event_info):
        if self._hover_cb:
            self._hover_cb(self._user_data[idx], idx, status)
        self._inner_cell_hover(idx, status, event_info)

    def _inner_cell_hover(self, idx, status, event_info):
        cell = self._cells[idx]
        if status:
            cell['image_color'] = self._hover_color
            cell.setScale(self._cell_hover_scale)
        else:
            cell['image_color'] = self._normal_color
            cell.setScale(self._cell_normal_scale)

    def _on_cell_clicked(self, idx, event_info):
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
        self._click_cb(self._user_data[idx], idx, button)


class InventoryLayout(GridLayout):
    def __init__(self, *args, **kwargs):
        self._labels = []
        GridLayout.__init__(self, *args, **kwargs)

    def _addCell(self):
        cell, img = GridLayout._addCell(self)

        # label
        count_label = DirectFrame(text="", frameColor=(0,0,0,0), text_align=TextNode.ABoxedLeft,
                                  text_scale=0.07, text_fg=(.9,.9,.9,1), text_bg=(0,0,0,.3),
                                  text_font=self._digital_font,
                                  sortOrder=0)
        count_label.reparentTo(cell)
        count_label.bind(DGG.B1PRESS, self._on_cell_clicked, [self._idx])
        count_label.bind(DGG.B2PRESS, self._on_cell_clicked, [self._idx])
        count_label.bind(DGG.B3PRESS, self._on_cell_clicked, [self._idx])
        count_label.ignore(DGG.B1PRESS)
        count_label.setBin("gui-popup", 50)  # 真奇怪的设计。setOrder不起作用，但是这玩意竟然起作用。

        self._labels.append(count_label)

        # freshness
        # TODO

        return cell, img

    def set_item(self, index, image_path, data=None, count=-1):
        self._user_data[index] = data

        self._cell_images[index]['image'] = image_path
        if count < 1:
            self._labels[index]['text'] = ''
        else:
            self._labels[index]['text'] = str(count)


class MenuLayout(GridLayout):
    def __init__(self, *args, **kwargs):
        GridLayout.__init__(self, *args, **kwargs)

    def _addCell(self):
        cell, img = GridLayout._addCell(self)
        return cell, img

    def setItem(self, index, text, data=None):
        cell = self._cells[index]
        cell['text'] = text
        cell['sortOrder'] = 0
        cell['text_font'] = self._font
        cell['text_scale'] = self._cell_h_scale
        cell['text_fg'] = (255, 255, 255, 255)
        cell['text_pos'] = (0, -0.03)
        self._user_data[index] = data


def test():
    def cb(item, idx, button):
        if button == 'mouse1':
            button = 'left _mouse'
        elif button == 'mouse3':
            button = 'right mose'
        print 'click %d-th item with key `%s`' % (idx, button)
    gl = GridLayout(5, 2, cb, alignment=ALIGNMENT_RIGHT)
    images = 'apple axe orange iron silver sapling cooking_pit cobweb'.split()
    for image_path in images:
        used_texture = G.loader.loadTexture("assets/images/items/%s.png" % image_path)
        gl._addCell(used_texture)
    gl.setPos(-0.01, 0)
    gl.setScale(0.5)
    G.run()


if __name__ == '__main__':
    test()
