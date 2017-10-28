## ChunkManager设计


### 移动物体的处理

如果object移动出了chunk，并且移到的chunk已经unload了，则进入freeze_list，依然属于该chunk。
freeze_list每一帧都会被遍历，以便重新定位object到正确的chunk。
freeze_list中的object不会被刷新。

### 更新

每次都会距离中心点最近的topN个chunk

### callbacks

1. generator 地图生成器
2. spawner 物体生成器
3. storage_mgr 存储管理器

各种回调的要求，详见代码注释

