# encoding: utf8

# 房间列表.每个房间放到固定大小的cell中进行缩放,房间保证从起点可达.

import random
import util
import grid
import sys


class Room:
    def __init__(self, r, c):
        self.r, self.c = r, c
        self.size = round(random.random() * 0.5 + 0.5, 3)
        self.reachable = False  # 是否和起点连接起来了
        self.is_start_room = False  # 是否是起始room
        self.around_rooms = []  # 周围的room列表
        self.connected_rooms = set()  # 直接相连的房间列表
        self.cluster_id = -1  # 直接相连的room拥有相同的id
        self.dist = -1  # 距离起始房间的距离(起始房间距离自己为0,旁边的房间为1,依次类推)

    def __str__(self):
        return 'Room[%s,%s]' % (self.r, self.c)


def set_cluster_id(room, cid):
    room.cluster_id = cid
    for croom in room.connected_rooms:
        if croom.cluster_id < 0:
            set_cluster_id(croom, cid)


# 距离起始房间的距离
def calc_dist(start_room):
    for room in start_room.connected_rooms:
        if room.dist < 0:
            room.dist = start_room.dist + 1
            calc_dist(room)


# 返回Room二维列表
def get_rooms(size1, size2, seed, ratio=1):
    random.seed(seed)

    # 随机生成房间
    rooms = []
    for idx1 in range(size1):
        line_rooms = []
        for idx2 in range(size2):
            if random.random() < ratio:
                room = Room(idx1, idx2)
                line_rooms.append(room)
            else:
                line_rooms.append(None)
        rooms.append(line_rooms)

    # 将周围的房间加入列表中
    def add_around(room, idx1, idx2):
        if 0 <= idx1 < size1 and 0 <= idx2 < size2:
            around_room = rooms[idx1][idx2]
            if around_room:
                room.around_rooms.append(around_room)
    for idx1 in range(size1):
        for idx2 in range(size2):
            room = rooms[idx1][idx2]
            if room is None:
                continue
            add_around(room, idx1 - 1, idx2)
            add_around(room, idx1 + 1, idx2)
            add_around(room, idx1, idx2 - 1)
            add_around(room, idx1, idx2 + 1)

    # 确定起点
    for i in range(size1*size2):
        start1, start2 = random.randint(0, size1-1), random.randint(0, size2-1)
        start_room = rooms[start1][start2]
        if start_room is None:
            continue
        start_room.is_start_room = True
        break
    else:
        raise RuntimeError("no start room can be found")

    # 将房间随机两两相连
    for i in range(size1*size2):
        idx1, idx2 = random.randint(0, size1 - 1), random.randint(0, size2 - 1)
        room = rooms[idx1][idx2]
        if room is None:
            continue
        # 随机选择当前房间旁边的一个房间
        if len(room.around_rooms) == 0:
            continue
        for i in range(8):
            around_room = random.choice(room.around_rooms)
            if len(around_room.connected_rooms) >= 2:
                continue
            if random.random() > 0.3:
                continue
            around_room.connected_rooms.add(room)
            room.connected_rooms.add(around_room)
            if len(room.connected_rooms) >= 2:
                break

    # 给所有房间进行编号,相连的设置为同一个cluster_id
    cluster_id = 0
    for idx1 in range(size1):
        for idx2 in range(size2):
            room = rooms[idx1][idx2]
            if room is None:
                continue
            if room.cluster_id < 0:
                cluster_id += 1
                set_cluster_id(room, cluster_id)

    # 展示cluster结果
    if False:
        print 'cluster map:'
        for idx1 in range(size1):
            ids = []
            for idx2 in range(size2):
                room = rooms[idx1][idx2]
                if room is None:
                    ids.append('.')
                    continue
                ids.append(str(room.cluster_id))
            print ' '.join(ids)

    # 计算每个cluster旁边的房间列表
    cluster2rooms = {}
    for idx1 in range(size1):
        for idx2 in range(size2):
            room = rooms[idx1][idx2]
            if room is None:
                continue
            for aroom in room.around_rooms:
                if aroom.cluster_id != room.cluster_id:
                    if aroom.cluster_id not in cluster2rooms:
                        cluster2rooms[aroom.cluster_id] = []
                    cluster2rooms[aroom.cluster_id].append((aroom, room))
                    if room.cluster_id not in cluster2rooms:
                        cluster2rooms[room.cluster_id] = []
                    cluster2rooms[room.cluster_id].append((room, aroom))

    # 从起始房间开始,将cluster都连接起来
    start_cluster_id = start_room.cluster_id
    reachable_cluster_ids = set()
    reachable_cluster_ids.add(start_cluster_id)
    keys = cluster2rooms.keys()
    random.shuffle(keys)
    for i in range(1000):
        for cluster_id in keys:
            if cluster_id not in reachable_cluster_ids:
                continue
            for pair in cluster2rooms[cluster_id]:
                reachable_room = pair[0]
                blocked_room = pair[1]
                if blocked_room.cluster_id in reachable_cluster_ids:
                    continue
                blocked_room.connected_rooms.add(reachable_room)
                reachable_room.connected_rooms.add(blocked_room)
                reachable_cluster_ids.add(blocked_room.cluster_id)
        if len(keys) == len(reachable_cluster_ids):
            break

    for cluster_id in keys:
        if cluster_id not in reachable_cluster_ids:
            print 'non-reachable cluster:', cluster_id

    # Flood 计算每个房间距离起始房间的距离
    start_room.dist = 0
    calc_dist(start_room)

    # 展示距离计算结果
    if False:
        print 'dist map:'
        for idx1 in range(size1):
            ids = []
            for idx2 in range(size2):
                room = rooms[idx1][idx2]
                if room is None:
                    ids.append('.')
                    continue
                ids.append(str(room.dist))
            print ' '.join(ids)

    return rooms, start_room


class RoomsGenerator(object):
    def __init__(self):
        self.rooms = None
        self.cells = None
        self.start_room = None
        self.size = 5

    def generate(self):
        random.seed(0)
        size = self.size
        self.rooms, self.start_room = get_rooms(size, size, 1, 0.99)
        self.generate_simple_cells()
        self.generate_cells()

    def generate_simple_cells(self):
        self.cells = []
        size = self.size
        for i in range(size*2):
            self.cells.append([' '] * (size*2))
        for i in range(size):
            for j in range(size):
                room = self.rooms[i][j]
                if room is None:
                    continue
                for croom in room.connected_rooms:
                    dx, dy = croom.r - room.r, croom.c - room.c
                    self.cells[i*2+dx][j*2+dy] = '+'
                self.cells[i*2][j*2] = '@' if room.is_start_room else 'O'
        if False:
            for i in range(len(self.cells)):
                for j in range(len(self.cells[0])):
                    data = self.cells[i][j]
                    sys.stdout.write('%s ' % data)
                sys.stdout.write('\n')

    def generate_cells(self):
        room_max_size = 7
        part_size = room_max_size + 2
        self.cells = grid.Grid(self.size * part_size, self.size * part_size)

        # 填充房间
        for i in range(self.size):
            for j in range(self.size):
                room = self.rooms[i][j]
                if room is None:
                    continue
                start_x = i * part_size
                start_y = j * part_size
                room_size1 = random.randint(part_size / 2, room_max_size)
                room_size2 = random.randint(part_size / 2, room_max_size)
                room_x = random.randint(1, (room_max_size - room_size1) / 2 + 1)
                room_y = random.randint(1, (room_max_size - room_size2) / 2 + 1)
                self.cells.set_all(start_x + room_x, start_y + room_y, room_size1, room_size2, 'x')

        if False:
            for i in range(self.cells.rows()):
                for j in range(self.cells.cols()):
                    data = self.cells.get(i, j)
                    if not data:
                        sys.stdout.write('[ ]')
                        continue
                    sys.stdout.write('[%s]' % data)
                sys.stdout.write('\n')
            print

        # 连接房间
        for i in range(self.size):
            for j in range(self.size):
                room = self.rooms[i][j]
                if room is None:
                    continue
                for croom in room.connected_rooms:
                    dx, dy = croom.r - room.r, croom.c - room.c  # delta_x
                    cx, cy = i * part_size + part_size / 2, j * part_size + part_size / 2  # center_x
                    ex, ey = cx + dx * part_size, cy + dy * part_size  # end_x
                    self.cells.fill_rect(cx, cy, ex, ey, '#')

        if False:
            for i in range(self.cells.rows()):
                for j in range(self.cells.cols()):
                    data = self.cells.get(i, j)
                    if not data:
                        sys.stdout.write('[ ]')
                        continue
                    sys.stdout.write('[%s]' % data)
                sys.stdout.write('\n')
            return

    def get(self, r, c):
        if r < 0 or r >= self.cells.rows() or c < 0 or c >= self.cells.cols():
            return 'empty'
        return self.cells.get(r, c)

    def get_start_pos(self):
        return self.start_room.r, self.start_room.c

generator = RoomsGenerator

if __name__ == '__main__':
    RoomsGenerator().generate()


