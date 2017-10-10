#encoding: utf8

from panda3d.core import *
from direct.interval.IntervalGlobal import *
from direct.gui import *
from direct.showbase.ShowBase import ShowBase
from direct.interval.LerpInterval import LerpPosInterval

class MyApp(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        font = self.loader.loadFont("Minecraft.ttf")
        tn = TextNode('title')
        tn.setText("Art Of Rain")
        tn.setFont(font)
        tn.setAlign(TextNode.ACenter)
        tn.setWordwrap(0)  # auto wrap
        tn.setShadow(.02, .02)
        tn.setShadowColor(0.5, 0, 0, 1)
        tn.setTextColor(1, 1, 1, 1)

        tnp = self.aspect2d.attachNewNode(tn)
        tnp.setScale(.1)

        # a simple animation
        duration = 1.5
        angle = 10
        i1 = LerpHprInterval(tnp, duration, Vec3(0, 0, angle), Vec3(0, 0, -angle), blendType='easeInOut')
        i2 = LerpHprInterval(tnp, duration, Vec3(0, 0, -angle), Vec3(0, 0, angle), blendType='easeInOut')
        seq = Sequence(i1, i2)
        seq.loop()


app = MyApp()
app.run()