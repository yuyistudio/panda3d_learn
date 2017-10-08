import physics
from panda3d.core import *
from direct.showbase.ShowBase import ShowBase
import variable
from util import draw, keyboard, trigger
from objects import ground, box, lights
from hero import create
from panda3d.core import loadPrcFile
from operation import operation
loadPrcFile("./config.prc")

class Test(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        self.disableMouse()

        # setup global environment
        variable.show_base = self
        keyboard.is_button_down = self.mouseWatcherNode.is_button_down
        self.triggers = trigger.Triggers()
        self.physics_world = physics.PhysicsWorld(self.render)
        self.taskMgr.add(self.ode_physics_task, "physics")

        # create objects
        self.hero = create.Hero()
        self.operation = operation.Operation()

        for i in range(2):
            for j in range(2):
                b = box.create(Vec3((i*2, j*2, 0)))
                b.setName("box(%d,%d)" % (i, j))

        ground.create()
        lights.create()

        # start
        self.taskMgr.add(self.onUpdate, "onUpdate")

    def onUpdate(self, task):
        dt = self.taskMgr.globalClock.getDt()
        self.hero.onUpdate(dt)
        self.hero.lookAt(self.operation.look_at_target)
        return task.cont

    def ode_physics_task(self, task):
        self.physics_world.simulationTask(task, self.taskMgr.globalClock.getDt())
        # camera control
        self.cam.set_pos(self.hero.getNP().get_pos() + Vec3(0, -20, 20))
        self.cam.look_at(self.hero.getNP())
        return task.cont

Test().run()