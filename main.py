from variable.global_vars import G
from panda3d.core import *
from objects import ground, box, lights
from hero import create
from panda3d.core import loadPrcFile
from operation import operation
loadPrcFile("./config.prc")


class Game(object):
    def __init__(self):
        G.taskMgr.add(self.ode_physics_task, "physics")

        # create objects
        self.hero = create.Hero()
        self.operation = operation.Operation(self.hero)

        for i in range(2):
            for j in range(2):
                b = box.create(Vec3((i*2, j*2, 0)))
                b.setName("box(%d,%d)" % (i, j))

        ground.create()
        lights.create()

        # start
        G.taskMgr.add(self.onUpdate, "onUpdate")
        G.run()

    def onUpdate(self, task):
        dt = G.taskMgr.globalClock.getDt()
        self.hero.onUpdate(dt)
        self.hero.lookAt(self.operation.look_at_target)
        return task.cont

    def ode_physics_task(self, task):
        dt = G.taskMgr.globalClock.getDt()
        G.physics_world.onUpdate(dt)
        # camera control
        G.cam.set_pos(self.hero.getNP().get_pos() + Vec3(0, -20, 20))
        G.cam.look_at(self.hero.getNP())
        return task.cont


Game()
