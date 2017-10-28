#encoding: utf8

import primitive
from util import trigger
from variable.global_vars import G
from panda3d.core import Vec3

def create():
    visual_np = G.physics_world.addGround()
    visual_np.set_python_tag("type", "ground")
    return visual_np
