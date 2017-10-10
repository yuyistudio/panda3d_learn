#encoding: utf8

from panda3d.ode import *
from panda3d.core import *
from panda3d.bullet import *
import variable


class PhysicsWorld(object):
    """
    object hierarchy:
        render
            physical_node (with physical_node_geom)
                visual_node (model / actor)

    trigger hierarchy:
        model node
            trigger_box (ghost node)
    """
    instance = None
    MASS_IFINITE = 0
    COLLISION_EVENT_NAME = "__ODE_COLLISION_EVENT__"
    def __init__(self, debug=True):
        if PhysicsWorld.instance:
            raise RuntimeError("duplicated physics world")
        PhysicsWorld.instance = self
        self.render = variable.show_base.render
        self.render = variable.show_base.render
        self.world = BulletWorld()
        self.world.setGravity(Vec3(0, 0, -9.81))
        if debug:
            debugNode = BulletDebugNode("debug_bullet")
            self.world.setDebugNode(debugNode)
            debugNode.showWireframe(True)
            debugNp = self.render.attachNewNode(debugNode)
            debugNp.show()

    def addBoxCollider(self, box_np, mass, bit_mask=variable.BIT_MASK_OBJECT):
        if variable.SHOW_BOUNDS:
            box_np.showTightBounds()

        bb = box_np.getTightBounds()  # calulcate bounds before any rotation or scale
        dx, dy, dz = abs(bb[0].getX() - bb[1].getX()),\
                     abs(bb[0].getY() - bb[1].getY()),\
                     abs(bb[0].getZ() - bb[1].getZ())

        half_size = Vec3(dx/2, dy/2, dz/2)
        shape = BulletBoxShape(half_size)
        node = BulletRigidBodyNode('physical_box_shapes')
        node.setMass(mass)
        node.addShape(shape)
        node.setIntoCollideMask(bit_mask)

        '''
        # TODO xy-rotation & z-position limitation
        hpr = TransformState.makePosHpr(Point3(-5), Vec3(0, 0, 0))
        hpr2 = TransformState.makePosHpr(Point3(5), Vec3(0, 0, 360))
        gc = BulletGenericConstraint(node, hpr, hpr2)
        #gc.setAngularLimit(0, 0, 0)
        #gc.setAngularLimit(1, 0, 0)
        self.world.attachConstraint(gc)
        '''

        self.world.attachRigidBody(node)

        np = self.render.attachNewNode(node)
        np.setName("physical_box")
        node.setPythonTag("instance", np)
        np.setPos(box_np.getPos())
        np.setZ(np, dz/2)
        box_np.setPos(Vec3(0, 0, -dz/2))
        box_np.reparentTo(np)  # to sync the transform automatically
        return np

    def addBoxTrigger(self, box_np, bit_mask):
        if variable.SHOW_BOUNDS:
            box_np.showTightBounds()

        bb = box_np.getTightBounds()  # calulcate bounds before any rotation or scale
        dx, dy, dz = abs(bb[0].getX() - bb[1].getX()),\
                     abs(bb[0].getY() - bb[1].getY()),\
                     abs(bb[0].getZ() - bb[1].getZ())

        half_size = Vec3(dx/2, dy/2, dz/2)
        shape = BulletBoxShape(half_size)
        node = BulletGhostNode('trigger_box_shapes')
        node.addShape(shape)
        node.setIntoCollideMask(bit_mask)
        self.world.attachGhost(node)

        np = box_np.attachNewNode(node)
        np.setName("rigger_box")
        pos = Point3((bb[1].getX() + bb[0].getX()) / 2 - box_np.getX(),
                     (bb[1].getY() + bb[0].getY()) / 2 - box_np.getY(),
                     (bb[1].getZ() + bb[0].getZ()) / 2 - box_np.getZ())
        np.setPos(pos)
        return np

    def addGround(self, plane_np):
        shape = BulletPlaneShape(Vec3(0, 0, 1), 0)
        node = BulletRigidBodyNode('physical_ground_shapes')
        node.addShape(shape)
        node.setFriction(1)
        node.setIntoCollideMask(variable.BIT_MASK_GROUND)
        np = self.render.attachNewNode(node)
        np.setName("physical_ground")  # if unset, take the name of its node
        np.setPos(0, 0, 0)
        self.world.attachRigidBody(node)
        plane_np.reparentTo(np)
        return np

    def onUpdate(self, dt):
        self.world.doPhysics(dt)

    def mouseHit(self, distance=100):
        mn = variable.show_base.mouseWatcherNode
        if not mn.hasMouse():
            return []
        base = variable.show_base
        render = base.render

        # Get from/to points from mouse click
        pMouse = mn.getMouse()
        pFrom = Point3()
        pTo = Point3()
        base.camLens.extrude(pMouse, pFrom, pTo)
        pFrom = render.getRelativePoint(base.cam, pFrom)
        pTo = render.getRelativePoint(base.cam, pTo)
        pTo = pFrom + (pTo - pFrom) .normalized() * distance

        result = self.world.rayTestAll(pFrom, pTo, variable.BIT_MASK_MOUSE)
        return result.getHits() or []
