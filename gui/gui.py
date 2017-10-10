#encoding: utf8

from direct.actor.Actor import  Actor
from direct.showbase.ShowBase import ShowBase
from panda3d.core import *
loadPrcFile("../config.prc")
from direct.gui.DirectGui import *

class Test(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        self.disableMouse()

        anims = ["walk", "pickup", "jump", "idle", "craft", "tool", "boring", "pick", "pickup"]
        anim_mapping = {}
        for aname in anims:
            anim_mapping[aname] = "../blender/hero-%s" % aname
        ac = Actor("../blender/hero", anim_mapping)
        ac.reparent_to(self.render)
        #ac.setPos(10)
        ac.setH(45)
        ac.loop("walk")
        self.cam.setPos(0)
        self.cam.lookAt(ac)
        self.ac = ac

        # Add button
        self.panda = self.loader.loadModel("models/panda")
        self.b = DirectButton(text=("pleasev click me","click it"), scale=.1, command=self.setText, relief=DGG.GROOVE, pos=Vec3(0.5, 0, 0.1), text_pos=(0,1))
        self.b2 = DirectButton(text="another_button\nline2\n last line --", command=self.setText, relief=DGG.GROOVE)
        self.b2.setPos(0, 0, 5)
        self.b2.reparentTo(self.b)
        #self.b.reparentTo(self.a2dBottomLeft)
        #self.b = DirectButton(geom=self.ac, scale=.1, command=self.setText, relief=None)

    def setText(self):
        #self.b['text'] = 'clicked!'
        self.b.resetFrameSize()
        print("click")

Test().run()