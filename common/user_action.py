# encoding: utf8

__author__ = 'Leon'

"""
定义玩家Action和Object的交互逻辑
1. 点击物体后的行为
    1. 无响应
    2. 可以响应
        1. 原地做出动作
        2. 走过去，并作出动作

三要素：
1. 玩家工具：hand axe pickaxe
2. 玩家行为：左击还是右击
2. 目标entity的组件

entity component:
1. allow_action(self, tool_component, key_type)
2. do_action(self, tool_component, key_type)

每个函数都拥有完备的三要素信息，所以可以完整判断接下来的行为。

匹配规则:
tool
	action_type => duration
component
	action_type => efficiency
key_type
	left
	right

依次遍历所有component，调用allow_action，并返回所有响应的 
	component，action_type，key_type, inspect_info
	（此时可以强制检查 key_type 没有冲突）
	这个规则可以做成通用的
执行action的时候，再检查一遍
	每个action执行的具体内容，可以重载
"""
