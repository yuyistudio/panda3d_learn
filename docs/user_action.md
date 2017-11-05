定义玩家Action和Object的交互逻辑
======================

1. 点击物体后的行为
    1. 无响应
    2. 可以响应
        1. 原地做出动作
        2. 走过去，并作出动作

四要素

1. 玩家工具：hand axe pickaxe
2. 玩家行为：左击还是右击
3. 目标entity的组件
4. 鼠标entity

entity component

1. allow_action(self, tool_component, key_type, mouse_entity)
	1. 返回结果为False表示不进行动作
	2. 返回dict为如下格式：
	    1. action_type： component自己可以识别就行了
	    2. anim_name：必须是主角支持的动画名次
	    3. target_entity entity
	    4. key
	    5. ctrl 是不是按下了ctrl
	    6. min_dist 用于hero和target_entity的距离判定
	    7. event_name 当anim_name的event_name事件发生时，调用 do_action()
2. do_action(self, tool_component, key_type, mouse_entity)

每个函数都拥有完备的信息，所以可以完整判断接下来的行为。

匹配规则:
1. tool
	1. action_type => duration
1. component
	1. action_type => efficiency
1. key_type
	1. left
	2. right

1. 依次遍历所有component，调用allow_action，并返回所有响应的
	1. component，action_type，key_type, inspect_info （此时可以强制检查 key_type 没有冲突）
	2. 这个规则可以做成通用的
1. 执行action的时候，再检查一遍
	1. 每个action执行的具体内容，可以重载
