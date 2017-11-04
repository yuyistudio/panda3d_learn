# encoding: utf8

from util import platform_util as putil
import random
import math

if putil.current_platform == putil.PLATFORM_MAC:
    from thirdparty.mac import noise
elif putil.current_platform == putil.PLATFORM_WIN64:
    from thirdparty.win64 import noise
else:
    assert False, 'unsupported platform: `%s`, ID: %s' % (putil.get_platform_str(), putil.current_platform)


def perlin_noise_2d(x, y, scale=1):
    """
    :param x:
    :param y:
    :return: range (0,1)
    """
    v = noise.pnoise2(x * scale, y * scale)
    return .5 * (v + 1)


def pos_around(center_point, radius):
    angle = math.radians(random.randint(0, 360))
    x = center_point.get_x() + radius * math.sin(angle)
    y = center_point.get_y() + radius * math.cos(angle)
    return x, y