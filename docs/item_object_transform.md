问题描述
===

item和object在转换的过程中,有些数据是共享的,比如火把的剩余燃料. 此时item和object要不要视为两个entity呢？


解决方案
===


1. 三种方案吧:
	1. 不统一，分开存，存在数据同步问题
	2. 不统一，共享部分com，需要定义哪些com需要共享
	3. 统一，需要加各种回调函数.
2. 最终决定用第三种方案.
	1. 主要是考虑统一性。entity其实就是data加上renderer，item和object只是renderer的不同而已。
	1. create_entity()的时候，需要指定entity的状态了.

1. 共享的方式实现，有如下状态
	1. ground item: 特殊实现，不放入chunk_manager，一定时间后自动消失
	2. inventory item:  使用on_item_update进行更新
	3. object: 使用on_update进行更新
2. entity记录当前状态 STATUS_ITEM STATUS_OBJECT STATUS_GROUND_ITEM
4. 每个component指定自己的类型，ITEM_ONLY, OBJECT_ONLY, or BOTH_ITEM_OBJECT
	1. 刚创建object的时候，ITEM_ONLY的com不会被添加
	2. ITEM_ONLY的com会在变成item的时候被自动添加
	3. BOTH_ITEM_OBJECT的com会在变成item的时候被调用 on_become_item()
	4. OBJECT_ONLY的com会在变成item的时候被销毁
	5. 创建object的时候,overwrite一些ITEM_ONLY的com属性是无效的
	6. 上述几点对于新建item的时候是一样的.
2. 对于BOTH类型的com，place的时候，调用on_become_object()回调；pickup的时候，调用on_become_item()回调

