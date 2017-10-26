#encoding: utf8

from base_actions import *


class ActionPick(BaseActionHand):
    """
    采集
    """
    def __init__(self, config):
        BaseActionHand.__init__(self, config)


class ActionPickup(BaseActionHand):
    """
    捡起
    """
    def __init__(self, config):
        BaseActionHand.__init__(self, config)


class ActionBox(BaseActionHand):
    """
    打开箱子
    """
    def __init__(self, config):
        BaseActionHand.__init__(self, config)


class ActionCut(BaseActionDestroy):
    """
    砍树等
    """
    def __init__(self, config):
        BaseActionDestroy.__init__(self, config)


class ActionMining(BaseActionDestroy):
    """
    采矿
    """
    def __init__(self, config):
        BaseActionDestroy.__init__(self, config)
