#encoding: utf8

import primitive
from util import trigger
import variable

def create():
    ground = primitive.make_ground(variable.show_base.render)
    trigger.addGroundDetectTarge(ground)
    return ground
