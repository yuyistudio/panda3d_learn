#encoding: utf8

from panda3d.ode import *
from panda3d.core import *
import math
from panda3d.core import VBase3, Point3
import variable

class PhysicsWorld(object):
    instance = None
    COLLISION_EVENT_NAME = "__ODE_COLLISION_EVENT__"
    def __init__(self, root_np):
        if PhysicsWorld.instance:
            raise RuntimeError("duplicated physics world")
        PhysicsWorld.instance = self

        self.root_np = root_np
        self.world = OdeWorld()
        self.world.setGravity(0, 0, -9.81)
        self.world.initSurfaceTable(1)
        self.world.setSurfaceEntry(0, 0, # id pair
                                   1.3, # frection
                                   0, # bouce
                                   9.1, # minimum bounce angle
                                   0.0, # how soft?
                                   0.0, # how sof?
                                   10, # slip. make body to slide past another!
                                   0.0) # dampen

        space = OdeQuadTreeSpace(Point3(0, 0, 0), VBase3(100, 100, 100), 3)  # center extents depth
        space.setAutoCollideWorld(self.world)
        self.contactgroup = OdeJointGroup()
        space.setAutoCollideJointGroup(self.contactgroup)
        self.space = space
        self.space.setCollisionEvent(self.COLLISION_EVENT_NAME)
        #self.space.autoCollide()
        self.np_list = []


    def addBoxCollider(self, box_np, density=1000, is_static=False, auto_transform=True, auto_disable=True):
        if variable.SHOW_BOUNDS:
            box_np.showTightBounds()

        bb = box_np.getTightBounds()  # calulcate bounds before any rotation or scale
        dx, dy, dz = abs(bb[0].getX() - bb[1].getX()),\
                     abs(bb[0].getY() - bb[1].getY()),\
                     abs(bb[0].getZ() - bb[1].getZ())

        rigid_body = None
        if not is_static:
            rigid_body = OdeBody(self.world)
            M = OdeMass()
            M.setBox(density, dx, dy, dz)  # first argument means density
            rigid_body.set_mass(M)
            rigid_body.set_auto_disable_flag(auto_disable)  # TODO setup auto disable
            rigid_body.set_position(box_np.getPos(self.root_np))
            rigid_body.set_quaternion(box_np.getQuat(self.root_np))

            if auto_transform:
                self.np_list.append((box_np, rigid_body, auto_transform))

        box_geom = OdeBoxGeom(self.space, dx, dy, dz)  # dx/dy/dz is side length
        box_geom.setCollideBits(variable.ODE_COMMON)
        box_geom.setCategoryBits(variable.ODE_CATEGORY_COMMON)
        if rigid_body:
            box_geom.setBody(rigid_body)
            box_geom.setOffsetPosition(0, 0, dz/2)  # setup geom's relative position from its body
        else:
            pos = box_np.get_pos()
            pos.add_z(dz / 2)
            box_geom.set_position(pos)
        return rigid_body

    def addPlaneCollider(self, plane_np):
        geom = OdePlaneGeom(plane_np, Vec4(0, 0, 1, 0))
        geom.setCollideBits(BitMask32(0x00000001))
        geom.setCategoryBits(BitMask32(0x00000001))

    # The task for our simulation
    def simulationTask(self, task, dt):
        self.space.autoCollide()  # Setup the contact joints

        # avoid large step problem
        if dt > 0.1:
            return task.cont
        # Step the simulation and set the new positions
        self.world.quickStep(dt)
        for np, body, auto_transform in self.np_list:
            if auto_transform:
                np.setPosQuat(self.root_np, body.getPosition(), Quat(body.getQuaternion()))
            else:
                pass
                #np.setPos(self.root_np, body.getPosition())
        self.contactgroup.empty()  # Clear the contact joints
        return task.cont
