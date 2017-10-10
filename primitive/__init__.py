# -*-coding:utf-8-*-

from panda3d.core import *
from panda3d.ode import OdePlaneGeom
import physics
import variable

def make_ground(parent_np):
    # Add a plane to collide with
    cm = CardMaker("Plane")
    size = 1000
    cm.setFrame(-size, size, -size, size) # left/right/bottom/top
    card = cm.generate()

    ground = parent_np.attachNewNode("visual_ground")
    ground.setPos(0, 0, 0)
    ground.setColorScale(.77, .88, .77, 1)
    card_np = ground.attachNewNode(card)
    card_np.look_at(0, 0, -1)

    return variable.show_base.physics_world.addGround(ground)
