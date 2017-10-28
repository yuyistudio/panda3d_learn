# encoding: utf8

__author__ = 'Leon'

"""
定义玩家Action和Object的交互逻辑
1. 点击物体后的行为
    1. 无响应
    2. 可以响应
        1. 原地做出动作
        2. 走过去，并作出动作

决定因素：
1. 玩家工具：hand axe pickaxe
2. 玩家行为：左击还是右击
2. 目标entity的组件
    1. 每个组件注册自己对于左击和右击的响应，并定义快速Action映射到左击还是右击
    2. entity保证组件的响应不会冲突
    3. 组件的回调：
        1. allow_action( tool_component, action_type )
            1. 返回行为类型，或者None/False表示不允许动作
            2. 行为类型为 pickup cut 等
        2. do_action( tool_component, action_type )
"""
