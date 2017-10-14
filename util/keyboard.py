from panda3d.core import *
from variable.global_vars import G

forward_button = KeyboardButton.ascii_key('w')
backward_button = KeyboardButton.ascii_key('s')
left_button = KeyboardButton.ascii_key('a')
right_button = KeyboardButton.ascii_key('d')


def get_direction():
    dx, dy = 0, 0
    is_button_down = G.mouseWatcherNode.is_button_down
    if is_button_down(left_button):
        dx = -1
    elif is_button_down(right_button):
        dx = 1

    if is_button_down(forward_button):
        dy = 1
    elif is_button_down(backward_button):
        dy = -1
    return dx, dy
