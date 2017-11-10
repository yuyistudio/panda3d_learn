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
        self._c += 1
        if self._c < 0:
            return
        if self._turned_on:
            return
        self._turned_on = True
#        return  # TODO

        tex = Texture()
        quad = self._manager.renderSceneInto(colortex=tex)
        quad.setShader(Shader.load("assets/shaders/post/fxaa.sha"))
        quad.setShaderInput("color", tex)
        quad.setShaderInput("active", 1)
        self._quads.append(quad)

        return
        tex = Texture()
        quad = self._manager.renderSceneInto(colortex=tex)
        quad.setShader(Shader.load("assets/shaders/post/mono.sha"))
        quad.setShaderInput("tex", tex)
        self._quads.append(quad)

    def on_update(self, dt):
        pass


