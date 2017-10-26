# encoding: utf8

from base_components import BaseComponent


class BaseAction(BaseComponent):
    def __init__(self, config):
        BaseComponent.__init__(self, config)

    def get_inspect_info(self):
        """
        overwrite this.
        :return: one item for a line. eg. ['Action Name', 'Action Usage Hint']
        """
        return []

    def on_left_click(self):
        """
        overwrite this.
        :return:
        """
        pass

    def on_right_click(self):
        """
        overwrite this.
        :return:
        """
        pass


class BaseActionTool(BaseAction):
    """
    需要使用工具来进行的Action.
        例如: 点火, 采矿
    这个类会做工具的类型匹配等工作.
    """
    def __init__(self, config):
        BaseAction.__init__(self, config)


class BaseActionHand(BaseAction):
    """
    空手即可进行的Action.
        例如: 采摘, 捡东西, 拨开关
    """
    def __init__(self, config):
        BaseAction.__init__(self, config)


class BaseActionChange(BaseActionTool):
    """
    导致目标状态变化的Action.
        例如: 拨开关, 点火
    """
    def __init__(self, config):
        BaseActionTool.__init__(self, config)


class BaseActionDestroy(BaseActionTool):
    """
    破坏目标的Action.
        例如: 采矿, 砍树
    """
    def __init__(self, config):
        BaseActionTool.__init__(self, config)

