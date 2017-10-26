# encoding: utf8


"""

实现目标:
1. 单个frame内update尽可能少的node
2. bt需要支持对事件的随时响应. 没有事件时按照bt结构执行.

states  当前状态列表
bt nodes  状态树及其节点列表
current_node  当前正在执行的node

on_hero_approach
on_attacked



简单的决策:

loop
    decision
        loop action util done
            yield
event
    if current_action.can_disturb( event )
        return next action

BT相当于把决策需要的一系列状态表示为树状结构了.


逻辑节点类型:
composite:
    sequence
    random
    parallel
    util_success
    util_failure
decorator:
leaf:
    idle
    walk_to
    run
    bark
    chase
    attack


实现目标:
让AI可配置. AI以JSON形式存在, node由代码预先注册, JSON可以引用.
未定义的AI行为需要自行注册node.
如何处理事件?
    事件作为一个Node. 事件来时修改Context, 等待Node去检查.
    每个action有优先级, event也有优先级. 来了event,比较和当前action的优先级. 貌似不太好定义优先级.
如何结合动画标注事件?
    node.wait_for_event( event_name )  等待事件发生的时候, 继续该node的执行.
如何处理parallel?
    Action处理完cb之后, 如果running, 则加入direct_nodes中.
    暂时不处理这种情况.



实现:
BT每次都需要从跟节点来遍历. 可以保存当前node来进行优化, 但是必须考虑保证事件被及时处理.






"""

