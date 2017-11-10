## panda3d的坑

* ode不支持trigger，所以要结合collision，每个物体要两个collider
* collision不支持box到box的碰撞检测（最新的dev版才支持）
* animation_node. play() 即使传入的是一个不存在的动画，也不会报错，而是默默的啥都不做
* 内存管理 Removing_Custom_Class_Instances
	* 一般的NodePath
		* node_path.detatchNode() # 取消层级关系
		* node_path.removeNode() # 会销毁子物体
	* GUI
		* direct_gui_object.destroy() # 会销毁子物体
	* Actor
		* delete()
	* 3D sound
		* removeNode之前必须显式detatch
	* Task
		* 必须显式删除注册的任务，否则 taskMgr 会持有一份classInstance的引用
		* DirectObject的子类必须调用 ignoreAll()
		* 使用 custom class 的 __del__ 方法来检测是否正确回收了内存。


如何解决模型seam问题
============

1. 不是vertex未重合导致的。。
2. pixel texture可能采样到附近未定义的像素上去了，所以增大texture可以缓解问题
3. 设置texture wrap mode
4. 设置texture filter type
5. 使用anti-alias和fxaa

