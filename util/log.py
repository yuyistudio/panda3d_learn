# encoding: utf8

__author__ = 'Leon'

import logging


def _common(prefix, *args):
    lst = list(args)
    lst[0] = prefix % lst[0]
    logging.warn(*tuple(lst))


def process(*args):
    """
    记录游戏的流程
    :param args:
    :return:
    """
    _common('[PROCESS] %s', *args)


def debug(*args):
    """
    调试信息
    :param args:
    :return:
    """
    _common('[DEBUG] %s', *args)


def error(*args):
    """
    非预期的错误
    :param args:
    :return:
    """
    _common('[ERROR] %s', *args)
    # assert False, args
