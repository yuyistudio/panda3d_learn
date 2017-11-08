#encoding: utf8

from panda3d.core import *
from variable.global_vars import G
import config


def init(render):
    render.setShaderAuto()


def add_point(parent_np):
    plight = PointLight('plight')
    plight.setColor(VBase4(0.2, 0.2, 0.2, 1))
    plnp = parent_np.attachNewNode(plight)
    plight.setShadowCaster(True)
    plnp.setPos(1)
    plight.setAttenuation(LVecBase3(0.001, 0.001, 0.001))
    parent_np.setLight(plnp)
    return plnp


def add_directional(parent_np):
    light = DirectionalLight("DiretionalSunLight")
    light_np = parent_np.attachNewNode(light)
    parent_np.setLight(light_np)
    light_np.setPos(30, -30, 60)
    light_np.look_at(0, 0, 0)
    light.setScene(parent_np)
    light.setShadowCaster(True)
    light.setColor(LVector4(1, 1, 1, 1))
    sun_range = 1
    light.getLens(0).setFilmSize(sun_range, sun_range)  # 设置光照范围.(横向、纵向)
    if config.SHOW_LIGHT_FRUSTUM:
        light.showFrustum()
    wrapper_np = NodePath('sun_light')
    light_np.reparent_to(wrapper_np)
    return wrapper_np


def add_spot(parent_np):
    light = parent_np.attachNewNode(Spotlight("Spot"))
    light.node().setScene(parent_np)
    light.node().setColor(LVector4(0.3, 0.3, 0.3, 1))
    light.node().setShadowCaster(True)
    if config.SHOW_LIGHT_FRUSTUM:
        light.node().showFrustum()
    light.node().getLens().setFov(40)
    light.node().getLens().setNearFar(10, 100)
    parent_np.setLight(light)
    light.setPos(20, 20, 40)
    light.look_at(0, 0, 0)
    return light


def add_ambient(parent_np):
    alight = parent_np.attachNewNode(AmbientLight("Ambient"))
    alight.node().setColor(LVector4(0.3, 0.3, 0.35, 1))
    parent_np.setLight(alight)
    return alight
