游戏流程
===


## Global

* G.physics_world		创建物理世界的单例，为创建entity做准备
* G.triggers


## Game

* G.camera_mgr
* G.state_mgr
	* load()
* G.spawner
* G.config_mgr			`注意，这个是管理数据配置的，而不是玩家settings。settings在storage_mgr中`
* g.resource_manager    `游戏全局资源`
* G.gui_mgr
* G.storage_mgr
* G.operation
* G.context			`全局的一些临时信息`


## States.MainMenu

* G.gui_mgr.DO(创建菜单)



## States.Game

* G.game_mgr


## Game Manager

* craft_mgr
	* load_craft_info( current_slot_storage )
* chunk_mgr
	on_load() or on_create
	load_hyper_entities()		从slot载入上一个地图的物品




## Other

* inventory，作为当前正在被控制的entity所携带的背包，作为一个component挂到某个entity上面。
* 驾驶时，载具拥有一个DriverSlot组件，用来记录驾驶相关信息，并用来保存主角。


	

	


