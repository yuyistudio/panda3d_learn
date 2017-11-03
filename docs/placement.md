问题描述
===

place指的是，将item变成地面上的object的过程。需要进行碰撞检测，和预览作用的渲染。如何实现？


解决方案
===

1. 实现place，本质上只需要view和ghost collider即可
1. 在mouse获得item时触发，检测item的placeable组件
1. placeable组件支持 get_place_models() 和 get_place_colliders()
	1. 可以固定的从ObjModel和ObjAnimator组件中获取，不用做的太通用
1. operation中，根据placeable中获取的信息，进行如下操作
	1. 获取到的model使用半透明的material
	2. colliders是primitive shape的列表，添加到ghost body中去，进行碰撞检测





