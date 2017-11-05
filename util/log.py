# encoding: utf8

__author__ = 'Leon'

import logging
import sys
import os


def _common(prefix, *args):
    frame = sys._getframe(1)
    frame2 = sys._getframe(2)
    line_info = '[%s:%s]' % (os.path.basename(frame2.f_code.co_filename), frame.f_back.f_lineno)
    lst = list(args)
    lst[0] = prefix % (line_info, lst[0])
    logging.warn(*tuple(lst))


def process(*args):
    """
    记录游戏的流程
    :param args:
    :return:
    """
    _common('[PROCESS] %s %s', *args)


def debug(*args):
    """
    调试信息
    :param args:
    :return:
    """
    _common('[DEBUG] %s %s', *args)


def error(*args):
    """
    非预期的错误
    :param args:
    :return:
    """
    _common('[ERROR] %s %s', *args)
    # assert False, args
