# encoding: utf8

__author__ = 'Leon'
from direct.filter.FilterManager import FilterManager
from variable.global_vars import G
from panda3d.core import Shader, Texture, Vec2
import math


class PostEffects(object):
    def __init__(self):
        self._manager = FilterManager(G.win, G.cam)
        self._quads = []
        self._turned_on = False
        self._c = 0

    def turn_on(self):
        if self._c < 30:
            self._c += 1
            return
        if self._turned_on:
            return
        self._turned_on = True

        # TODO 开启之后会报错 :display:gsg:glgsg(error): GL error GL_INVALID_OPERATION
        # 现象是没法儿和anti-alias一起用。config里面的anti-alias不开，就不报错。
        # 而且必须等程序跑一小会儿才能turn_on，否则会有异常，不知道啥原因，估计是P3D的bug.

        self.enable_fxaa()

    def enable_fxaa(self):
        tex1 = Texture()
        quad1 = self._manager.renderQuadInto(colortex=tex1)
        tex2 = Texture()
        self._quads.append(quad1)

        quad1.setShader(Shader.load("assets/shaders/post/fxaa.sha"))
        quad1.setShaderInput("color", tex1)
        quad1.setShaderInput("active", 1)

        quad2 = self._manager.renderSceneInto(colortex=tex2)
        self._quads.append(quad2)
        quad2.setShader(Shader.load("assets/shaders/post/color.sha"))
        quad2.setShaderInput("tex", tex2)

    def on_update(self, dt):
        pass


