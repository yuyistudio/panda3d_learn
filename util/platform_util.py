# encoding: utf8

import platform


PLATFORM_WINDOWS = 0
PLATFORM_LINUX = 1
PLATFORM_MAC = 2
PLATFORM_UNKNOWN = 3


def get_platform():
    """
    :return: macro PLATFORM_*
    """
    sys_str = platform.system()
    if sys_str == 'Windows':
        return PLATFORM_WINDOWS
    if sys_str == 'Linux':
        return PLATFORM_LINUX
    if sys_str == 'Darwin':
        return PLATFORM_MAC
    return PLATFORM_UNKNOWN


def get_platform_str():
    return platform.system()


current_platform = get_platform()

