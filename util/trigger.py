#encoding: utf8

'''
_mouse picker based on ray cast from camera view.
collide with specified collide_mask
'''

from pandac.PandaModules import *
import config
from variable.global_vars import G


class MousePicker(object):
    def __init__(self, triggers):
        self.pickerNode = CollisionNode('mouseRay')
        self.pickerNP = G.cam.attachNewNode(self.pickerNode)
        self.pickerNode.setFromCollideMask(BitMask32(config.BIT_MASK_MOUSE))
        self.pickerNode.setIntoCollideMask(0)
        self.pickerRay = CollisionRay()
        self.pickerNode.addSolid(self.pickerRay)
        self.pickerNP.setTag("type", "_mouse")
        triggers.addCollider(self.pickerNP)

    def onUpdate(self):  # mpos is the position of the _mouse on the screen
        if not G.mouseWatcherNode.hasMouse():
            return []
        mpos = G.mouseWatcherNode.getMouse()
        self.pickedObj = None  # be sure to reset this
        self.pickerRay.setFromLens(G.camNode, mpos.getX(), mpos.getY())

class Triggers(object):
    def __init__(self):
        self.collision_traverser = CollisionTraverser()
        if config.SHOW_COLLISION:
            self.collision_traverser.showCollisions(G.render)
        self.queue = CollisionHandlerQueue()

    def addCollider(self, node_path):
        self.collision_traverser.addCollider(node_path, self.queue)

    def getEntries(self):
        self.collision_traverser.traverse(G.render)
        if self.queue.getNumEntries() > 0:
            self.queue.sortEntries()
        return [self.queue.getEntry(i) for i in range(self.queue.getNumEntries())]

def addCollisionBox(box_np, bit_mask, type_tag='unknown', from_enabled=False, to_enabled=False):
    assert(from_enabled or to_enabled)
    bb = box_np.getTightBounds()  # calulcate bounds before any rotation or scale
    dx, dy, dz = abs(bb[0].getX() - bb[1].getX()),\
                 abs(bb[0].getY() - bb[1].getY()),\
                 abs(bb[0].getZ() - bb[1].getZ())
    # for _mouse pick
    cnode = CollisionNode('box_collision')
    '''
     * Create the Box by giving a Center and distances of of each of the sides of
     * box from the Center.
    '''
    cnode.addSolid(CollisionBox(
        Point3((bb[1].getX() + bb[0].getX()) / 2 - box_np.getX(),
               (bb[1].getY() + bb[0].getY()) / 2 - box_np.getY(),
               (bb[1].getZ() + bb[0].getZ()) / 2) - box_np.getZ(),
        dx/2, dy/2, dz/2))
    cnode.setCollideMask(0)
    cnode.setIntoCollideMask(0) # ? necessary ?
    cnode.setFromCollideMask(0)
    if from_enabled:
        cnode.setFromCollideMask(bit_mask)
    if to_enabled:
        cnode.setIntoCollideMask(bit_mask)
    cnp = box_np.attachNewNode(cnode)
    if config.SHOW_COLLISION_BOX:
        cnp.show()
    cnp.setTag("type", type_tag)
    return cnp

def addCollisionSegment(node_path, bit_mask, type_tag='unknown', from_enabled=False, to_enabled=False):
    assert(from_enabled or to_enabled)
    bb = node_path.getTightBounds()  # calulcate bounds before any rotation or scale
    dx, dy, dz = abs(bb[0].getX() - bb[1].getX()),\
                 abs(bb[0].getY() - bb[1].getY()),\
                 abs(bb[0].getZ() - bb[1].getZ())
    # for _mouse pick
    cnode = CollisionNode('box_collision')
    '''
     * Create the Box by giving a Center and distances of of each of the sides of
     * box from the Center.
    '''
    debug_offset = 0.2  # TODO
    cnode.addSolid(CollisionSegment(0, bb[0].getY(), 0,
                                    0, bb[1].getY() + debug_offset, 0))
    cnode.setCollideMask(0)
    if from_enabled:
        cnode.setFromCollideMask(bit_mask)
    if to_enabled:
        cnode.setIntoCollideMask(bit_mask)
    cnp = node_path.attachNewNode(cnode)
    if config.SHOW_COLLISION_BOX:
        cnp.show()
    cnp.setTag("type", type_tag)
    return cnp

def addInfinitePlane(node_path, type_tag, a, b, c, d):
    """
    the equation `ax + by + cz = d` defines the plane.
    """
    cn = CollisionNode('ground_plane')
    cn.setFromCollideMask(0)
    cn.setIntoCollideMask(BitMask32(config.BIT_MASK_GROUND))
    # cp = CollisionPlane(Plane(Vec3(0, 1, 0), Point3(0, 0, 0)))
    cp = CollisionPlane(Plane(0, 0, 1, 0))
    cn.addSolid(cp)
    cnp = node_path.attachNewNode(cn)
    cnp.setTag("type", type_tag)
    return cnp

def addGroundDetectTarge(node_path):
    return addInfinitePlane(node_path, "ground", 0, 0, 1, 0)
