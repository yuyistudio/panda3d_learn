# encoding: utf8

import sys
reload(sys)
sys.setdefaultencoding('utf8')

from panda3d.core import *
from direct.showbase.ShowBase import ShowBase
from direct.filter.FilterManager import FilterManager

load_prc_file("./config.prc")

class App(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        self.render.setAntialias(AntialiasAttrib.MMultisample, 1)

        model = self.loader.loadModel("models/panda")
        model.reparent_to(self.render)
        self.cam.set_pos(50, 50, 0)
        self.cam.look_at(model)

        self._manager = FilterManager(self.win, self.cam)
        tex = Texture()
        self.quad = self._manager.renderSceneInto(colortex=tex)
        self.quad.setShader(Shader.load("./mono.sha"))
        self.quad.setShaderInput("tex", tex)

App().run()