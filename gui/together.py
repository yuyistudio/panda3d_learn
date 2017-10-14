#encoding: utf8

__author__ = 'Leon'

from layout import ALIGNMENT_RIGHT, GridLayout
from mouse_info import MouseGUI
from variable.global_vars import G

def test():
    mg = MouseGUI()
    mg.setItem(None)
    mg.setText(None)

    def hover(item, is_hover):
        if is_hover:
            mg.setText(str(item.getName()))
        else:
            mg.setText(None)

    def cb(item, idx, button):
        if button == 'mouse1':
            button = 'left mouse'
            mg.setItem(item['image'])
        elif button == 'mouse3':
            button = 'right mose'
        print 'click %d-th item with key `%s`' % (idx, button)

    gl = GridLayout(5, 2, cb, hover, ALIGNMENT_RIGHT)
    images = 'apple axe orange iron silver sapling cooking_pit cobweb'.split()
    for image_path in images:
        used_texture = G.loader.loadTexture("../images/items/%s.png" % image_path)
        gl.addButton(used_texture)
    gl.setPos(-0.01, 0)
    gl.setScale(0.5)

    G.schedule(mg.onUpdate, 'mouse_gui_update')

    G.run()


if __name__ == '__main__':
    test()
