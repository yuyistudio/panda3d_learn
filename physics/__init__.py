#encoding: utf8

from panda3d.core import *
from panda3d.bullet import *
from variable.global_vars import G
import config


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

    def __init__(self, debug=False):
        if PhysicsWorld.instance:
            raise RuntimeError("duplicated physics world")
        PhysicsWorld.instance = self
        self.use_wrapper = False  # TODO 为什么设置为True会非常卡？
        self.world = BulletWorld()
        self.world.setGravity(Vec3(0, 0, -9.81))
        if debug:
            debugNode = BulletDebugNode("debug_bullet")
            self.world.setDebugNode(debugNode)
            #debugNode.showWireframe(True)
            debugNp = G.render.attachNewNode(debugNode)
            debugNp.show()

    def remove_collider(self, physics_np):
        self.world.remove_rigid_body(physics_np.node())

    def addBoxCollider(self, box_np, mass, bit_mask=config.BIT_MASK_OBJECT, reparent=False):
        if config.SHOW_BOUNDS:
            box_np.showTightBounds()

        bb = box_np.getTightBounds()  # calulcate bounds before any rotation or scale
        dx, dy, dz = abs(bb[0].getX() - bb[1].getX()),\
                     abs(bb[0].getY() - bb[1].getY()),\
                     abs(bb[0].getZ() - bb[1].getZ())

        half_size = Vec3(dx/2, dy/2, dz/2)
        shape = BulletBoxShape(half_size)
        body = BulletRigidBodyNode('physical_box_shapes')
        body.setMass(mass)
        body.addShape(shape)
        body.set_static(True)
        body.setIntoCollideMask(bit_mask)

        self.world.attachRigidBody(body)

        np = G.render.attachNewNode(body)
        np.setName("physical_box")
        body.setPythonTag("instance", np)
        np.setPos(box_np.getPos())
        np.setZ(np, dz/2)

        if reparent:
            box_np.setPos(Vec3(0, 0, -dz / 2))
            box_np.reparentTo(np)  # to sync the transform automatically
        return np

    def add_player_controller(self, box_np, bit_mask):
        height = 3.3
        radius = 0.6
        shape = BulletCapsuleShape(radius, height - 2 * radius, ZUp)
        player_node = BulletCharacterControllerNode(shape, 0.4, 'Player')
        player_np = G.render.attach_new_node(player_node)
        player_np.setCollideMask(bit_mask)
        self.world.attachCharacter(player_np.node())
        if box_np:
            box_np.reparentTo(player_np)
            box_np.setPos(Vec3(0, 0, height * -.5))
        return player_np

    def addBoxTrigger(self, box_np, bit_mask):
        if config.SHOW_BOUNDS:
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

    def set_collider_enabled(self, np, enabled):
        if enabled:
            self.world.attach_rigid_body(np.node())
        else:
            self.world.remove_rigid_body(np.node())

    def addGround(self, friction=3):
        shape = BulletPlaneShape(Vec3(0, 0, 1), 0)
        node = BulletRigidBodyNode('physical_ground_shapes')
        node.addShape(shape)
        node.setFriction(friction)
        node.setIntoCollideMask(config.BIT_MASK_GROUND)
        np = G.render.attachNewNode(node)
        np.setName("physical_ground")  # if unset, take the name of its node
        np.setPos(0, 0, 0)
        self.world.attachRigidBody(node)
        return np

    def onUpdate(self, dt):
        self.world.do_physics(dt)

    def mouseHit(self, distance=1000):
        mn = G.mouseWatcherNode
        if not mn.hasMouse():
            return []
        render = G.render

        # Get from/to points from _mouse click
        pMouse = mn.getMouse()
        pFrom = Point3()
        pTo = Point3()
        G.camLens.extrude(pMouse, pFrom, pTo)
        pFrom = render.getRelativePoint(G.cam, pFrom)
        pTo = render.getRelativePoint(G.cam, pTo)
        pTo = pFrom + (pTo - pFrom) .normalized() * distance

        result = self.world.rayTestAll(pFrom, pTo, config.BIT_MASK_MOUSE)
        return result.getHits() or []
