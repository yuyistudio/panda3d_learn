#encoding: utf8

from panda3d.core import *
from direct.showbase.ShowBase import ShowBase


class GlobalVariable(ShowBase):
    """
    A lightweight wrapper for Panda3D's APIs.
    """
    def __init__(self):
        ShowBase.__init__(self)

        '''
        import sys
        sys.path.insert(0, './render_pipeline')

        from render_pipeline.rpcore import RenderPipeline
        self.render_pipeline = RenderPipeline()
        self.render_pipeline.create(self)
        '''
        self.disableMouse()
        self.render.setAntialias(AntialiasAttrib.MMultisample, 1)
        self.debug = True

    def schedule(self, fn, name="update"):
        def _wrapper_(task):
            fn()
            return task.cont
        self.taskMgr.add(_wrapper_, name)

    def getMouse(self):
        m = self.mouseWatcherNode
        if not m.hasMouse():
            return False
        p = m.getMouse()
        fs = G.camLens.getFilmSize()
        if fs.getX() > fs.getY():
            mx, my = p.getX() * fs.getX() / fs.getY(), p.getY()
        else:
            mx, my = p.getX(), p.getY() * fs.getY() / fs.getX()
        return Point3(mx, 0, my)

G = GlobalVariable()

# 添加一些全局遍历。
# 不在G的实例化时直接赋值的原因是，这些全局遍历也依赖于G进行初始化。

from util import trigger
import physics

G.triggers = trigger.Triggers()
G.physics_world = physics.PhysicsWorld()
