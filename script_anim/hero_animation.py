#encoding: utf8

from panda3d.core import *
import variable
from direct.actor.Actor import Actor

def load_hero():
    anims = ["walk", "pickup", "jump", "idle", "craft", "tool", "boring", "pick", "pickup"]
    anim_mapping = {}
    for aname in anims:
        anim_mapping[aname] = "blender/hero-%s" % aname
    np = Actor("blender/hero", anim_mapping)
    for tex in np.find_all_textures():
        tex.set_magfilter(Texture.FT_nearest)
        tex.set_minfilter(Texture.FT_linear)
    np.set_name("hero_actor")
    np.reparent_to(variable.show_base.render)

    return np
