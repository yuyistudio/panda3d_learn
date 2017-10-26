# -*-coding:utf-8-*-

from panda3d.core import *
from variable.global_vars import G

def make_ground(parent_np):
    # Add a plane to collide with
    '''
    cm = CardMaker("Plane")
    size = 1000
    cm.setFrame(-size, size, -size, size) # left/right/bottom/top
    card = cm.generate()

    ground = parent_np.attachNewNode("visual_ground")
    ground.setPos(0, 0, 0)
    ground.setColorScale(.77, .88, .77, 1)
    card_np = ground.attachNewNode(card)
    card_np.look_at(0, 0, -1)
    '''
    return
