# encoding: utf8

from util import platform_util as putil


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


