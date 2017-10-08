from panda3d.core import *

forward_button = KeyboardButton.ascii_key('w')
backward_button = KeyboardButton.ascii_key('s')
left_button = KeyboardButton.ascii_key('a')
right_button = KeyboardButton.ascii_key('d')

is_button_down = None

def get_direction():
    dx, dy = 0, 0
    if is_button_down(left_button):
        dx = -1
    elif is_button_down(right_button):
        dx = 1

    if is_button_down(forward_button):
        dy = 1
    elif is_button_down(backward_button):
        dy = -1
    return dx, dy
