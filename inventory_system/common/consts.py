#encoding: utf8

# 将一个物体放入某个cell,有三种结果
PUT_MERGE_TOTALLY = 0  # 同类物品,完全放入
PUT_MERGE_PARTIALLY = 1  # 同类物品,放入部分
PUT_MERGE_FAILED = 2  # 同类已满
PUT_FORBIDDEN = 3  # 不允许放入该位置
PUT_SWITCH = 4  # 不同类的物品,交换成功
PUT_INTO_EMPTY = 5  # 成功放入了一个空的cell
PUT_SWITCH_FORBIDDEN = 6  # 不同的或者相同但是不可堆叠的物体, 同时不允许switch

BAG_PUT_TOTALLY = 0
BAG_PUT_PARTIALLY = 1
BAG_PUT_FAILED = 2
