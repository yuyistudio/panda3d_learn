#encoding: utf8

import primitive
from util import trigger
import variable

def create():
    visual_np = primitive.make_ground(variable.show_base.render)
    visual_np.setTag("type", "ground")
    return visual_np
