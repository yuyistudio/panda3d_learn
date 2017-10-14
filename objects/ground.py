#encoding: utf8

import primitive
from util import trigger
from variable.global_vars import G


def create():
    visual_np = primitive.make_ground(G.render)
    visual_np.setTag("type", "ground")
    return visual_np
