#encoding: utf8

from panda3d.core import BitMask32

show_base = None
MB_MOUSE = 1 << 1
MB_TOOL = 1 << 2

# from
BIT_MASK_MOUSE = BitMask32(MB_MOUSE)
BIT_MASK_TOOL = BitMask32(MB_TOOL)

# to
BIT_MASK_GROUND = BitMask32(MB_MOUSE)
BIT_MASK_OBJECT = BitMask32(MB_MOUSE | MB_TOOL)
BIT_MASK_HERO = BitMask32(MB_MOUSE)

ODE_COMMON = BitMask32(0x00000001)
ODE_CATEGORY_COMMON = BitMask32(0x00000001)

DEBUG = True
SHOW_BOUNDS = False
SHOW_COLLISION_BOX = False
SHOW_COLLISION = False
SHOW_LIGHT_FRUSTUM = False
